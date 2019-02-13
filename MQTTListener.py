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
import time

import paho.mqtt.client as mqtt

# BROKER_ADDRESS = "test.geoportal-hamburg.de"
# BROKER_ADDRESS = "130.192.85.32"
BROKER_ADDRESS = "localhost"

BROKER_PORT = 1883
KEEPALIVE = 60
CLIENT_ID = "MONICA_GPS"
TOPIC = "v1.0/Things(12295)/Locations"

# TOPIC_GOST = "GOST/+/Observations"
# TOPIC_ALL = "#"
# TOPIC_THING_ID = "v1.0/Things(12295)/#"
# TOPIC_ALL_THINGS = "v1.0/+/Locations"


def on_connect(client, userdata, flags, rc):
    topic = TOPIC
    # The callback for when the client receives a CONNACK response from the server.
    logging.info("Connected to '"+BROKER_ADDRESS+"' with result code "+str(rc))

    logging.info("Listening on topic: "+topic)
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic, 2)


def on_disconnect(client, userdata, rc):
    time.sleep(10)
    logging.info("Connection lost! Try to re-connecting...")
    client.connect(BROKER_ADDRESS, BROKER_PORT, KEEPALIVE)


def on_message(client, userdata, msg):
    # The callback for when a PUBLISH message is received from the server.
    logging.debug(" *** Message received *** ")
    logging.info(msg.topic+" "+str(msg.payload))


def log_configuration(debug_level):
    """ Configure the log """

    logging.basicConfig(format="%(message)s")
    logging.getLogger().setLevel(level=debug_level)
    logging.info("     #########################     \n"
                 "     ###   MQTT Listener   ###     \n"
                 "     #########################       ")
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)04d %(levelname)s: %(message)s", datefmt="%H:%M:%S"))


if __name__ == '__main__':
    # configuring the logger
    log_configuration(logging.DEBUG)

    # Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp")
    client = mqtt.Client(CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    logging.info(" *** Connecting to the broker '" + BROKER_ADDRESS + "' *** ")
    client.connect(BROKER_ADDRESS, BROKER_PORT, KEEPALIVE)

    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a manual interface.
    logging.info(" *** Start listening... *** ")
    client.loop_forever()
