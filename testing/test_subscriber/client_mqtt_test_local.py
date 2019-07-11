import paho.mqtt.client as mqtt
import time
import datetime
import dateutil.parser
import json
import numpy as np

import threading
from typing import List

DICTIONARY_OBSERVABLE_TOPICS = {1: ['GOST/#']}


class Settings:
    list_topics = list()
    flag_connection = 0
    flag_subscribe = 0
    counter_message_received = 0
    time_diff = 30

    @staticmethod
    def initialize_main_list():
        for key in DICTIONARY_OBSERVABLE_TOPICS:
            list_string = DICTIONARY_OBSERVABLE_TOPICS[key]

            if not list_string:
                continue

            Settings.list_topics.append((list_string[0], 0))

    @staticmethod
    def initialize_additional_list():
        Settings.list_topics.append(("GOST_LARGE_SCALE_TEST/Datastreams(23)/Observations", 0))
        Settings.list_topics.append(("GOST_LARGE_SCALE_TEST/Datastreams(25)/Observations", 0))


def on_message(client, userdata, message):
    try:
        current_time = datetime.datetime.now()
        current_time = current_time.astimezone(tz=datetime.timezone.utc)

        print("message topic=",message.topic)
        print("message received " ,str(message.payload.decode("utf-8")))
        print("timestamp: {}".format(current_time.strftime("%Y-%m-%d, %H:%M:%S%Z")))
        # print("message qos=",message.qos)
        # print("message retain flag=",message.retain)

        string_json = str(message.payload.decode("utf-8"))
        json_received = json.loads(string_json)
        timestamp_str = json_received["phenomenonTime"]
		
        timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        diff = current_time - timestamp
        if abs(diff.total_seconds()) > Settings.time_diff:
            print(" ============ Critical ============ ")

        Settings.counter_message_received += 1

        print('OnMessage JSON Conversion Success, counter_messages: {}\n'
        .format(str(Settings.counter_message_received)))
		
        if Settings.counter_message_received % 10 == 0:
            print("======================================================================\n")
		
    except Exception as ex:
        print('Exception OnMessage: {}'.format(ex))

  
def on_connect(client, userdata, flags, rc):
    try:
        if Settings.flag_connection == 1:
            return

        Settings.flag_connection = 1
        counter_topics = len(Settings.list_topics)

        print('Client Connected, Subscribing to {} Elements'.format(str(counter_topics)))
        client.subscribe(Settings.list_topics)
    except Exception as ex:
        print('Exception: {}'.format(ex))

def on_disconnect(client, userdata, flags, rc):
    try:
        Settings.flag_connection = 0
        print('Client Disconnected')
        client.reconnect()
    except Exception as ex:
        print('Exception: {}'.format(ex))

def on_unsubscribe(client, userdata, level, buf):
    print('Unsubscribed Success! {}'.format(buf))

def on_subscribe(client, userdata, level, buf):
    print('Subscribed Success! {}'.format(len(buf)))

def on_log(client, userdata, level, buf):
    print('MQTT Log raised: {}'.format(buf))    

def convert_stringtime_to_epoch(string_time):
    time.mktime(datetime.datetime.strptime(string_time).timetuple())

def get_matrix(row, columns) -> np.matrix:
    if row == 0:
        return np.matrix([])

    if columns == 0:
        return np.matrix([])
    return np.zeros(shape=(row, columns))

from typing import Iterable

try:
    broker_address="localhost"
  
    print("Creating new instance 2")
    client = mqtt.Client("LocalClientTest") #create new instance

    client.on_connect     = on_connect
    client.on_subscribe   = on_subscribe
    client.on_unsubscribe = on_unsubscribe
    client.on_message     = on_message
    client.on_disconnect  = on_disconnect
    #client.on_log        = on_log

    # client.username_pw_set(username='mosquitto',password='mosquitto')

    Settings.initialize_main_list()

    print("connecting to broker: {}".format(broker_address))
    client.connect(broker_address, 1884)

    client.loop_forever()
	
except Exception as ex:
    print('Exception in Main Function: {}'.format(ex))
	
