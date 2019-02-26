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

import paho.mqtt.client as mqtt

from .constants import CATALOG_FILENAME, DEFAULT_KEEPALIVE
from . import util
from . import mqtt_util


class SCRALModule(object):

    def __init__(self, connection_file, pub_topic_prefix):
        """ Parses the connection file and stores information about the MQTT broker.

        @:param The path of the connection file
        :return A tuple containing the OGC server address and broker ip/port information
        """

        # 1 Load connection configuration file
        connection_config_file = util.load_from_file(connection_file)

        # 2 Load local resource catalog / TEMPORARY USELESS
        if os.path.exists(CATALOG_FILENAME):
            self._resource_catalog = util.load_from_file(CATALOG_FILENAME)
            logging.info('[PHASE-INIT] Resource Catalog: ', json.dumps(self._resource_catalog))
        else:
            logging.info("No resource catalog available on file.")
            self._resource_catalog = {}

        # 3 Creating an MQTT Publisher
        self._topic_prefix = pub_topic_prefix
        self._pub_broker_address = connection_config_file["mqtt"]["pub_broker"]
        self._pub_broker_port = connection_config_file["mqtt"]["pub_broker_port"]

        self._mqtt_publisher = mqtt.Client()
        self._mqtt_publisher.on_connect = mqtt_util.on_connect
        self._mqtt_publisher.on_disconnect = mqtt_util.automatic_reconnection

        logging.info("Try to connect to broker: %s:%s" % (self._pub_broker_address, self._pub_broker_port))
        logging.debug("Client ID is: "+str(self._mqtt_publisher._client_id))
        self._mqtt_publisher.connect(self._pub_broker_address, self._pub_broker_port, DEFAULT_KEEPALIVE)
        self._mqtt_publisher.loop_start()

    def get_mqtt_connection_address(self):
        return self._pub_broker_address

    def get_mqtt_connection_port(self):
        return self._pub_broker_port

    @abstractmethod
    def runtime(self):
        raise NotImplementedError("Implement runtime method in subclasses")
