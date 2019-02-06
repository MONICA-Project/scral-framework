##########################################################################
#        _____ __________  ___    __                                     #
#       / ___// ____/ __ \/   |  / /                                     #
#       \__ \/ /   / /_/ / /| | / /                                      #
#      ___/ / /___/ _, _/ ___ |/ /___                                    #
#     /____/\____/_/ |_/_/  |_/_____/  v.2.0 - enhanced by Python 3      #
#                                                                        #
# (c) 2019 by Jacopo Foglietti & Luca Mannella                           #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md  #
#                                                                        #
##########################################################################
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
    if verbose:
        logging.info("Try to re-connecting...")

    mqtt_client.connect(BROKER_DEFAULT_IP, BROKER_DEFAULT_PORT, DEFAULT_KEEPALIVE)
