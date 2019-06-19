#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################
#                                                                     #
#                       *Simple MQTT Publisher*                       #
#                Inspired by the PyPI MQTT Subscriber                 #
#             It was adapted to be used in SCRAL testing              #
#######################################################################
import json
import logging
import random
import time
import paho.mqtt.client as mqtt
from testing.MQTTListener import BROKER_ADDRESS, BROKER_PORT, KEEPALIVE, TOPIC


def on_connect(client, userdata, flags, rc):
    # The callback for when the client receives a CONNACK response from the server.
    logging.info("Connected to '" + BROKER_ADDRESS + "' with result code " + str(rc))


def log_configuration(debug_level):
    """ Configure the log """

    logging.basicConfig(format="%(message)s")
    logging.getLogger().setLevel(level=debug_level)
    logging.info("     ##########################     \n"
                 "     ###   MQTT Publisher   ###     \n"
                 "     ##########################       ")
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)04d %(levelname)s: %(message)s", datefmt="%H:%M:%S"))


if __name__ == '__main__':
    # configuring the logger
    log_configuration(logging.DEBUG)

    # Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp")
    client = mqtt.Client()
    client.on_connect = on_connect

    logging.info(" *** Connecting to the broker '" + BROKER_ADDRESS + "' *** ")
    client.connect(BROKER_ADDRESS, BROKER_PORT, KEEPALIVE)

    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a manual interface.
    logging.info(" *** Start sending messages... *** ")
    client.loop_start()

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    payload = {
        "name": "gps-tracker-test",
        "description": "Continuously updated GPS location of tracker device",
        "encodingType": "application/vnd.geo+json",
        "location": {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [round(random.uniform(0, 100), 4), round(random.uniform(0, 100), 4)]
            }
        },
        "Things@iot.navigationLink": "http://test.geoportal-hamburg.de/itsLGVhackathon/v1.0/Locations(78819)/Things",
        "@iot.selfLink": "http://test.geoportal-hamburg.de/itsLGVhackathon/v1.0/Locations(78819)",
        "HistoricalLocations@iot.navigationLink":
            "http://test.geoportal-hamburg.de/itsLGVhackathon/v1.0/Locations(78819)/HistoricalLocations",
    }
    for i in range(1, 1000):
        payload["@iot.id"] = i
        client.publish(TOPIC, json.dumps(payload), 2)
        logging.debug("Data "+str(i)+" written on topic "+TOPIC)
        time.sleep(3)
