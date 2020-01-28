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
import json
import logging
from threading import Thread
from time import sleep
from typing import Dict

import requests
import paho.mqtt.client as mqtt
import arrow
from requests.exceptions import SSLError

from scral_ogc import OGCObservation, OGCDatastream

from scral_core.ogc_configuration import OGCConfiguration
from scral_core import util, mqtt_util
from scral_core.constants import DEFAULT_KEEPALIVE, DEFAULT_MQTT_QOS, OGC_ID_KEY, CATALOG_FILENAME, \
                                 MQTT_KEY, MQTT_SUB_BROKER_KEY, MQTT_SUB_BROKER_PORT_KEY, MQTT_SUB_BROKER_KEEP_KEY

from gps_tracker.constants import LOCALIZATION
from gps_tracker.gps_module import SCRALGPS
from gps_tracker_poll.constants import BROKER_HAMBURG_CLIENT_ID, OGC_HAMBURG_THING_URL, \
    OGC_HAMBURG_FILTER, DEVICE_ID_KEY, THINGS_SUBSCRIBE_TOPIC, HAMBURG_UNIT_OF_MEASURE, DYNAMIC_DISCOVERY_SLEEP


class SCRALGPSPoll(SCRALGPS):
    """ Resource manager for integration of the GPS-TRACKER-GW (by usage of LoRa devices). """

    def __init__(self, ogc_config: OGCConfiguration, connection_file: str, catalog_name: str = CATALOG_FILENAME):
        """ Initialize MQTT Brokers for listening and publishing

        :param connection_file: A file containing connection information.
        """

        super().__init__(ogc_config, connection_file, catalog_name)

        # Creating an MQTT Subscriber
        self._mqtt_subscriber = mqtt.Client(BROKER_HAMBURG_CLIENT_ID)
        self._mqtt_subscriber.on_connect = mqtt_util.on_connect
        self._mqtt_subscriber.on_disconnect = mqtt_util.automatic_reconnection
        self._mqtt_subscriber.on_message = self.on_message_received

        # Loading broker info
        connection_config_file = util.load_from_file(connection_file)
        self._sub_broker_address = connection_config_file[MQTT_KEY][MQTT_SUB_BROKER_KEY]
        self._sub_broker_port = connection_config_file[MQTT_KEY][MQTT_SUB_BROKER_PORT_KEY]
        try:
            self._sub_broker_keepalive = connection_config_file[MQTT_KEY][MQTT_SUB_BROKER_KEEP_KEY]
        except KeyError:
            logging.warning(
                "No subscribing broker keepalive specified, will be used the default one: "+str(DEFAULT_KEEPALIVE)+" s")
            self._sub_broker_keepalive = DEFAULT_KEEPALIVE

        # broker connection test
        logging.info("Connecting to broker: %s:%s for listening" % (self._sub_broker_address, self._sub_broker_port))
        logging.debug("Client id is: '" + BROKER_HAMBURG_CLIENT_ID + "'")
        self._mqtt_subscriber.connect(self._sub_broker_address,  self._sub_broker_port, self._sub_broker_keepalive)

    # noinspection PyMethodOverriding
    def runtime(self, dynamic_discovery: bool = True):
        """ This method retrieves the THINGS from the Hamburg OGC server and convert them to MONICA OGC DATASTREAMS.
            These DATASTREAMS are published on MONICA OGC server.
            This is a "blocking function".

        :param dynamic_discovery:  A boolean value that enable the dynamic discovery of new devices.
        """
        self.datastream_discovery()

        if dynamic_discovery:
            th = Thread(target=self.dynamic_discovery)
            th.start()
            self._mqtt_subscriber.loop_start()
            th.join()
        else:
            self._mqtt_subscriber.loop_forever()

    def datastream_discovery(self):
        http_request = None
        try:
            http_request = requests.get(url=OGC_HAMBURG_THING_URL + OGC_HAMBURG_FILTER)
        except SSLError as tls_exception:
            logging.error("Error during TLS connection, the connection could be insecure or "
                          "the certificate could be self-signed...\n" + str(tls_exception))
        except Exception as ex:
            logging.error(ex)

        if http_request is None or not http_request.ok:
            raise ConnectionError(
                "URL: " + OGC_HAMBURG_THING_URL + " - Connection status: " + str(http_request.status_code)
                + "\nImpossible to establish a connection or resources not found.")
        else:
            logging.info("Connection status: " + str(http_request.status_code))

        hamburg_devices = http_request.json()["value"]
        for hd in hamburg_devices:
            iot_id = str(hd[OGC_ID_KEY])
            device_id = hd["name"]
            device_description = hd["description"]
            # if iot_id in self._resource_catalog:
            #   logging.info("Device: " + device_id + " already registered with id: " + iot_id)
            # else:
            datastreams = self.ogc_datastream_registration(
                device_id, device_description, HAMBURG_UNIT_OF_MEASURE,iot_id)
            if len(datastreams) > 0:
                # Associating HAMBURG THING id to MONICA DATASTREAM id (plus HAMBURG device_id)
                self._resource_catalog[iot_id][DEVICE_ID_KEY] = device_id

                for ds in datastreams:  # right now there is only 1 Datastream for each dom device
                    ds.set_mqtt_topic(THINGS_SUBSCRIBE_TOPIC + "(" + iot_id + ")/Locations")

        self.update_file_catalog()
        self.update_mqtt_subscription(self._ogc_config.get_datastreams())

    def update_mqtt_subscription(self, datastreams: Dict[str, OGCDatastream]):
        """ This method updates the lists of MQTT subscription topics.

        :param datastreams: A Dictionary of OGCDatastream
        """
        # Get the listening topics and run the subscriptions
        for ds in datastreams.values():
            top = ds.get_mqtt_topic()
            logging.debug("Subscribing to MQTT topic: " + top)
            self._mqtt_subscriber.subscribe(top, DEFAULT_MQTT_QOS)

    def dynamic_discovery(self):
        """ This method implements the dynamic discovery.
            This is a 'blocking function'.
        """
        while True:
            sleep(DYNAMIC_DISCOVERY_SLEEP)
            logging.debug("Starting Dynamic Discovery!")
            self.datastream_discovery()

    def on_message_received(self, client, userdata, msg):
        logging.debug("\nOn topic: "+msg.topic + " - message received:\n" + str(msg.payload))
        observation_time = str(arrow.utcnow())
        thing_id = str(msg.topic.split('(')[1].split(')')[0])  # Get the thing_id associated to the physical device

        datastream_id = self._resource_catalog[thing_id][LOCALIZATION]
        device_id = self._resource_catalog[thing_id][DEVICE_ID_KEY]
        topic_prefix = self._topic_prefix
        topic = topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # OBSERVATION result
        hamburg_obs_result = json.loads(msg.payload)["location"]["geometry"]  # Load the received message
        observation_result = {
            "tagId": device_id,
            "lon": hamburg_obs_result["coordinates"][0],
            "lat": hamburg_obs_result["coordinates"][1]
        }

        # Create OGC Observation and publish
        ogc_observation = OGCObservation(datastream_id, observation_time, observation_result, observation_time)
        observation_payload = json.dumps(dict(ogc_observation.get_rest_payload()))
        ok = self.mqtt_publish(topic, observation_payload)
        self._update_active_devices_counter()
        if not ok:
            logging.error("Impossible to send MQTT message")
