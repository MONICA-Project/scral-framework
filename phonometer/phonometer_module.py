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

import arrow
import logging
from threading import Thread

import requests
from datetime import timedelta

from urllib3.exceptions import NewConnectionError, MaxRetryError

from scral_module import util
from scral_module.constants import REST_HEADERS
from scral_module.scral_module import SCRALModule
from scral_ogc import OGCDatastream

from microphone.microphone_module import SCRALMicrophone
from microphone.constants import SEQUENCES_KEY

from phonometer.constants import URL_TENANT, ACTIVE_DEVICES, FILTER_SDN_1, URL_CLOUD, UPDATE_INTERVAL, LAEQ_KEY, \
    SPECTRA_KEY, RETRY_INTERVAL, FREQ_INTERVALS, FILTER_SDN_2, FILTER_SDN_3


class SCRALPhonometer(SCRALModule, SCRALMicrophone):
    """ Resource manager for integration of Phonometers. """

    def runtime(self):
        """ This method discovers active Phonometers from SDN cloud, registers them as OGC Datastreams into the MONICA
            cloud and finally retrieves sound measurements for each device by using parallel querying threads.
        """
        # Start Phonometer discovery and Datastream registration
        self.ogc_datastream_registration(URL_TENANT)

        # Start thread pool for Observations
        self._start_thread_pool(SCRALPhonometer.PhonoThread)

    def ogc_datastream_registration(self, url):
        """ This method receives a target URL as parameter and discovers active Phonometers.
            A new OGC Datastream for each couple Phonometer-ObservedProperty is registered.

        :param url: Target server address.
        """
        r = None
        try:
            r = requests.get(url)
        except Exception as ex:
            logging.error(ex)

        if not r or not r.ok:
            raise ConnectionError(
                "Connection status: " + str(r.status_code) + "\nImpossible to establish a connection with " + url)

        # Start OGC Datastreams registration
        logging.info("\n\n--- Start OGC DATASTREAMs registration ---\n")
        phonometers = r.json()["metadata"]

        # Iterate over active devices
        for phono in phonometers:
            if phono["dataset"]["code"] in ACTIVE_DEVICES:
                device_id = phono["dataset"]["code"]
                device_name = phono["name"]
                device_coordinates = (phono["longitude"], phono["latitude"])
                device_description = phono["description"]

                # Check whether device has been already registered
                if device_id in self._resource_catalog:
                    logging.debug("Device: " + device_name + " already registered with id: " + device_id)
                else:
                    self._resource_catalog[device_id] = {}
                    # Iterate over ObservedProperties
                    for ogc_property in self._ogc_config.get_observed_properties():
                        self._new_datastream(
                            ogc_property, device_id, device_coordinates, device_description)

                url_sequence = URL_CLOUD + device_id + FILTER_SDN_1
                self._active_devices[device_id][SEQUENCES_KEY] = url_sequence

            logging.info("--- End of OGC DATASTREAMs registration ---\n")

    def _new_datastream(self, ogc_property, device_id, device_coordinates, device_description):
        """ This method creates a new DATASTREAM.

        :param ogc_property: The OBSERVED PROPERTY.
        :param device_id: The physical device ID.
        :param device_coordinates: An array (or tuple) of coordinates.
        :param device_description: A device description.
        :return: The DATASTREAM ID of the new created device.
        """
        # ToDo: upgradami
        # Collect OGC information needed to build Datastreams payload
        thing = self._ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor = self._ogc_config.get_sensors()[0]  # Assumption: only "Phonometer" Sensor is defined for this adapter.
        sensor_id = sensor.get_id()
        sensor_name = sensor.get_name()

        property_id = ogc_property.get_id()
        property_name = ogc_property.get_name()
        property_definition = {"definition": ogc_property.get_definition()}

        datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + device_id
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

    class PhonoThread(Thread):
        """ Each instance of this class manage a different microphone. """

        def __init__(self, thread_id, thread_name, device_id, url_sequence, phonometer_module):
            super().__init__()

            # Init Thread logger
            self._logger = util.init_mirrored_logger("("+str(thread_id)+")", logging.DEBUG)

            # Enable log storage in file
            # self._logger = util.init_mirrored_logger(str(thread_id), logging.DEBUG, "mic_"+str(thread_id)+".log")

            self._thread_name = thread_name
            self._thread_id = thread_id
            self._device_id = device_id
            self._url_sequence = url_sequence
            self._phonometer_module = phonometer_module

        def run(self):
            self._logger.info("Starting Thread: " + self._thread_name)

            rc = self._phonometer_module.get_resource_catalog()
            self._logger.info("\n\n--- Start OGC OBSERVATIONs registration ---\n")
            while True:
                try:
                    now = arrow.utcnow()
                    query_ts_start = util.from_utc_to_query(now - timedelta(seconds=UPDATE_INTERVAL), False, False)
                    query_ts_end = util.from_utc_to_query(arrow.utcnow(), False, False)

                    time_token = query_ts_start + FILTER_SDN_2 + query_ts_end + FILTER_SDN_3
                    url_data_seq = self._url_sequence + time_token

                    r = requests.get(url_data_seq, headers=REST_HEADERS)
                    if not r or not r.ok:
                        raise Exception("Something wrong retrieving data!")

                    payload = r.json()["d"]["results"]

                    if payload and len(payload) >= 1:  # is the payload not empty?
                        data_laeq = []
                        data_spectra = []

                        for result in payload:
                            data_laeq.append(float(result[LAEQ_KEY]))

                            spectra = [0]
                            for interval in FREQ_INTERVALS:
                                band = 'b_' + interval + '_Hz'
                                freq_value = result[band]
                                # freq_value might be NULL or negative
                                if not freq_value or float(freq_value) < 0:
                                    spectra.append(0)
                                else:
                                    spectra.append(float(freq_value))

                            data_spectra.append(spectra)

                            # Registering LAEq value in GOST
                            datastream_id = rc[self._device_id][LAEQ_KEY]
                            phenomenon_time = query_ts_start
                            observation_result = {"valueType": LAEQ_KEY, "response": data_laeq}
                            self._phonometer_module.ogc_observation_registration(
                                datastream_id, phenomenon_time, observation_result)

                            # Registering spectra value in GOST
                            datastream_id = rc[self._device_id][SPECTRA_KEY]
                            phenomenon_time = query_ts_start
                            observation_result = {"valueType": SPECTRA_KEY, "response": data_spectra}
                            self._phonometer_module.ogc_observation_registration(
                                datastream_id, phenomenon_time, observation_result)

                    else:
                        self._logger.error("Empty Payload!")

                    time.sleep(UPDATE_INTERVAL)
                # Loop End

                except Exception as ex:
                    if isinstance(ex, NewConnectionError):
                        self._logger.error("Connection error: " + str(ex))
                    elif isinstance(ex, MaxRetryError):
                        self._logger.error("Too many connection attempts: " + str(ex))
                    else:
                        self._logger.error(str(ex))

                    self._logger.info("Retrying after " + str(RETRY_INTERVAL) + " seconds.")
                    time.sleep(RETRY_INTERVAL)
