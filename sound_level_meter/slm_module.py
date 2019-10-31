#############################################################################
#      _____ __________  ___    __                                          #
#     / ___// ____/ __ \/   |  / /                                          #
#     \__ \/ /   / /_/ / /| | / /                                           #
#    ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Adaptation Layer  #
#   /____/\____/_/ |_/_/  |_/_____/   v.2.0 - enhanced by Python 3          #
#                                                                           #
# LINKS Foundation, (c) 2019                                                #
# developed by Jacopo Foglietti & Luca Mannella                             #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md     #
#                                                                           #
#############################################################################
import time
from threading import Thread, Lock
from datetime import timedelta
from typing import Optional, Dict, List

import arrow
import requests
import json
import logging

from arrow import Arrow
from flask import Flask, Response
from urllib3.exceptions import NewConnectionError, MaxRetryError

from scral_ogc import OGCDatastream, OGCObservedProperty

from scral_core.constants import REST_HEADERS, CATALOG_FILENAME, ENABLE_CHERRYPY, COORD
from scral_core import util
from scral_core.ogc_configuration import OGCConfiguration
from scral_core.rest_module import SCRALRestModule

from microphone.microphone_module import SCRALMicrophone
from microphone.constants import SEQUENCES_KEY

from sound_level_meter.constants import UPDATE_INTERVAL, URL_SLM_CLOUD, MIN5_IN_SECONDS, RETRY_INTERVAL, \
    DEVICE_NAME_KEY, CLOUD_KEY, SITE_NAME_KEY, TENANT_ID_KEY, SITE_ID_KEY, AD_NAME_KEY, AD_COORD_KEY, AD_DESCRIPTION_KEY


