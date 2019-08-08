#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################################################################
#                                                                                                   #
#                                    *Simple MQTT Listener*                                         #
#                                                                                                   #
#  This is an example of an MQTT Subscriber taken from the Python Package Index (PyPI) repository.  #
#  Url: https://pypi.org/project/paho-mqtt/                                                         #
#                                                                                                   #
#  It was adapted to be used for SCRAL testing.                                                     #
#####################################################################################################
import logging
import signal
import sys
import time

import paho.mqtt.client as mqtt

BROKER_HAMBURG = "test.geoportal-dom.de"
BROKER_PERT = "130.192.85.32"
BROKER_MONICA = "monappdwp3.monica-cloud.eu"
BROKER_LOCAL = "localhost"

BROKER_PORT = 1884
KEEPALIVE = 60
CLIENT_ID = "MONICA_GPS"

TOPIC_ALL = "#"
TOPIC_GOST_ALL_OBSERVATIONS = "GOST/+/Observations"
TOPIC_THING_ID = "v1.0/Things(12295)/#"
TOPIC_ALL_THINGS = "v1.0/+/Locations"
TOPIC_WB_MQTT = "GOST/SCRAL/Wristband/Localization"


BROKER_ADDRESS = BROKER_LOCAL
TOPIC = TOPIC_WB_MQTT


def on_connect(client, userdata, flags, rc):
    # The callback for when the client receives a CONNACK response from the server.
    logging.info("Connected to '"+BROKER_ADDRESS+"' with result code "+str(rc))

    logging.info("Listening on topic: "+TOPIC)
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(TOPIC, 2)


def on_disconnect(client, userdata, rc):
    time.sleep(10)
    logging.info("Connection lost! Try to re-connecting...")
    client.connect(BROKER_ADDRESS, BROKER_PORT, KEEPALIVE)


def on_message(client, userdata, msg):
    # The callback for when a PUBLISH message is received from the server.
    logging.debug(" *** Message received *** ")
    logging.info(msg.topic+" "+str(msg.payload))


def log_configuration(debug_level):
    """ Configuring the log """

    logging.basicConfig(format="%(message)s")
    logging.getLogger().setLevel(level=debug_level)
    logging.info("     #########################     \n"
                 "     ###   MQTT Listener   ###     \n"
                 "     #########################       ")
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)04d %(levelname)s: %(message)s", datefmt="%H:%M:%S"))


def signal_handler(signal, frame):
    """ This signal handler overwrite the default behaviour of SIGKILL (pressing CTRL+C). """

    logging.critical('You pressed Ctrl+C!')
    print("\nThe MQTT listener is turning down now...\n")
    sys.exit(0)


if __name__ == '__main__':
    # configuring the logger
    log_configuration(logging.DEBUG)

    # Signal Handler
    signal.signal(signal.SIGINT, signal_handler)

    # Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp")
    client = mqtt.Client(CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    logging.info(" *** Connecting to broker '" + BROKER_ADDRESS + ":"+str(BROKER_PORT)+"' *** ")
    client.connect(BROKER_ADDRESS, BROKER_PORT, KEEPALIVE)

    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a manual interface.
    logging.info(" *** Start listening... *** ")
    client.loop_forever()
