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

import arrow
import requests
import json
import logging
from flask import Flask

from scral_ogc import OGCDatastream, OGCObservation
from scral_module.constants import REST_HEADERS
from scral_module import util
from scral_module.rest_module import SCRALRestModule

from sound_level_meter.constants import UPDATE_INTERVAL, URL_SLM_CLOUD, TENANT_ID, SITE_ID

app = Flask(__name__)


class SCRALSoundLevelMeter(SCRALRestModule):
    """ Resource manager for integration of the SLM-GW (by usage of B&K's IoT Sound Level Meters). """

    def __init__(self, ogc_config, connection_file, pub_topic_prefix,
                 url_login, credentials, token_prefix="", token_suffix=""):
        """ Load OGC configuration model and initialize MQTT Broker for publishing Observations

        :param connection_file: A file containing connection information.
        :param pub_topic_prefix: The MQTT topic prefix on which information will be published.
        """
        super().__init__(ogc_config, connection_file, pub_topic_prefix)

        self._sequences = []
        self._active_devices = {}

        self._publish_mutex = Lock()

        self._url_login = url_login
        self._credential = credentials
        self._token_prefix = token_prefix
        self._token_suffix = token_suffix
        self._cloud_token = ""
        self.update_cloud_token()

    def get_cloud_token(self):
        return self._cloud_token

    def get_mutex(self):
        return self._publish_mutex

    def update_cloud_token(self):
        """ Updates the cloud access token by using available credentials """
        self._cloud_token = util.get_server_access_token(self._url_login, self._credential, REST_HEADERS,
                                                         self._token_prefix, self._token_suffix)

    # noinspection PyMethodOverriding
    def runtime(self, flask_instance):
        """
        This method discovers active SLMs from B&K cloud, registers them as OGC Datastreams into the MONICA
        cloud and finally retrieves sound measurements for each device by using parallel querying threads.

        Furthermore, this method deploys an REST endpoint as Flask application based on CherryPy WSGI web server.
        The endpoint will listen for incoming REST requests of the type "sound event detection",
        and will generate corresponding Observations.
        """
        # Start SLM discovery and Datastream registration
        self.ogc_datastream_registration(URL_SLM_CLOUD, TENANT_ID, SITE_ID)

        # Start thread pool for Observations
        self._start_thread_pool()

        # starting REST web server
        super().runtime(flask_instance)

    def ogc_datastream_registration(self, url, tenant_id, site_id):
        """
        This method discovers active SLMs for a given site_id and registers a new OGC Datastream for
        each couple SLM-ObservedProperty.
        :param url: server address
        :param tenant_id: server tenant_id
        :param site_id: server site_id (pilot specific)
        """

        url_locations = url + "/tenants/" + str(tenant_id) + "/sites/" + str(site_id) + "/locations"

        # Get the list of active locations registered to the site_id
        r = None
        try:
            r = requests.get(url_locations, headers=self._cloud_token)
        except Exception as ex:
            logging.error(ex)

        if not r or not r.ok:
            raise ConnectionError(
                "Connection status: " + str(r.status_code) + "\nImpossible to establish a connection with " + url)
        else:
            locations_list = r.json()['value']
            logging.debug("Active locations list: " + str(locations_list))

        # Get location ids from active locations
        locations_id_list = []
        for location in locations_list:
            locations_id_list.append(location["locationId"])

        # Discover active devices from active location ids (assumption: 1 SLM x 1 location_id)
        for location_id in locations_id_list:
            logging.info("Start discovery for active SLMs in a given site (pilot)")
            url_loc = url_locations + "/" + str(location_id)
            try:
                r = requests.get(url_loc, headers=self._cloud_token)
            except Exception as ex:
                logging.error(ex)

            # Get device id, name, description and coordinates information stored in location item
            location_item = r.json()
            device_id = location_item["assignedDevices"][0]["deviceId"]
            device_name = location_item["assignedDevices"][0]["name"]
            device_description = location_item["assignedDevices"][0]["description"]
            location_coordinates = location_item["geoLocation"]
            logging.debug("SLM id: "+str(device_id)+" / SLM name: "+device_name)

            # Build active devices catalog
            self._active_devices[device_id] = {}
            self._active_devices[device_id]["coordinates"] = location_coordinates["coordinates"]
            self._active_devices[device_id]["name"] = device_name
            self._active_devices[device_id]["description"] = device_description

            url_sequences = url + "/tenants/" + str(tenant_id) + "/sites/" + str(site_id) + "/locations/" + str(
                location_id) + "/sequences"
            self._active_devices[device_id]["location_sequences"] = url_sequences

        # Start OGC Datastreams registration
        logging.info("\n\n--- Start OGC DATASTREAMs registration ---\n")

        # Iterate over active devices
        for device_id, values in self._active_devices.items():
            device_name = values["name"]
            device_coordinates = values["coordinates"]
            device_description = values["description"]

            # Check whether device has been already registered
            if device_id in self._resource_catalog:
                logging.debug("Device: "+device_name+" already registered with id: "+device_id)
            else:
                self._resource_catalog[device_id] = {}
                # Iterate over ObservedProperties
                for ogc_property in self._ogc_config.get_observed_properties():
                    self._new_datastream(ogc_property, device_id, device_name, device_coordinates, device_description)

        logging.info("--- End of OGC DATASTREAMs registration ---\n")

    def new_datastream(self, ogc_obs_property, device_id):
        """ """
        obs_prop = self._ogc_config.add_observed_property(ogc_obs_property)
        device_coordinates = self._active_devices[device_id]["coordinates"]
        device_name = self._active_devices[device_id]["name"]
        device_description = self._active_devices[device_id]["description"]

        datastream_id = self._new_datastream(obs_prop, device_id, device_name, device_coordinates, device_description)
        return datastream_id

    def _new_datastream(self, ogc_property, device_id, device_name, device_coordinates, device_description):
        """ """
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

        # for the future debuggare: maybe could be better to use device_id
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

        return datastream_id

    def _start_thread_pool(self, locking=False):
        thread_pool = []
        thread_id = 1

        for device_id, values in self._active_devices.items():
            thread = SCRALSoundLevelMeter.SLMThread(
                thread_id, "Thread-" + str(thread_id), device_id, values["location_sequences"], self)
            thread.start()
            thread_pool.append(thread)
            thread_id += 1

        logging.info("Threads detached")
        if locking:
            for thread in thread_pool:
                thread.join()
            logging.error("All threads have been interrupted!")

    class SLMThread(Thread):
        def __init__(self, thread_id, thread_name, device_id, url_sequences, slm_module):
            super().__init__()

            self._thread_name = thread_name
            self._thread_id = thread_id
            self._device_id = device_id
            self._url_sequences = url_sequences
            self._slm_module = slm_module

        def run(self):
            logging.debug("Starting Thread: " + self._thread_name)
            self._fetch_sequences()
            logging.debug("Exiting " + self._thread_name)

        def _fetch_sequences(self):
            r = None
            try:
                r = requests.get(self._url_sequences, headers=self._slm_module.get_cloud_token())
            except Exception as ex:
                logging.error(ex)
            if not r or not r.ok:
                raise ConnectionError("Connection status: " + str(r.status_code) +
                                      "\nImpossible to establish a connection with " + self._url_sequences)

            # ### LAeq values averaged on 5 minutes ###
            min5_in_seconds = 300  # this is the timer, new query triggered each 5 min (300 sec)
            time_elapsed = 0       # counter for current time passed by
            start_timer = time.time()

            utc_now = arrow.utcnow()
            query_ts_end = util.from_utc_to_query(utc_now)
            time_token = build_time_token(utc_now, UPDATE_INTERVAL)

            sequences_data = []
            for sequence in r.json()['value']:
                logging.debug(self._thread_name + " sequence:\n" + str(json.dumps(sequence)))
                prefix = self._url_sequences+"/"+sequence["sequenceId"]+"/data"

                sequence_name = sequence["name"]
                data = {"valueType": sequence_name, "time": time_token}
                if sequence_name == "LAeq" or sequence_name == "LCeq":
                    data["url_prefix"] = prefix + "/single"
                elif sequence_name == "Avg5minLAeq":
                    data["url_prefix"] = prefix + "/single"

                    min10_ago_in_seconds = arrow.utcnow() - timedelta(seconds=600)
                    time_token = build_time_token(min10_ago_in_seconds, min5_in_seconds)
                    data["time"] = time_token
                elif sequence_name == "CPBLZeq":
                    data["url_prefix"] = prefix + "/array"
                else:
                    logging.debug(sequence_name+" not yet integrated!")
                    continue

                sequences_data.append(data)

            time_elapsed = 300  # to force to perform request the first time
            rc = self._slm_module.get_resource_catalog()
            logging.info("\n\n--- Start OGC OBSERVATIONs registration ---\n")
            while True:
                try:
                    for seq in sequences_data:
                        property_name = seq["valueType"]

                        if property_name == "Avg5minLAeq" and time_elapsed < min5_in_seconds:
                            continue  # not update data

                        url = seq["url_prefix"] + seq["time"]
                        r = requests.get(url, headers=self._slm_module.get_cloud_token())
                        payload = r.json()  # ['value']
                        logging.debug("Sequence: " + property_name+"\n"+json.dumps(payload))

                        if payload["value"] and len(payload["value"]) >= 1:  # is the payload not empty?
                            datastream_id = rc[self._device_id][property_name]
                            observation_result = {"valueType": property_name, "response": payload}
                            phenomenon_time = payload["value"][0]["startTime"]
                            self._slm_module.ogc_observation_registration(
                                datastream_id, phenomenon_time, observation_result)

                    time.sleep(UPDATE_INTERVAL)
                    logging.debug("\n")

                    # UPDATE INTERVALS
                    time_elapsed = time.time() - start_timer
                    query_ts_start = query_ts_end
                    query_ts_end = util.from_utc_to_query(arrow.utcnow())

                    for seq in sequences_data:
                        property_name = seq["valueType"]

                        if property_name == "Avg5minLAeq":
                            if time_elapsed >= min5_in_seconds:
                                time_elapsed = 0
                                start_timer = time.time()

                                min10_ago_in_seconds = arrow.utcnow() - timedelta(seconds=600)
                                seq["time"] = build_time_token(min10_ago_in_seconds, min5_in_seconds)
                        else:
                            seq["time"] = '?startTime=' + query_ts_start + '&endTime=' + query_ts_end

                except ValueError:
                    if r.status_code == 401:
                        logging.info("\nAuthentication Token expired!\n")
                        self._slm_module.update_cloud_token()

    def ogc_observation_registration(self, datastream_id, phenomenon_time, observation_result):
        # Preparing MQTT topic
        topic = self._topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # Preparing Payload
        observation = OGCObservation(datastream_id, phenomenon_time, observation_result, str(arrow.utcnow()))

        # Publishing
        self._publish_mutex.acquire()
        try:
            self.mqtt_publish(topic, json.dumps(observation.get_rest_payload()))
        finally:
            self._publish_mutex.release()


def build_time_token(utc_ts_end, update_interval):
    # Set time-window size in order to define the number of values you retrieve for each request (in UTC)
    utc_ts_start = utc_ts_end - timedelta(seconds=update_interval)

    # prepare format for URL
    query_ts_end = util.from_utc_to_query(utc_ts_end)
    query_ts_start = util.from_utc_to_query(utc_ts_start)

    time_token = '?startTime=' + query_ts_start + '&endTime=' + query_ts_end
    return time_token
