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
import logging
from threading import Lock

import arrow
import json

from scral_ogc import OGCObservation, OGCObservedProperty, OGCDatastream

from scral_core.ogc_configuration import OGCConfiguration
from scral_core.constants import CATALOG_FILENAME, COORD
from scral_core.rest_module import SCRALRestModule

from microphone.constants import NAME_KEY, SEQUENCES_KEY


class SCRALMicrophone(SCRALRestModule):
    """ Resource manager for integration of Phonometers. """

    def __init__(self, ogc_config: OGCConfiguration, config_filename: str, catalog_name: str = CATALOG_FILENAME):
        super().__init__(ogc_config, config_filename, catalog_name)
        self._active_microphones = {}
        self._publish_mutex = Lock()

    def _start_thread_pool(self, microphone_thread, locking: bool = False):
        """ This method starts a thread for each active microphone (Sound Level Meter).

        :param microphone_thread: The microphone thread that you need.
        :param locking: True if you would like to return from this methods only after all threads are completed.
        """

        thread_pool = []
        thread_id = 1

        for device_id, values in self._active_microphones.items():
            t_name = values[NAME_KEY]
            sequences = values[SEQUENCES_KEY]

            thread = microphone_thread(
                thread_id, t_name, device_id, sequences, self)
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

    def _new_datastream(self, ogc_property: OGCObservedProperty, device_id: str,
                        device_coordinates: COORD, device_description: str):
        """ This method creates a new DATASTREAM.

        :param ogc_property: The OBSERVED PROPERTY.
        :param device_id: The physical device ID.
        :param device_coordinates: An array (or tuple) of coordinates.
        :param device_description: A device description.
        :return: The DATASTREAM ID of the new created device.
        """
        # Collect OGC information needed to build Datastreams payload
        thing = self._ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor = self._ogc_config.get_sensors()[0]  # Assumption: only one Sensor is defined for this adapter.
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

    def ogc_observation_registration(self, datastream_id: int, phenomenon_time: str, observation_result):
        """ This method sends an OBSERVATION to the MQTT broker.

        :param datastream_id: The DATASTREAM ID to be used.
        :param phenomenon_time: The time on which the OBSERVATION was recorded.
        :param observation_result: The value of the OBSERVATION.
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
            to_ret = self.mqtt_publish(topic, json.dumps(observation.get_rest_payload()), to_print=True)
            self._update_active_devices_counter()
        finally:
            self._publish_mutex.release()

        return to_ret
