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
import arrow as arrow

from scral_constants import resource_catalog, mqtt_publisher, DEFAULT_MQTT_QOS
from scral_ogc import OGCObservation


def on_connect(mqttc, userdata, flags, rc):
    if rc != 0:
        logging.critical("Connection failed, error code: "+str(rc))
    else:
        logging.info("Connection with MQTT broker successfully established|")


def on_disconnect(client, userdata, rc):
    time.sleep(10)
    logging.info("Broker connection lost! Try to re-connecting to " + str(client._host) + "...")
    client.reconnect()


def on_message_received(client, userdata, msg):
    # global resource_catalog
    # global mqtt_publisher

    logging.debug(msg.topic+": "+str(msg.payload))
    observation_result = json.loads(msg.payload)["location"]["geometry"]
    logging.debug("Data to be sent: " + str(observation_result))
    observation_timestamp = arrow.utcnow()
    thing_id = str(msg.topic.split('(')[1].split(')')[0])
    logging.debug(thing_id)
    datastream_id = resource_catalog[thing_id]
    ogc_observation = OGCObservation(datastream_id, observation_timestamp, observation_result, observation_timestamp)
    mqtt_publisher.publish("GOST/Datastreams("+str(datastream_id)+")/Observations", ogc_observation, DEFAULT_MQTT_QOS)


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
