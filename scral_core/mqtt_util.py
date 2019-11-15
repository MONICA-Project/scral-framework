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
"""
    SCRAL - mqtt_util
    This file contains several MQTT utility functions that could be used in different modules.
"""

import time
import logging

from scral_core.constants import DEFAULT_GOST_PREFIX
from paho.mqtt.client import MQTT_ERR_SUCCESS


def on_connect(client, userdata, flags, rc):
    if rc == MQTT_ERR_SUCCESS:
        logging.info("Connection with MQTT broker: '" + str(client._host) + "' successfully established!")
    else:
        logging.critical("Connection failed, error code: "+str(rc))


def automatic_reconnection(client, userdata, rc):
    time.sleep(10)
    logging.error("Broker connection lost! Try to re-connecting to '"+str(client._host)+"'...")
    client.reconnect()


def get_publish_mqtt_topic(pilot_name: str):
    """ This function retrieves the appropriate MQTT topic according to the pilot name.

    :param pilot_name: the name of the desired pilot
    :return: An MQTT topic string if the pilot name exists otherwise a boolean value (False).
    """
    pilot_name = pilot_name.upper()

    if pilot_name == 'LOCAL':
        mqtt_topic = DEFAULT_GOST_PREFIX
    elif pilot_name == 'MOVIDA':
        mqtt_topic = "GOST_MOVIDA/"
    elif pilot_name == 'SDOM':
        mqtt_topic = "GOST_DOM/"
    elif pilot_name == 'WDOM':
        mqtt_topic = "GOST_WDOM/"
    elif pilot_name == "FDL":
        mqtt_topic = "GOST_LUMIERE_2019/"
    elif pilot_name == "LEEDS":
        mqtt_topic = "GOST_LEEDS/"
    elif pilot_name == "TIVOLI":
        mqtt_topic = "GOST_TIVOLI/"
    elif pilot_name == "RIF":
        mqtt_topic = "GOST_RIF/"
    elif pilot_name == "PORT":
        mqtt_topic = "GOST_PA/"
    elif pilot_name == "NS":
        mqtt_topic = "GOST_NS/"
    elif pilot_name == "IOTWEEK":
        mqtt_topic = "GOST_IOTWEEK/"
    elif pilot_name == "KFF":
        mqtt_topic = "GOST_KFF/"
    elif pilot_name == "WT":
        mqtt_topic = "GOST_WOODSTOWER/"
    elif pilot_name == "PM":
        mqtt_topic = "GOST_PUETZ/"
    elif pilot_name == "ROSKILDE":
        mqtt_topic = "GOST_ROSKILDE/"
    elif pilot_name == "LST":
        mqtt_topic = "GOST_LARGE_SCALE_TEST/"
    else:
        mqtt_topic = False

    return mqtt_topic