class SCRALSoundLevelMeter(SCRALRestModule, SCRALMicrophone):
    """ Resource manager for integration of the SLM-GW (by usage of B&K's IoT Sound Level Meters). """

    def __init__(self, ogc_config: OGCConfiguration, connection_file: str, pilot: str,
                 url_login: str, credentials, catalog_name: str = CATALOG_FILENAME,
                 token_prefix: Optional[str] = "", token_suffix: Optional[str] = ""):
        """ Load OGC configuration model and initialize MQTT Broker for publishing Observations

        :param connection_file: A file containing connection information.
        :param pilot: The MQTT topic prefix on which information will be published.
        """
        super().__init__(ogc_config, connection_file, pilot, catalog_name)

        self._publish_mutex = Lock()
        self._active_devices = {}

        self._sequences = []

        self._url_login = url_login
        self._credential = credentials
        self._token_prefix = token_prefix
        self._token_suffix = token_suffix
        self._cloud_token = ""
        self.update_cloud_token()

        connection_config_file = util.load_from_file(connection_file)
        self._site_name = connection_config_file[CLOUD_KEY][SITE_NAME_KEY]
        self._tenant_id = connection_config_file[CLOUD_KEY][TENANT_ID_KEY]
        self._site_id = connection_config_file[CLOUD_KEY][SITE_ID_KEY]

    def get_cloud_token(self) -> str:
        return self._cloud_token

    def get_mutex(self) -> Lock:
        return self._publish_mutex

    def update_cloud_token(self):
        """ Updates the cloud access token by using available credentials """
        self._cloud_token = util.get_server_access_token(self._url_login, self._credential, REST_HEADERS,
                                                         self._token_prefix, self._token_suffix)

    # noinspection PyMethodOverriding
    def runtime(self, flask_instance: Flask, mode: int = ENABLE_CHERRYPY):
        """
        This method discovers active SLMs from B&K cloud, registers them as OGC Datastreams into the MONICA
        cloud and finally retrieves sound measurements for each device by using parallel querying threads.

        Furthermore, this method deploys an REST endpoint as Flask application based on CherryPy WSGI web server.
        The endpoint will listen for incoming REST requests of the type "sound event detection",
        and will generate corresponding Observations.
        """
        # Start SLM discovery and Datastream registration
        try:
            self.ogc_datastream_registration(URL_SLM_CLOUD)
        except AttributeError as ae:
            logging.critical(ae)
            logging.info("Site name: " + self._site_name)
            logging.info("Tenant ID :" + self._tenant_id)
            logging.info("Site ID :" + self._site_id)
            return

        # Start thread pool for Observations
        self._start_thread_pool(SCRALSoundLevelMeter.SLMThread)

        # starting REST web server
        super().runtime(flask_instance, mode)

    def ogc_datastream_registration(self, url: str):
        """ This method receive a target URL as parameter and discovers active SLMs.
            A new OGC Datastream for each couple SLM-ObservedProperty is registered.

        :param url: Target server address.
        """

        url_locations = url + "/tenants/" + str(self._tenant_id) + "/sites/" + str(self._site_id) + "/locations"

        # Get the list of active locations registered to the site_id
        resp = None
        try:
            resp = requests.get(url_locations, headers=self._cloud_token)
        except Exception as ex:
            logging.error(ex)

        if not resp or not resp.ok:
            raise ConnectionError(
                "Connection status: " + str(resp.status_code) + "\nImpossible to establish a connection with " + url)

        logging.info("\n\n--- Active device discovery ---\n")
        locations_list = resp.json()['value']

        if len(locations_list) <= 0:
            raise AttributeError("Impossible to retrieve active devices.")

        # Discover active devices from active location ids (assumption: 1 SLM x 1 location_id)
        logging.debug("Active locations list:")
        for location in locations_list:
            logging.debug(location)
            location_id = location["locationId"]

            url_loc = url_locations + "/" + str(location_id)
            try:
                resp = requests.get(url_loc, headers=self._cloud_token)
            except Exception as ex:
                logging.error(ex)

            # Get device id, name, description and coordinates information stored in location item
            location_item = resp.json()
            device_id = location_item["assignedDevices"][0]["deviceId"]
            # device_name = location_item["assignedDevices"][0]["name"]  # sometimes is apparently wrong
            device_name = location_item["name"]
            device_description = location_item["assignedDevices"][0]["description"]
            location_coordinates = location_item["geoLocation"]
            logging.debug("SLM id: " + str(device_id) + " / SLM name: " + device_name)

            if not location_coordinates:
                logging.error("Location coordinates of device " + device_name + " are not defined.")
                location_coordinates = {"coordinates": [0.0, 0.0]}

            # Build active devices catalog
            self._active_devices[device_id] = {}
            self._active_devices[device_id][AD_NAME_KEY] = device_name
            self._active_devices[device_id][AD_DESCRIPTION_KEY] = device_description
            self._active_devices[device_id][AD_COORD_KEY] = location_coordinates[AD_COORD_KEY]

            url_sequences = url + "/tenants/" + str(self._tenant_id) + "/sites/" + str(
                self._site_id) + "/locations/" + str(location_id) + "/sequences"
            self._active_devices[device_id][SEQUENCES_KEY] = url_sequences
        logging.info("\n\n--- End of active device discovery. "
                     "There are "+str(len(self._active_devices))+" active devices. ---\n")

        # Start OGC Datastreams registration
        logging.info("\n\n--- Start OGC DATASTREAMs registration ---\n")

        # Iterate over active devices
        for device_id, values in self._active_devices.items():
            device_name = values["name"]
            device_coordinates = values["coordinates"]
            device_description = values["description"]

            # Check whether device has been already registered
            if device_id in self._resource_catalog:
                logging.debug("Device: " + device_name + " already registered with id: " + device_id)
            else:
                self._resource_catalog[device_id] = {}
                self._resource_catalog[device_id][DEVICE_NAME_KEY] = device_name
                # Iterate over ObservedProperties
                for ogc_property in self._ogc_config.get_observed_properties():
                    self._new_datastream(ogc_property, device_id, device_name, device_coordinates, device_description)

        self.update_file_catalog()
        logging.info("\n\n--- End of OGC DATASTREAMs registration. "
                     + str(len(self._ogc_config.get_datastreams()))+" datastreams were registered. ---\n")

    def new_datastream(self, device_id: str, ogc_obs_property: OGCObservedProperty):
        """ This method have to be called when you want to add a new DATASTREAM.

        :param device_id: The ID of the device for which you want to create the DATASTREAMs.
        :param ogc_obs_property: The OBSERVED PROPERTY for which you want to create the DATASTREAMs.
        :return: The datastream_id of the new generated DATASTREAM.
        """
        if device_id not in self._active_devices:
            logging.error("Device " + device_id + " is not active.")
            return False

        if ogc_obs_property not in self.get_ogc_config().get_observed_properties():
            ogc_obs_property = self._ogc_config.add_observed_property(ogc_obs_property)

        try:
            datastream_id = self._resource_catalog[device_id][ogc_obs_property.get_name()]
        except KeyError:
            device_coordinates = self._active_devices[device_id]["coordinates"]
            device_name = self._active_devices[device_id]["name"]
            device_description = self._active_devices[device_id]["description"]

            datastream_id = self._new_datastream(
                ogc_obs_property, device_id, device_name, device_coordinates, device_description)

        return datastream_id

    def _new_datastream(self, ogc_property: OGCObservedProperty, device_id: str, device_name: str,
                        device_coordinates: COORD, device_description: str) -> int:
        """ This method creates a new DATASTREAM. It is a private method, externally you should call "new_datastream".

        :param ogc_property: The OBSERVED PROPERTY.
        :param device_id: The physical device ID.
        :param device_name: A name associated to the device.
        :param device_coordinates: An array (or tuple) of coordinates
        :param device_description: A device description
        :return: The DATASTREAM ID of the new created device.
        """
        # Collect OGC information needed to build Datastreams payload
        thing = self._ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor = self._ogc_config.get_sensors()[0]  # Assumption: only "SLM" Sensor is defined for this adapter
        sensor_id = sensor.get_id()
        sensor_name = sensor.get_name()

        property_id = ogc_property.get_id()
        property_name = ogc_property.get_name()
        property_definition = {"definition": ogc_property.get_definition()}

        # for the future debugger: maybe could be better to use device_id
        datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + device_name
        datastream = OGCDatastream(name=datastream_name, description=device_description,
                                   ogc_property_id=property_id, ogc_sensor_id=sensor_id,
                                   ogc_thing_id=thing_id, x=device_coordinates[0], y=device_coordinates[1],
                                   unit_of_measurement=property_definition)
        datastream_id = self._ogc_config.entity_discovery(
            datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)

        datastream.set_id(datastream_id)
        self._ogc_config.add_datastream(datastream)

        # Store device/property information in local resource catalog
        if property_name not in self._resource_catalog[device_id].keys():
            self._resource_catalog[device_id][property_name] = datastream_id
            logging.debug("Added Datastream: " + str(datastream_id) + " to the resource catalog for device: "
                          + device_id + " and property: " + property_name)

        self.update_file_catalog()
        return datastream_id

    class SLMThread(Thread):
        """ Each instance of this class manage a different microphone. """

        def __init__(self, thread_id: int, thread_name: str, device_id: str, url_sequences: str,
                     slm_module: "SCRALSoundLevelMeter", print_on_file: bool = False):
            super().__init__()

            thread_debug_name = "("+thread_name+")"
            if not print_on_file:
                # Init Thread logger
                self._logger = util.init_mirrored_logger(thread_debug_name, logging.DEBUG)
            else:
                # Enable log storage in file
                self._logger = util.init_mirrored_logger(thread_debug_name, logging.DEBUG, "mic_"+str(thread_id)+".log")

            self._thread_name = thread_name
            self._thread_id = thread_id
            self._device_id = device_id
            self._url_sequences = url_sequences
            self._slm_module = slm_module

        def run(self):
            self._logger.info("Starting Thread: " + self._thread_name)

            resp = None
            try:
                resp = requests.get(self._url_sequences, headers=self._slm_module.get_cloud_token())
            except Exception as ex:
                self._logger.error(ex)
            if not resp or not resp.ok:
                raise ConnectionError("Connection status: " + str(resp.status_code) +
                                      "\nImpossible to establish a connection with " + self._url_sequences)

            sequences_data = self._init_sequences(resp)
            query_ts_end = util.from_utc_to_query(arrow.utcnow())

            # ### LAeq values averaged on 5 minutes ###
            start_timer_avg5min = time.time()
            start_timer_annoyance = time.time()

            # These variables should be initialized to 0. The following values are used to force first requests.
            time_elapsed_avg_laeq = MIN5_IN_SECONDS
            time_elapsed_annoyance = 60

            rc = self._slm_module.get_resource_catalog()
            self._logger.info("\n\n--- Start OGC OBSERVATIONs registration ---\n")
            while True:
                try:
                    for seq in sequences_data:
                        property_name = seq["valueType"]

                        if property_name == "Avg5minLAeq" and time_elapsed_avg_laeq < MIN5_IN_SECONDS:
                            continue  # not update data
                        if property_name == "Annoyance" and time_elapsed_annoyance < 60:
                            continue  # not update data

                        url = seq["url_prefix"] + seq["time"]
                        resp = requests.get(url, headers=self._slm_module.get_cloud_token())
                        if not resp or not resp.ok:
                            if resp.status_code == 401:
                                raise ValueError("Authentication token expired!")
                            else:
                                raise Exception("Something wrong retrieving data!")

                        payload = resp.json()  # ['value']

                        if payload["value"] and len(payload["value"]) >= 1:  # is the payload not empty?
                            self._logger.info("Sequence: " + property_name + "\n" + json.dumps(payload))

                            datastream_id = rc[self._device_id][property_name]
                            observation_result = {"valueType": property_name, "response": payload}
                            phenomenon_time = payload["value"][0]["startTime"]
                            self._slm_module.ogc_observation_registration(
                                datastream_id, phenomenon_time, observation_result)
                        else:
                            self._logger.error("Property: '"+property_name+"' has NULL payload!")
                            self._logger.info("Timestamp: " + seq["time"])

                    time.sleep(UPDATE_INTERVAL)  # ## # ### # #### # ##### # ######
                    self._logger.info("")        # ## # ### # #### # ##### # ######
                    self._logger.info("Time elapsed: " + str(int(time_elapsed_annoyance)))

                    # UPDATE INTERVALS
                    query_ts_start = query_ts_end
                    query_ts_end = util.from_utc_to_query(arrow.utcnow())

                    for seq in sequences_data:
                        property_name = seq["valueType"]

                        if property_name == "Avg5minLAeq":
                            if time_elapsed_avg_laeq >= MIN5_IN_SECONDS:  # updates only if time is elapsed
                                start_timer_avg5min = time.time()

                                min10_ago_in_seconds = arrow.utcnow() - timedelta(seconds=600)
                                seq["time"] = build_time_token(min10_ago_in_seconds, MIN5_IN_SECONDS)
                        elif property_name == "Annoyance":                # updates only if time is elapsed
                            if time_elapsed_annoyance >= 60:
                                start_timer_annoyance = time.time()

                                # min2_ago_in_seconds = arrow.utcnow() - timedelta(seconds=120)
                                min10_ago_in_seconds = arrow.utcnow() - timedelta(seconds=600)
                                seq["time"] = build_time_token(min10_ago_in_seconds, 60)
                        else:
                            seq["time"] = '?startTime=' + query_ts_start + '&endTime=' + query_ts_end

                    time_elapsed_avg_laeq = time.time() - start_timer_avg5min
                    time_elapsed_annoyance = time.time() - start_timer_annoyance
                    self._logger.info("Time elapsed: "+str(int(time_elapsed_annoyance))+"\n\n")

                except ValueError as ve:
                    if resp.status_code == 401:
                        self._logger.info("\nAuthentication Token expired!\n")
                        self._slm_module.update_cloud_token()
                    else:
                        self._logger.error("Unknown ValueError exception: " + str(ve))
                except Exception as ex:
                    if isinstance(ex, NewConnectionError):
                        self._logger.error("Connection error: " + str(ex))
                    elif isinstance(ex, MaxRetryError):
                        self._logger.error("Too many connection attempts: " + str(ex))
                    else:
                        self._logger.error(str(ex))

                    self._logger.info("Retrying after " + str(RETRY_INTERVAL) + " seconds.")
                    time.sleep(RETRY_INTERVAL)

        def _init_sequences(self, resp: Response) -> List[Dict[str, str]]:
            """ This method builds and initializes an array of data sequences using the result of an HTTP request.

            :param resp: The result of the http request.
            :return: An array of sequences properly initialized.
            """

            time_token = build_time_token(arrow.utcnow(), UPDATE_INTERVAL)

            sequences_data = []
            for sequence in resp.json()['value']:
                self._logger.info(self._thread_name + " sequence:\n" + str(json.dumps(sequence)))
                prefix = self._url_sequences + "/" + sequence["sequenceId"] + "/data"

                sequence_name = sequence["name"]
                data = {"valueType": sequence_name, "time": time_token}
                if sequence_name == "LAeq" or sequence_name == "LCeq":
                    data["url_prefix"] = prefix + "/single"
                elif sequence_name == "Annoyance":
                    data["url_prefix"] = prefix + "/single"

                    # min2_ago_in_seconds = arrow.utcnow() - timedelta(seconds=120)
                    # data["time"] = build_time_token(min2_ago_in_seconds, 60)

                    min10_ago_in_seconds = arrow.utcnow() - timedelta(seconds=600)
                    data["time"] = build_time_token(min10_ago_in_seconds, 60)
                elif sequence_name == "Avg5minLAeq":
                    data["url_prefix"] = prefix + "/single"

                    min10_ago_in_seconds = arrow.utcnow() - timedelta(seconds=600)
                    data["time"] = build_time_token(min10_ago_in_seconds, MIN5_IN_SECONDS)
                elif sequence_name == "CPBLZeq":
                    data["url_prefix"] = prefix + "/array"
                else:
                    self._logger.info(sequence_name + " not yet integrated!")
                    continue

                sequences_data.append(data)

            return sequences_data


def build_time_token(utc_ts_end: Arrow, update_interval: float) -> str:
    """ This function build a time_token according to HTTP request format.

    :param utc_ts_end: An arrow timestamp
    :param update_interval: An amount of second that you want to subtract from the "utc_ts_end"
    :return: A string like this: '?startTime=<start_time>&endTime=<end_time>'
    """
    # Set time-window size in order to define the number of values you retrieve for each request (in UTC)
    utc_ts_start = utc_ts_end - timedelta(seconds=update_interval)

    # prepare format for URL
    query_ts_end = util.from_utc_to_query(utc_ts_end)
    query_ts_start = util.from_utc_to_query(utc_ts_start)

    time_token = '?startTime=' + query_ts_start + '&endTime=' + query_ts_end
    return time_token
