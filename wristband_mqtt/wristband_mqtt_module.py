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

from scral_core.constants import CATALOG_FILENAME, \
                                 MQTT_KEY, MQTT_SUB_BROKER_KEY, MQTT_SUB_BROKER_PORT_KEY, MQTT_SUB_BROKER_KEEP_KEY
from scral_core import mqtt_util, util
from scral_core.ogc_configuration import OGCConfiguration

from wristband.constants import PROPERTY_LOCALIZATION_NAME, PROPERTY_BUTTON_NAME, TAG_ID_KEY, SENSOR_ASSOCIATION_NAME
from wristband.wristband_module import SCRALWristband

from wristband_mqtt.constants import CLIENT_ID, BUTTON_SUBTOPIC, \
                                     ASSOCIATION_SUBTOPIC, LOCALIZATION_SUBTOPIC, LISTENING_DEFAULT_QOS

MESSAGE_RECEIVED: int = 0


class SCRALMQTTWristband(SCRALWristband):

    def __init__(self, ogc_config: OGCConfiguration, connection_file: str, catalog_name: str = CATALOG_FILENAME):
        """ Initialize MQTT Brokers for listening and publishing

        :param connection_file: A file containing connection information.
        :param catalog_name: The name of the resource catalog.
        """

        super().__init__(ogc_config, connection_file, catalog_name)

        # Creating an MQTT Subscriber
        self._mqtt_subscriber = mqtt.Client(CLIENT_ID)

        # Retrieving MQTT connection info from connection_file
        connection_config_file = util.load_from_file(connection_file)
        self._sub_broker_address = connection_config_file[MQTT_KEY][MQTT_SUB_BROKER_KEY]
        self._sub_broker_port = connection_config_file[MQTT_KEY][MQTT_SUB_BROKER_PORT_KEY]
        self._sub_keepalive = connection_config_file[MQTT_KEY][MQTT_SUB_BROKER_KEEP_KEY]

        # Associate callback functions
        self._mqtt_subscriber.on_connect = mqtt_util.on_connect
        self._mqtt_subscriber.on_disconnect = mqtt_util.automatic_reconnection
        self._mqtt_subscriber.on_message = self.on_message_received

        #  MQTT Subscriber setting configuration
        logging.info("Try to connect to broker: %s:%s for LISTENING..."
                     % (self._sub_broker_address, self._sub_broker_port))
        logging.debug("MQTT Client ID is: " + str(self._mqtt_subscriber._client_id))
        self._mqtt_subscriber.connect(self._sub_broker_address, self._sub_broker_port, self._sub_keepalive)

    def mqtt_subscriptions(self, device: str):
        topic = self._topic_prefix+"SCRAL/"+device+"/Localization"

        logging.info("Subscribing to MQTT topic: " + topic)
        self._mqtt_subscriber.subscribe(topic, LISTENING_DEFAULT_QOS)
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
