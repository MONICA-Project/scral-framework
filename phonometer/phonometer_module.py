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
import arrow
import json
import logging
from threading import Thread, Lock

import requests

from scral_module import util
from scral_module.scral_module import SCRALModule
from phonometer.constants import URL_TENANT, ACTIVE_DEVICES
from scral_ogc import OGCObservation, OGCDatastream


class SCRALPhonometer(SCRALModule):
    """ Resource manager for integration of Phonometers. """

    def __init__(self, ogc_config, connection_file, pilot):
        """ Load OGC configuration model and initialize MQTT Broker for publishing Observations

        :param connection_file: A file containing connection information.
        :param pilot: The MQTT topic prefix on which information will be published.
        """
        super().__init__(ogc_config, connection_file, pilot)

        self._publish_mutex = Lock()
        self._active_devices = {}

    def runtime(self):
        """ This method discovers active Phonometers from SDN cloud, registers them as OGC Datastreams into the MONICA
            cloud and finally retrieves sound measurements for each device by using parallel querying threads.
        """
        # Start Phonometer discovery and Datastream registration
        self.ogc_datastream_registration(URL_TENANT)

        # Start thread pool for Observations
        self._start_thread_pool()

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

                self._active_devices[device_id]["location_sequences"] = url_sequences

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

    def _start_thread_pool(self, locking=False):
        """ This method starts a thread for each active microphone.

        :param locking: True if you would like to return from this methods only after all threads are completed.
        """
        thread_pool = []
        thread_id = 1

        for device_id, values in self._active_devices.items():
            thread = SCRALPhonometer.PhonoThread(
                thread_id, "Thread-" + str(thread_id), device_id, values["location_sequences"], self)
            thread.start()
            thread_pool.append(thread)
            thread_id += 1

        if len(thread_pool) <= 0:
            logging.error("No thread detached, maybe no active devices.")
        else:
            logging.info("Threads detached")
            if locking:
                for thread in thread_pool:
                    thread.join()
                logging.error("All threads have been interrupted!")

    class PhonoThread(Thread):
        """ Each instance of this class manage a different microphone. """

        def __init__(self, thread_id, thread_name, device_id, url_sequences, phonometer_module):
            super().__init__()

            # Init Thread logger
            self._logger = util.init_mirrored_logger("("+str(thread_id)+")", logging.DEBUG)

            # Enable log storage in file
            # self._logger = util.init_mirrored_logger(str(thread_id), logging.DEBUG, "mic_"+str(thread_id)+".log")

            self._thread_name = thread_name
            self._thread_id = thread_id
            self._device_id = device_id
            self._url_sequences = url_sequences
            self._phonometer_module = phonometer_module

        def run(self):
            self._logger.info("Starting Thread: " + self._thread_name)

    def ogc_observation_registration(self, datastream_id, phenomenon_time, observation_result):
        """ This method sends an OBSERVATION to the MQTT broker.

        :param datastream_id: The DATASTREAM ID to be used.
        :param phenomenon_time: The time on which the OBSERVATION was recorded.
        :param observation_result: The time on which you are processing the OBSERVATION.
        :return: True if the message was send, False otherwise.
        """
        # Preparing MQTT topic
        topic = self._topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # Preparing Payload
        observation = OGCObservation(datastream_id, phenomenon_time, observation_result, str(arrow.utcnow()))

        to_ret = False
        # Publishing
        self._publish_mutex.acquire()
        try:
            to_ret = self.mqtt_publish(topic, json.dumps(observation.get_rest_payload()), to_print=False)
        finally:
            self._publish_mutex.release()

        return to_ret
