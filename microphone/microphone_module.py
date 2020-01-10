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
import logging
import arrow
import json

from scral_ogc import OGCObservation

from scral_core.ogc_configuration import OGCConfiguration
from scral_core.constants import CATALOG_FILENAME
from scral_core.rest_module import SCRALRestModule

from microphone.constants import NAME_KEY, SEQUENCES_KEY


class SCRALMicrophone(SCRALRestModule):
    """ Resource manager for integration of Phonometers. """

    def __init__(self, ogc_config: OGCConfiguration, connection_file: str, pilot: str,
                 catalog_name: str = CATALOG_FILENAME):
        super().__init__(ogc_config, connection_file, pilot, catalog_name)
        self._active_microphones = {}

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
