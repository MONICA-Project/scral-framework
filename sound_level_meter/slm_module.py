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
import threading
import time
from datetime import timedelta

import arrow
import requests
import json
import logging
from flask import Flask

from scral_ogc import OGCDatastream
from scral_module.constants import REST_HEADERS
from scral_module import util
from scral_module.scral_module import SCRALModule

from sound_level_meter.constants import URL_SLM_LOGIN, CREDENTIALS, UPDATE_INTERVAL, URL_SLM_CLOUD, TENANT_ID, SITE_ID


app = Flask(__name__)
_slm_module = None


class SCRALSoundLevelMeter(SCRALModule):
    """ Resource manager for integration of the SLM-GW (by usage of B&K's IoT Sound Level Meters). """

    def __init__(self, ogc_config, connection_file, pub_topic_prefix):
        """ Load OGC configuration model and initialize MQTT Broker for publishing Observations

        :param connection_file: A file containing connection information.
        :param pub_topic_prefix: The MQTT topic prefix on which information will be published.
        """
        super().__init__(ogc_config, connection_file, pub_topic_prefix)

        # Creating endpoint for listening to "sound event detection" REST requests
        connection_config_file = util.load_from_file(connection_file)
        self._listening_address = connection_config_file["REST"]["listening_address"]["address"]
        self._listening_port = int(connection_config_file["REST"]["listening_address"]["port"])

        self._sequences = []
        self._active_devices = {}

        # Get cloud access token by using available credentials
        self._cloud_token = util.get_server_access_token(URL_SLM_LOGIN, CREDENTIALS,
                                                         REST_HEADERS, token_prefix="Bearer ")

        global _slm_module
        _slm_module = self

    def get_active_devices(self):
        return self._active_devices

    @property
    def get_cloud_token(self):
        return self._cloud_token

    # noinspection PyMethodOverriding
    def runtime(self):
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
        self.start_thread_pool()

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

        # Collect OGC information needed to build Datastreams payload
        thing = self._ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor = self._ogc_config.get_sensors()[0]  # Assumption: only "SLM" Sensor is defined for this adapter
        sensor_id = sensor.get_id()
        sensor_name = sensor.get_name()

        properties_list = self._ogc_config.get_observed_properties()  # There are more than one properties to parse

        # Start OGC Datastreams registration
        logging.info("--- Start OGC DATASTREAMs registration ---")
        # Iterate over active devices
        for device_id, values in self._active_devices.items():
            device_name = values["name"]
            device_coordinates = values["coordinates"]
            device_description = values["description"]

            # Check whether device has been already registered
            if device_name in self._resource_catalog:
                logging.debug("Device: "+device_id+" already registered with id: "+device_id+" and name: "+device_name)
            else:
                self._resource_catalog[device_name] = {}

                # Iterate over ObservedProperties
                for ogc_property in properties_list:
                    property_id = ogc_property.get_id()
                    property_name = ogc_property.get_name()
                    property_definition = {"definition": ogc_property.get_definition()}
                    datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + device_name
                    description = device_description
                    datastream = OGCDatastream(name=datastream_name, description=description,
                                               ogc_property_id=property_id, ogc_sensor_id=sensor_id,
                                               ogc_thing_id=thing_id, x=device_coordinates[0], y=device_coordinates[1],
                                               unit_of_measurement=property_definition)
                    datastream_id = self._ogc_config.entity_discovery(
                                        datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)

                    datastream.set_id(datastream_id)
                    self._ogc_config.add_datastream(datastream)

                    # Store device/property information in local resource catalog
                    self._resource_catalog[device_name][property_name] = datastream_id

                    logging.debug("Added Datastream: " + str(datastream_id) + " to the resource catalog for device: "
                                  + device_name + " and property: " + property_name)

    def start_thread_pool(self):
        thread_pool = []
        thread_id = 1

        for device_id, values in self._active_devices.items():
            thread = self.SLMThread(thread_id, "Thread-" + str(thread_id), values["name"], values["location_sequences"])
            thread.start()
            thread_pool.append(thread)
            thread_id += 1

        for thread in thread_pool:
            thread.join()

        logging.error("Exiting Main Thread")

    class SLMThread(threading.Thread):
        def __init__(self, thread_id, thread_name, device_name, url_sequences):
            super().__init__()

            self._thread_name = thread_name
            self._thread_id = thread_id
            self._device_name = device_name
            self._url_sequences = url_sequences

        def run(self):
            logging.debug("Starting Thread: " + self._thread_name)
            self._fetch_sequences()
            logging.debug("Exiting " + self._thread_name)

        def _fetch_sequences(self):
            r = None
            try:
                r = requests.get(self._url_sequences, headers=_slm_module.get_cloud_token)
            except Exception as ex:
                logging.error(ex)
            if not r or not r.ok:
                raise ConnectionError("Connection status: " + str(r.status_code) +
                                      "\nImpossible to establish a connection with " + self._url_sequences)

            # Set time-window size in order to define the number of values you retrieve for each request (in UTC)
            utc_ts_end = arrow.utcnow()
            utc_ts_start = utc_ts_end - timedelta(seconds=UPDATE_INTERVAL)

            # prepare format for URL
            query_ts_end = util.from_utc_to_query(utc_ts_end)
            query_ts_start = util.from_utc_to_query(utc_ts_start)
            time_token = '?startTime=' + query_ts_start + '&endTime=' + query_ts_end

            sequences_data = []
            for sequence in r.json()['value']:
                logging.debug(self._thread_name + " sequence:\n" + str(json.dumps(sequence)))
                prefix = self._url_sequences+"/"+sequence["sequenceId"]+"/data"

                sequence_name = sequence["name"]
                data = {"valueType": sequence_name, "time": time_token}
                if sequence_name == "LAeq" or sequence_name == "LCeq":
                    data["url_prefix"] = prefix + "/single"
                elif sequence_name == "CPBLZeq":
                    data["url_prefix"] = prefix + "/array"
                else:
                    logging.debug(sequence_name+" not yet integrated!")
                    continue

                sequences_data.append(data)

            logging.debug("Initial values: "+query_ts_start+" --- "+query_ts_end)

            while True:
                for seq in sequences_data:
                    url = seq["url_prefix"] + seq["time"]
                    r = requests.get(url, headers=_slm_module.get_cloud_token)
                    payload = r.json()['value']
                    logging.debug("Sequence: " + seq["valueType"]+"\n"+json.dumps(payload) + "\n")
                    break

                time.sleep(UPDATE_INTERVAL)

                # UPDATE INTERVALS
                query_ts_start = query_ts_end
                query_ts_end = util.from_utc_to_query(arrow.utcnow())
                time_token = '?startTime=' + query_ts_start + '&endTime=' + query_ts_end
                logging.debug("Updated values: " + query_ts_start + " --- " + query_ts_end)
                for seq in sequences_data:
                    seq["time"] = time_token
