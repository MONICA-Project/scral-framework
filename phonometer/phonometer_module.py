#############################################################################
#      _____ __________  ___    __                                          #
#     / ___// ____/ __ \/   |  / /                                          #
#     \__ \/ /   / /_/ / /| | / /                                           #
#    ___/ / /___/ _, _/ ___ |/ /___                                         #
#   /____/\____/_/ |_/_/  |_/_____/   Smart City Resource Adaptation Layer  #
#                                                                           #
# LINKS Foundation, (c) 2017-2020                                           #
# developed by Jacopo Foglietti & Luca Mannella                             #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md     #
#                                                                           #
#############################################################################
import time

import arrow
import logging
from threading import Thread, Lock

import requests
from datetime import timedelta

from flask import Flask
from urllib3.exceptions import NewConnectionError, MaxRetryError

from scral_ogc import OGCDatastream, OGCObservedProperty

from scral_core.constants import REST_HEADERS, CATALOG_FILENAME, COORD, LATITUDE_KEY, LONGITUDE_KEY, \
    START_DATASTREAMS_REGISTRATION, END_DATASTREAMS_REGISTRATION, START_OBSERVATION_REGISTRATION, ENABLE_CHERRYPY
from scral_core import util
from scral_core.ogc_configuration import OGCConfiguration

from microphone.microphone_module import SCRALMicrophone
from microphone.constants import SEQUENCES_KEY, NAME_KEY

from phonometer.constants import URL_TENANT, ACTIVE_DEVICES, FILTER_SDN_1, URL_CLOUD, UPDATE_INTERVAL, LAEQ_KEY, \
    SPECTRA_KEY, RETRY_INTERVAL, FREQ_INTERVALS, FILTER_SDN_2, FILTER_SDN_3, METADATA_KEY, STREAM_KEY, SMART_OBJECT_KEY, \
    CODE_KEY, DATASET_KEY, DESCRIPTION_KEY, TOTAL_COUNT_KEY, COUNT_KEY, OBS_DATA_KEY, OBS_DATA_RESULTS_KEY, \
    VALUE_TYPE_KEY, RESPONSE_KEY


