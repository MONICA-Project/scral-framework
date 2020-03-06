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
import json
import logging
import os
import sys
import time

import paho.mqtt.client as mqtt

from scral_core.constants import CATALOG_FILENAME, DEFAULT_KEEPALIVE, BROKER_DEFAULT_PORT, \
                                 ERROR_MISSING_PARAMETER, ERROR_MISSING_ENV_VARIABLE, \
                                 MQTT_KEY, MQTT_SUB_BROKER_KEY, MQTT_SUB_BROKER_PORT_KEY, MQTT_SUB_BROKER_KEEP_KEY
from scral_core import mqtt_util, util
from scral_core.ogc_configuration import OGCConfiguration

from wristband.constants import PROPERTY_LOCALIZATION_NAME, PROPERTY_BUTTON_NAME, TAG_ID_KEY, SENSOR_ASSOCIATION_NAME
from wristband.wristband_module import SCRALWristband

from wristband_mqtt.constants import CLIENT_ID, BUTTON_SUBTOPIC, DEFAULT_SUBSCRIPTION_WB, \
                                     ASSOCIATION_SUBTOPIC, LOCALIZATION_SUBTOPIC, LISTENING_DEFAULT_QOS

MESSAGE_RECEIVED: int = 0


class SCRALMQTTWristband(SCRALWristband):

    def __init__(self, ogc_config: OGCConfiguration, config_filename: str, catalog_name: str = CATALOG_FILENAME):
        """ Initialize MQTT Brokers for listening and publishing

        :param config_filename: A file containing connection information.
        :param catalog_name: The name of the resource catalog.
        """

        super().__init__(ogc_config, config_filename, catalog_name)

        # Creating an MQTT Subscriber
        self._mqtt_subscriber = mqtt.Client(CLIENT_ID)
        self._mqtt_subscriber.connected_flag = False  # create connection flag in client
        self._mqtt_subscriber.on_connect = mqtt_util.on_connect
        self._mqtt_subscriber.on_disconnect = self.automatic_reconnection
        self._mqtt_subscriber.on_message = self.on_message_received

        # Retrieving MQTT subscribing info from config_filename
        if config_filename:
            config_file = util.load_from_file(config_filename)
            try:
                self._sub_broker_address = config_file[MQTT_KEY][MQTT_SUB_BROKER_KEY]
            except KeyError as ex:
                logging.critical('Missing parameter: '+str(ex)+' in configuration file.')
                sys.exit(ERROR_MISSING_PARAMETER)
            try:
                self._sub_broker_port = int(config_file[MQTT_KEY][MQTT_SUB_BROKER_PORT_KEY])
            except KeyError as ex:
                logging.warning('Missing parameter: '+str(ex)+'.Default value used: '+str(BROKER_DEFAULT_PORT))
                self._sub_broker_port = BROKER_DEFAULT_PORT
            try:
                self._sub_broker_keepalive = int(config_file[MQTT_KEY][MQTT_SUB_BROKER_KEEP_KEY])
            except KeyError:
                logging.warning(
                    "No subscribing broker keepalive specified, default one used: "+str(DEFAULT_KEEPALIVE)+" s")
                self._sub_broker_keepalive = DEFAULT_KEEPALIVE

        # Retrieving MQTT publishing info from environmental variables
        else:
            try:
                self._sub_broker_address = os.environ[MQTT_SUB_BROKER_KEY.upper()]
            except KeyError as ex:
                logging.critical('Missing environmental variable: ' + str(ex))
                sys.exit(ERROR_MISSING_ENV_VARIABLE)
            try:
                self._sub_broker_port = int(os.environ[MQTT_SUB_BROKER_PORT_KEY.upper()])
            except KeyError as ex:
                logging.warning('Missing environmental variable: ' + str(ex) +
                                '.Default value used: ' + str(BROKER_DEFAULT_PORT))
                self._sub_broker_port = BROKER_DEFAULT_PORT
            try:
                self._sub_broker_keepalive = int(os.environ[MQTT_SUB_BROKER_KEEP_KEY.upper()])
            except KeyError:
                logging.warning("No subscribing broker keepalive specified, will be used the default one: "
                                + str(DEFAULT_KEEPALIVE) + " s")
                self._sub_broker_keepalive = DEFAULT_KEEPALIVE

        #  MQTT Subscriber setting configuration
        logging.info("Try to connect to broker: %s:%s for LISTENING..."
                     % (self._sub_broker_address, self._sub_broker_port))
        logging.debug("MQTT Client ID is: " + str(self._mqtt_subscriber._client_id))
        self._mqtt_subscriber.connect(self._sub_broker_address, self._sub_broker_port, self._sub_broker_keepalive)
        # Two connection to the same broker are apparently problematic...
        # while not self._mqtt_subscriber.connected_flag:  # wait in loop
        #     logging.debug("Waiting...")
        #     time.sleep(1)

    def mqtt_subscriptions(self, device: str):
        topic = self._topic_prefix+"SCRAL/"+device+"/Localization"

        logging.info("Subscribing to MQTT topic: " + topic)
        self._mqtt_subscriber.subscribe(topic, LISTENING_DEFAULT_QOS)
        logging.info("Start listening...")
        self._mqtt_subscriber.loop_start()

        # ToDo: Here we can add dynamic discovery phase in the future as did in gps_tracker_poll
        # if dynamic_discovery:
        #     th = Thread(target=self.dynamic_discovery)
        #     th.start()
        #     self._mqtt_subscriber.loop_start()
        #     th.join()
        # else:
        #     self._mqtt_subscriber.loop_forever()

    def on_message_received(self, client, userdata, msg):
        global MESSAGE_RECEIVED
        MESSAGE_RECEIVED += 1

        topic = msg.topic
        payload = json.loads(msg.payload)
        logging.info("Messages Number: "+str(MESSAGE_RECEIVED)+" - Device: "+payload[TAG_ID_KEY]+" -  topic: "+topic)

        result = None
        if LOCALIZATION_SUBTOPIC in topic:
            result = self.ogc_observation_registration(PROPERTY_LOCALIZATION_NAME, payload)
        elif BUTTON_SUBTOPIC in topic:
            result = self.ogc_observation_registration(PROPERTY_BUTTON_NAME, payload)
        elif ASSOCIATION_SUBTOPIC in topic:
            vds = self.get_ogc_config().get_virtual_datastream(SENSOR_ASSOCIATION_NAME)
            if not vds:
                logging.critical('No Virtual DATASTREAM registered for Virtual SENSOR: "'+SENSOR_ASSOCIATION_NAME+'"')
                result = None
            else:
                result = self.ogc_service_observation_registration(vds, payload)
        else:
            logging.error("Unrecognized topic: " + topic)

        if not result:
            logging.error("Error sending an MQTT message.\n"+topic+"\n"+payload)

    def automatic_reconnection(self, client, userdata, rc):
        time.sleep(10)
        logging.error("Broker connection lost! Try to re-connecting to '" + str(client._host) + "'...")
        client.reconnect()
        time.sleep(5)
        counter = 1
        while not client.connected_flag:  # wait in loop
            logging.debug("Waiting "+str(counter)+"s...")
            time.sleep(1)
        logging.info("Re-subscribing to topics again...")
        self.mqtt_subscriptions(DEFAULT_SUBSCRIPTION_WB)
