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

from scral_module import util
from scral_module.scral_module import SCRALModule
from phonometer.constants import URL_CLOUD
from scral_ogc import OGCObservation


class SCRALPhonometer(SCRALModule):
    """ Resource manager for integration of Phonometers. """

    def __init__(self, ogc_config, connection_file, pilot):
        """ Load OGC configuration model and initialize MQTT Broker for publishing Observations

        :param connection_file: A file containing connection information.
        :param pilot: The MQTT topic prefix on which information will be published.
        """
        super().__init__(ogc_config, connection_file, pilot)

        self._active_devices = {}
        self._publish_mutex = Lock()

    def runtime(self):
        """
        This method discovers active Phonometer from SDN cloud, registers them as OGC Datastreams into the MONICA
        cloud and finally retrieves sound measurements for each device by using parallel querying threads.
        """
        # Start SLM discovery and Datastream registration
        self.ogc_datastream_registration(URL_CLOUD)

        # Start thread pool for Observations
        self._start_thread_pool()

    def ogc_datastream_registration(self, url):
        """ This method receive a target URL as parameter and discovers active Phonometer.
            A new OGC Datastream for each couple Phonometer-ObservedProperty is registered.

        :param url: Target server address.
        """
        pass

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
