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

""" This object will contains the publishing MQTT Client and the resource catalog. """
connection_manager = None


class _MQTTConnectionManager:
    """ This class manage an MQTT Publisher with the associated resource catalog. """

    def __init__(self, address, port, keepalive, resource_catalog):
        """ Initialize the MQTTConnectionManager

        :param address: The IP address (or alias) of the MQTT Broker on which the messages will be published.
        :param port: The port of the MQTT Broker
        :param keepalive: The keepalive value used to establish the connection to the broker
        :param resource_catalog: A dictionary containing the mapping between the Hamburg THING @iot.id and
            the MONICA DATASTREAM @iot.id
        """
        self._mqtt_publisher = mqtt.Client()

        # Map event handlers
        self._mqtt_publisher.on_connect = on_connect
        self._mqtt_publisher.on_disconnect = on_disconnect
        self._mqtt_publisher.on_message = on_message_received

        logging.info("Try to connect to broker: %s:%s" % (address, port))
        self._mqtt_publisher.connect(address, port, keepalive)
        self._mqtt_publisher.loop_start()

        self._resource_catalog = resource_catalog

    def get_resource_catalog(self):
        return self._resource_catalog

    def get_mqtt_publisher(self):
        return self._mqtt_publisher


def init_connection_manager(address, port, resource_catalog):
    """ This function should be called to initialize the connection_manager. """
    global connection_manager
    connection_manager = _MQTTConnectionManager(address, port, DEFAULT_KEEPALIVE, resource_catalog)


def on_message_received(client, userdata, msg):
    logging.debug(msg.topic+": "+str(msg.payload))
    observation_result = json.loads(msg.payload)["location"]["geometry"]
    observation_timestamp = str(arrow.utcnow())
    thing_id = str(msg.topic.split('(')[1].split(')')[0])

    catalog = connection_manager.get_resource_catalog()
    datastream_id = catalog[thing_id]
    topic = "GOST/Datastreams("+str(datastream_id)+")/Observations"
    logging.debug("On topic '"+topic+"' will be send: "+ str(observation_result))

    ogc_observation = OGCObservation(datastream_id, observation_timestamp, observation_result, observation_timestamp)
    ogc_obs_dict = ogc_observation.get_rest_payload()
    payload = json.dumps(dict(ogc_obs_dict))
    publisher = connection_manager.get_mqtt_publisher()
    publisher.publish(topic, payload, DEFAULT_MQTT_QOS)


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
