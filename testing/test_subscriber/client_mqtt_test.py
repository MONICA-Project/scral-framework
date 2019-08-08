import signal
import sys
import time
import datetime
import json
import logging

import paho.mqtt.client as mqtt
import arrow

# DICTIONARY_OBSERVABLE_TOPICS = {1: ["GOST_TIVOLI/Datastreams"]}
DICTIONARY_OBSERVABLE_TOPICS = {1: ["GOST_LARGE_SCALE_TEST/+/Observations"]}
# from dictionary_catalog_local import DICTIONARY_OBSERVABLE_TOPICS

RABBITMQ_URL = "mpclsifrmq01.monica-cloud.eu"
LST_URL = "monapp-lst.monica-cloud.eu"
MONICA_URL = "monappdwp3.monica-cloud.eu"
INTERNAL_BROKER_NAME = "mosquitto"
LOCAL = "localhost"

PORT = 1883
LOCAL_PORT = 1884
BURST_SIZE = 5000


class Settings:
    list_topics = list()
    flag_connection = 0
    flag_subscribe = 0
    counter_message_received = 0
    time_diff = 30

    @staticmethod
    def initialize_main_list():
        if not DICTIONARY_OBSERVABLE_TOPICS:
            logging.warning("No dictionary!")
            return

        for key in DICTIONARY_OBSERVABLE_TOPICS:
            list_string = DICTIONARY_OBSERVABLE_TOPICS[key]

            if not list_string:
                continue

            # Settings.list_topics.append((list_string[0], 0))
            Settings.list_topics.append((list_string[0], 1))
            # Settings.list_topics.append((list_string[0], 2))


def on_message(client, userdata, message):
    try:
        current_time = arrow.utcnow()

        logging.info("Message topic: " + message.topic)
        logging.info("Message received: " + str(message.payload))
        logging.info("current_time: " + str(current_time.format('YYYY-MM-DD HH:mm:ss')))
        # logging.info("message qos=",message.qos)
        # logging.info("message retain flag=",message.retain)

        string_json = str(message.payload.decode("utf-8"))
        json_received = json.loads(string_json)
        try:
            timestamp_str = json_received["phenomenonTime"]
            timestamp = arrow.get(timestamp_str)
            # timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            diff = current_time - timestamp
            diff_sec = diff.total_seconds()
            logging.info("Message received after: " + str(diff_sec))
            if abs(diff_sec) > Settings.time_diff:
                logging.error(" ---------- Critical ---------- ")
        except KeyError:
            logging.warning("No phenomenonTime.")

        Settings.counter_message_received += 1

        logging.info('OnMessage JSON Conversion Success, counter_messages: {}\n'
                     .format(str(Settings.counter_message_received)))

        if Settings.counter_message_received % BURST_SIZE == 0:
            logging.info("======================================================================\n")

    except Exception as ex:
        logging.critical('Exception OnMessage: {}'.format(ex))


def on_connect(client, userdata, flags, rc):
    try:
        if Settings.flag_connection == 1:
            return

        Settings.flag_connection = 1
        counter_topics = len(Settings.list_topics)

        logging.info('Client Connected, Subscribing to {} Elements'.format(str(counter_topics)))
        logging.info(Settings.list_topics)
        client.subscribe(Settings.list_topics)

        # client.subscribe('GOST_IOTWEEK/Datastreams(583)/Observations')
        # client.subscribe('GOST_IOTWEEK/+/Observations')
        # client.subscribe('GOST_LARGE_SCALE_TEST//Antonio/Datastreams')

    except Exception as ex:
        logging.critical('Exception: {}'.format(ex))


def on_disconnect(client, userdata, flags, rc):
    try:
        Settings.flag_connection = 0
        logging.error('Client Disconnected')
        client.reconnect()
    except Exception as ex:
        logging.critical('Exception: {}'.format(ex))


def on_unsubscribe(client, userdata, level, buf):
    logging.info('Unsubscribed Success! {}'.format(buf))


def on_subscribe(client, userdata, level, buf):
    logging.info('Subscribed Success! {}'.format(len(buf)))


def on_log(client, userdata, level, buf):
    logging.info('MQTT Log raised: {}'.format(buf))


def convert_stringtime_to_epoch(string_time):
    time.mktime(datetime.datetime.strptime(string_time).timetuple())


def signal_handler(signal, frame):
    """ This signal handler overwrite the default behaviour of SIGKILL (pressing CTRL+C). """

    logging.critical('You pressed Ctrl+C!')
    print("\nThe MQTT listener is turning down now...\n")
    sys.exit(0)


def main(broker_address: str, port: int):
    logging.info("Creating new instance 3")
    client = mqtt.Client("LocalClientTest")  # create new instance

    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_unsubscribe = on_unsubscribe
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    # client.on_log = on_log

    # client.username_pw_set(username='mosquitto',password='mosquitto')

    Settings.initialize_main_list()

    logging.info("Connecting to broker: " + broker_address + ":" + str(port))
    client.connect(host=broker_address, port=port)  # connect to broker
    try:
        client.loop_forever()

    except Exception as ex:
        logging.critical('Exception in Main Function: {}'.format(ex))


if __name__ == '__main__':
    now = arrow.utcnow().format('YYYY-MM-DD_HH-mm')
    formatter = "%(asctime)s.%(msecs)04d %(name)-7s %(levelname)s: %(message)s"

    logging.basicConfig(filename="logs/" + str(now) + ".log", level=logging.DEBUG)
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(formatter, datefmt="(%b-%d) %H:%M:%S"))

    # signal.signal(signal.SIGINT, signal_handler)

    main(RABBITMQ_URL, PORT)