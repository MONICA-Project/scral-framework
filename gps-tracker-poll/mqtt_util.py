##############################################################################
#      _____ __________  ___    __                                           #
#     / ___// ____/ __ \/   |  / /                                           #
#     \__ \/ /   / /_/ / /| | / /                                            #
#    ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Abstraction Layer  #
#   /____/\____/_/ |_/_/  |_/_____/   v.2.0 - enhanced by Python 3           #
#                                                                            #
# LINKS Foundation, (c) 2019                                                 #
# developed by Jacopo Foglietti & Luca Mannella                              #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md      #
#                                                                            #
##############################################################################
import json
import time
import logging

import arrow
import paho.mqtt.client as mqtt

from scral_constants import DEFAULT_KEEPALIVE, DEFAULT_MQTT_QOS
from scral_ogc import OGCObservation


class MQTTConnectionManager:
    """ This class manage an MQTT Publisher with the associated resource catalog. """



    def get_topic_prefix(self):
        return self._topic_prefix

    def get_resource_catalog(self):
        return self._resource_catalog

    def get_mqtt_publisher(self):
        return self._mqtt_publisher



def on_connect(mqttc, userdata, flags, rc):
    if rc != 0:
        logging.critical("Connection failed, error code: "+str(rc))
    else:
        logging.info("Connection with MQTT broker successfully established|")


def on_disconnect(client, userdata, rc):
    time.sleep(10)
    logging.info("Broker connection lost! Try to re-connecting to " + str(client._host) + "...")
    client.reconnect()


def get_publish_mqtt_topic(pilot_name):
    """ This function retrieves the appropriate MQTT topic according to the pilot name.

    :param pilot_name: the name of the desired pilot
    :return: An MQTT topic string if the pilot name exists otherwise a boolean value (False).
    """
    if pilot_name == 'local':
        mqtt_topic = "GOST/"
    elif pilot_name == 'MOVIDA':
        mqtt_topic = "GOST_MOVIDA/"
    elif pilot_name == 'DOM':
        mqtt_topic = "GOST_DOM/"
    elif pilot_name == "LUMIERE":
        mqtt_topic = "GOST_LUMIERE/"
    else:
        mqtt_topic = False

    return mqtt_topic
