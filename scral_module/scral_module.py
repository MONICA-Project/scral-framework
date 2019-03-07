#############################################################################
#      _____ __________  ___    __                                          #
#     / ___// ____/ __ \/   |  / /                                          #
#     \__ \/ /   / /_/ / /| | / /                                           #
#    ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Adaptation Layer  #
#   /____/\____/_/ |_/_/  |_/_____/   v.2.0 - enhanced by Python 3          #
#                                                                           #
# LINKS Foundation, (c) 2019                                                #
# developed by Jacopo Foglietti & Luca Mannella                             #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md     #
#                                                                           #
#############################################################################

import json
import logging
import os
from abc import abstractmethod
from typing import Dict

import paho.mqtt.client as mqtt

from .constants import CATALOG_FILENAME, DEFAULT_KEEPALIVE, DEFAULT_MQTT_QOS
from . import util
from . import mqtt_util


class SCRALModule(object):
    """ This class is the base entity of SCRAL framework.
        When you want to develop a new SCRAL module, you have to extend this class, extend (if necessary) the __init__
        initializer and to implement the runtime method (that actually does not have a default implementation.
    """

    _resource_catalog: Dict[str, int]

    def __init__(self, ogc_config: object, connection_file: object, pub_topic_prefix: object) -> object:
        """ Parses the connection file, instantiate an MQTT Client and stores all relevant connection information.

        :param ogc_config: An instance of an OGCConfiguration.
        :param connection_file: The path of the connection file, it has to contain the address of the MQTT broker.
        :param pub_topic_prefix: The prefix of the MQTT topic used to publish information.
        """
        # 1 Storing the OGC configuration
        self._ogc_config = ogc_config
        # 2 Load connection configuration file
        connection_config_file = util.load_from_file(connection_file)

        # 3 Load local resource catalog / TEMPORARY USELESS
        if os.path.exists(CATALOG_FILENAME):
            self._resource_catalog = util.load_from_file(CATALOG_FILENAME)
            logging.info('[PHASE-INIT] Resource Catalog: ', json.dumps(self._resource_catalog))
        else:
            logging.info("No resource catalog available on file.")
            self._resource_catalog = {}

        # 4 Creating an MQTT Publisher
        self._topic_prefix = pub_topic_prefix
        self._pub_broker_address = connection_config_file["mqtt"]["pub_broker"]
        self._pub_broker_port = connection_config_file["mqtt"]["pub_broker_port"]

        self._mqtt_publisher = mqtt.Client()
        self._mqtt_publisher.on_connect = mqtt_util.on_connect
        self._mqtt_publisher.on_disconnect = mqtt_util.automatic_reconnection

        logging.info("Try to connect to broker: %s:%s for publishing" % (self._pub_broker_address, self._pub_broker_port))
        logging.debug("Client ID is: "+str(self._mqtt_publisher._client_id))
        self._mqtt_publisher.connect(self._pub_broker_address, self._pub_broker_port, DEFAULT_KEEPALIVE)
        self._mqtt_publisher.loop_start()

    def get_mqtt_connection_address(self):
        return self._pub_broker_address

    def get_mqtt_connection_port(self):
        return self._pub_broker_port

    def get_ogc_config(self):
        return self._ogc_config

    def get_resource_catalog(self):
        return self._resource_catalog

    def get_topic_prefix(self):
        return self._topic_prefix

    def mqtt_publish(self, topic, payload, qos=DEFAULT_MQTT_QOS):
        """ Publish the payload given as parameter to the MQTT publisher

        :param topic: The MQTT topic on which the client will publish the message.
        :param payload: Data to send (according to Paho documentation could be: None, str, bytearray, int or float).
        :param qos: The desired quality of service (it has an hardcoded default value).
        """
        logging.debug("\nOn topic '"+topic+"' will be send the following payload:\n"+str(payload))
        self._mqtt_publisher.publish(topic, payload, qos)

    @abstractmethod
    def runtime(self):
        """ This is an abstract method that has to be overwritten.
            It manages the runtime operation of the module.
        """
        raise NotImplementedError("Implement runtime method in subclasses")
