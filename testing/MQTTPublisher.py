#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################
#                                                                     #
#                       *Simple MQTT Publisher*                       #
#                Inspired by the PyPI MQTT Subscriber                 #
#             It was adapted to be used in SCRAL testing              #
#                                                                     #
#######################################################################
import argparse
import json
import logging
import random
import signal
import sys
import time

import arrow

import paho.mqtt.client as mqtt

from testing.MQTTListener import BROKER_ADDRESS, BROKER_PORT, KEEPALIVE, TOPIC

GPS_REST_PAYLOAD = {
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

WB_MQTT_PAYLOAD = {
  "tagId": "GeoTag00",
  "type": "uwb",
  "areaId": "unknown",
  "motion_state": "MOVING",
  "lat": 0.0,
  "lon": 0.0,
  "speed": 0.0,
  "speed_x": 0.0,
  "speed_y": 0.0,
  "speed_z": 0.0,
  "x": 0.0,
  "y": 0.0,
  "z": 0.0,
  "bearing": 0.0,
  "height": 0.0,
  "herr": 0.0,
  "battery_level": 4.074999809265137,
  "timestamp": str(arrow.utcnow())
}


def main():
    # configuring the logger
    log_configuration(logging.DEBUG)

    # signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # parsing command line
    args = parse_command_line()

    # Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp")
    client_id = "MQTT_Publisher"
    client = mqtt.Client(client_id=client_id)
    logging.info("Publisher Client ID: '" + client_id + "'")

    logging.info("Connecting to broker: '" + BROKER_ADDRESS + ":"+str(BROKER_PORT)+"' *** ")
    client.on_connect = on_connect
    client.connect(BROKER_ADDRESS, BROKER_PORT, KEEPALIVE)

    # input("\nPress any key to start MQTT sending messages...\n")

    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a manual interface.
    logging.info(" *** Start sending messages... *** \n")

    topic = TOPIC
    payload = WB_MQTT_PAYLOAD
    for i in range(1, args.number):
        # payload["@iot.id"] = i
        client.publish(topic=topic, payload=json.dumps(payload), qos=2)
        client.loop()
        logging.debug("Data " + str(i) + " written on topic " + TOPIC)
        time.sleep(args.sleep)


def on_connect(client, userdata, flags, rc):
    # The callback for when the client receives a CONNACK response from the server.
    logging.info("Connected to '" + BROKER_ADDRESS + "' with result code " + str(rc))


def log_configuration(debug_level):
    """ Configure the log """

    logging.basicConfig(format="%(message)s")
    logging.getLogger().setLevel(level=debug_level)
    logging.info("     ##########################     \n"
                 "     ###   MQTT Publisher   ###     \n"
                 "     ##########################     \n")
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)04d %(levelname)s: %(message)s", datefmt="%H:%M:%S"))


def parse_command_line():
    parser = argparse.ArgumentParser(prog='MQTTPublisher', epilog="example: MQTTPublisher.py -n 10",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-n', '--number', default=10, type=int, help='The number of mqtt packets to send')
    parser.add_argument('-s', '--sleep', default=0, type=float,
                        help='The amount of time (in seconds) to wait between a message and the next one')
    args = parser.parse_args()
    return args


def signal_handler(signal, frame):
    """ This signal handler overwrite the default behaviour of SIGKILL (pressing CTRL+C). """

    logging.critical('You pressed Ctrl+C!')
    print("\nThe MQTT listener is turning down now...\n")
    sys.exit(0)


if __name__ == '__main__':
    main()
