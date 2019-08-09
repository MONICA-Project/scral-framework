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

import paho.mqtt.client as mqtt

from scral_module import mqtt_util, util
from scral_module.constants import ENABLE_FLASK, CATALOG_FILENAME, \
                                   BROKER_DEFAULT_PORT, DEFAULT_KEEPALIVE, DEFAULT_MQTT_QOS, \
                                   ERROR_WRONG_PILOT_NAME
from wristband.constants import PROPERTY_LOCALIZATION_NAME, PROPERTY_BUTTON_NAME
from wristband_mqtt.constants import CLIENT_ID
from wristband.wristband_module import SCRALWristband

MESSAGE_RECEIVED = 0


class SCRALMQTTWristband(SCRALWristband):

    def __init__(self, ogc_config, connection_file, pilot, catalog_name=CATALOG_FILENAME):
        """ Initialize MQTT Brokers for listening and publishing

        :param connection_file: A file containing connection information.
        :param pilot: The pilot name,
                      it will be used for generate the MQTT topic prefix on which information will be published.
        """

        super().__init__(ogc_config, connection_file, pilot, catalog_name)

        # Creating an MQTT Subscriber
        self._mqtt_subscriber = mqtt.Client(CLIENT_ID)

        # Retrieving MQTT connection info from connection_file
        connection_config_file = util.load_from_file(connection_file)
        self._sub_broker_address = connection_config_file["mqtt"]["sub_broker"]
        self._sub_broker_port = connection_config_file["mqtt"]["sub_broker_port"]
        self._sub_keepalive = connection_config_file["mqtt"]["sub_broker_keepalive"]

        # Associate callback functions
        self._mqtt_subscriber.on_connect = mqtt_util.on_connect
        self._mqtt_subscriber.on_disconnect = mqtt_util.automatic_reconnection
        self._mqtt_subscriber.on_message = self.on_message_received

        #  MQTT Subscriber setting configuration
        logging.info(
            "Try to connect to broker: %s:%s for LISTENING..." % (self._sub_broker_address, self._sub_broker_port))
        logging.debug("MQTT Client ID is: " + str(self._mqtt_subscriber._client_id))
        self._mqtt_subscriber.connect(self._sub_broker_address, self._sub_broker_port, self._sub_keepalive)

    def mqtt_subscriptions(self, device: str):
        topic = self._topic_prefix+"SCRAL/"+device+"/Localization"

        logging.info("Subscribing to MQTT topic: " + topic)
        self._mqtt_subscriber.subscribe(topic, 2)  # DEFAULT_MQTT_QOS)
        self._mqtt_subscriber.loop_start()

        # ToDo: adding dynamic discovery phase in the future.
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
        logging.info("Messages Number: "+str(MESSAGE_RECEIVED)+" - Device: "+payload["tagId"]+" -  topic: "+topic)

        result = None
        if "Localization" in topic:
            result = self.ogc_observation_registration(PROPERTY_LOCALIZATION_NAME, payload)
        elif "Button" in topic:
            result = self.ogc_observation_registration(PROPERTY_BUTTON_NAME, payload)
        else:
            logging.error("Unrecognized topic: " + topic)

        if not result:
            logging.error("Error sending an MQTT message.\n"+topic+"\n"+payload)
