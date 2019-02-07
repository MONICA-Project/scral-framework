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
import time
import logging
from scral_gps_poll import verbose, mqtt_client

# IP configuration
BROKER_DEFAULT_IP = "test.mosquitto.org"
BROKER_DEFAULT_PORT = "1883"
DEFAULT_KEEPALIVE = 60


def on_connect(mqttc, userdata, flags, rc):
    logging.debug("rc = " + str(rc))


def on_disconnect(client, userdata, rc):
    time.sleep(10)
    logging.info("Connection lost! Try to re-connecting...")
    mqtt_client.connect(BROKER_DEFAULT_IP, BROKER_DEFAULT_PORT, DEFAULT_KEEPALIVE)


def get_mqtt_topic(pilot_name):
    """ This function retrieves the appropriate MQTT topic according to the pilot name

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