class SCRALPhonometer(SCRALMicrophone):
    """ Resource manager for integration of Phonometers. """

    def __init__(self, ogc_config: OGCConfiguration, config_filename: str, catalog_name: str = CATALOG_FILENAME):
        """ Load OGC configuration model and initialize MQTT Broker for publishing Observations

        :param config_filename: A file containing connection information.
        """
        super().__init__(ogc_config, config_filename, catalog_name)
        self._publish_mutex = Lock()

    def runtime(self, flask_instance: Flask, mode: int = ENABLE_CHERRYPY):
        """ This method discovers active Phonometers from SDN cloud, registers them as OGC Datastreams into the MONICA
            cloud and finally retrieves sound measurements for each device by using parallel querying threads.

            Furthermore, this method deploys a REST endpoint to retrieve module status information.
        """

        # Start Phonometer discovery and Datastream registration
        self.ogc_datastream_registration(URL_TENANT)

        # Start thread pool for Observations
        self._start_thread_pool(SCRALPhonometer.PhonoThread)

        # starting REST web server
        super().runtime(flask_instance, mode)

    def ogc_datastream_registration(self, url: str):
        """ This method receives a target URL as parameter and discovers active Phonometers.
            A new OGC Datastream for each couple Phonometer-ObservedProperty is registered.

        :param url: Target server address.
        """

        logging.info(START_DATASTREAMS_REGISTRATION)
        count = 0
        i = 1
        while True:
            r = None
            query_url = url + "&start="+str(count)
            try:
                r = requests.get(query_url)
            except Exception as ex:
                logging.error(ex)

            if not r or not r.ok:
                raise ConnectionError(
                    "Connection status: "+str(r.status_code)+"\nImpossible to establish a connection with "+query_url)

            payload = r.json()
            phonometers = payload[METADATA_KEY]

            logging.debug("\n\nPhonometers retrieved (page "+str(i)+"):\n")
            for phono in phonometers:
                logging.debug(phono[STREAM_KEY][SMART_OBJECT_KEY][NAME_KEY])
                logging.debug(phono[STREAM_KEY][SMART_OBJECT_KEY][CODE_KEY]+"\n")

            # OGC DATASTREAM Registration ONLY of active devices
            for phono in phonometers:
                if phono[DATASET_KEY][CODE_KEY] in ACTIVE_DEVICES:
                    device_id = phono[DATASET_KEY][CODE_KEY]
                    device_name = phono[NAME_KEY]
                    device_coordinates = (phono[LONGITUDE_KEY], phono[LATITUDE_KEY])
                    device_description = phono[DESCRIPTION_KEY]

                    # Check whether device has been already registered
                    if device_id in self._resource_catalog:
                        logging.debug("Device: " + device_name + " already registered with id: " + device_id)
                    else:
                        self._resource_catalog[device_id] = {}
                        self._active_microphones[device_id] = {}
                        # Iterate over ObservedProperties
                        for ogc_property in self._ogc_config.get_observed_properties():
                            self._new_datastream(
                                ogc_property, device_id, device_coordinates, device_description)

                        url_sequence = URL_CLOUD + '/' + device_id + '/' + FILTER_SDN_1
                        self._active_microphones[device_id][SEQUENCES_KEY] = url_sequence
                        self._active_microphones[device_id][NAME_KEY] = device_name

            total_count = payload[TOTAL_COUNT_KEY]
            count += payload[COUNT_KEY]
            i += 1
            if count >= total_count:
                break

        # self.update_file_catalog()
        logging.info(END_DATASTREAMS_REGISTRATION)

    class PhonoThread(Thread):
        """ Each instance of this class manage a different microphone. """

        def __init__(self, thread_id: str, thread_name: str, device_id: str, url_sequence: str,
                     phonometer_module: "SCRALPhonometer"):
            super().__init__()

            # thread_debug_name = "("+str(thread_id)+")"
            thread_debug_name = "(" + thread_name + ")"

            # Init Thread logger
            self._logger = util.init_mirrored_logger(thread_debug_name, logging.DEBUG)

            # Enable log storage in file
            # self._logger = util.init_mirrored_logger(
            #     thread_debug_name, logging.DEBUG, "mic_"+thread_debug_name+".log")

            self._thread_name = thread_name
            self._thread_id = thread_id
            self._device_id = device_id
            self._url_sequence = url_sequence
            self._phonometer_module = phonometer_module

        def run(self):
            self._logger.info("Starting Thread: " + self._thread_name)

            rc = self._phonometer_module.get_resource_catalog()
            self._logger.info(START_OBSERVATION_REGISTRATION)
            while True:
                try:
                    now = arrow.utcnow()
                    # change parameters of "from_utc_to_query" is milliseconds are required
                    query_ts_start = util.from_utc_to_query(now - timedelta(seconds=UPDATE_INTERVAL), True, False)
                    query_ts_end = util.from_utc_to_query(now, True, False)

                    time_token = query_ts_start + FILTER_SDN_2 + query_ts_end + FILTER_SDN_3
                    url_data_seq = self._url_sequence + time_token

                    r = requests.get(url_data_seq, headers=REST_HEADERS)
                    if not r or not r.ok:
                        raise Exception("Something wrong retrieving data!")

                    payload = r.json()[OBS_DATA_KEY][OBS_DATA_RESULTS_KEY]

                    if payload and len(payload) >= 1:  # is the payload not empty?
                        data_laeq = []
                        data_spectra = []

                        for result in payload:
                            data_laeq.append(float(result[LAEQ_KEY]))

                            spectra = [0]  # adding a leading 0 to uniform with SLM microphones
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
                        phenomenon_time = query_ts_start[:-1]+".000Z"
                        response = {"value": [{
                            "values": data_laeq,
                            "startTime": phenomenon_time,
                            "endTime": query_ts_end[:-1]+".000Z"
                        }]}

                        observation_result = {VALUE_TYPE_KEY: LAEQ_KEY, RESPONSE_KEY: response}
                        self._phonometer_module.ogc_observation_registration(
                            datastream_id, phenomenon_time, observation_result)

                        # Registering spectra value in GOST (CBPLZeq)
                        datastream_id = rc[self._device_id][SPECTRA_KEY]
                        phenomenon_time = query_ts_start[:-1]+".000Z"
                        response = {"value": [{
                            "values": data_spectra,
                            "startTime": phenomenon_time,
                            "endTime": query_ts_end[:-1]+".000Z"
                        }]}

                        observation_result = {VALUE_TYPE_KEY: SPECTRA_KEY, RESPONSE_KEY: response}
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
