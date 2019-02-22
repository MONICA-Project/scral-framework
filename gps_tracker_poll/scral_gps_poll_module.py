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
from threading import Thread
from time import sleep
from typing import Dict

import requests
import paho.mqtt.client as mqtt
import arrow

from requests.exceptions import SSLError

from scral_ogc import OGCDatastream, OGCObservation

from scral_module.ogc_configuration import OGCConfiguration
from scral_module.scral_constants import BROKER_DEFAULT_PORT, DEFAULT_KEEPALIVE, OGC_ID, DEFAULT_MQTT_QOS
from scral_module import mqtt_util
from scral_module.scral_module import SCRALModule

from hamburg_constants import BROKER_HAMBURG_ADDRESS, BROKER_HAMBURG_CLIENT_ID, OGC_HAMBURG_THING_URL, \
                              OGC_HAMBURG_FILTER, HAMBURG_UNIT_OF_MEASURE, THINGS_SUBSCRIBE_TOPIC


class SCRALGPSPoll(SCRALModule):
    """ Resource manager for integration of the GPS-TRACKER-GW (by usage of LoRa devices). """

    _resource_catalog: Dict[str, int]

    def __init__(self, connection_file, pub_topic_prefix):
        """ Initialize MQTT Brokers for listening and publishing

        :param connection_file: A file containing connection information.
        :param pub_topic_prefix: The MQTT topic prefix on which information will be published.
        """

        super().__init__(connection_file)

        # Creating an MQTT Subscriber
        self._mqtt_subscriber = mqtt.Client(BROKER_HAMBURG_CLIENT_ID)
        self._mqtt_subscriber.on_connect = mqtt_util.on_connect
        self._mqtt_subscriber.on_disconnect = mqtt_util.automatic_reconnection
        self._mqtt_subscriber.on_message = self.on_message_received

        logging.info("Try to connect to broker: %s:%s" % (BROKER_HAMBURG_ADDRESS, BROKER_DEFAULT_PORT))
        self._mqtt_subscriber.connect(BROKER_HAMBURG_ADDRESS, BROKER_DEFAULT_PORT, DEFAULT_KEEPALIVE)

        # Creating an MQTT Publisher
        self._mqtt_publisher = mqtt.Client()
        self._mqtt_publisher.on_connect = mqtt_util.on_connect
        self._mqtt_publisher.on_disconnect = mqtt_util.automatic_reconnection

        logging.info("Try to connect to broker: %s:%s" % (self._pub_broker_ip, self._pub_broker_port))
        self._mqtt_publisher.connect(self._pub_broker_ip, self._pub_broker_port, DEFAULT_KEEPALIVE)
        self._mqtt_publisher.loop_start()

        self._topic_prefix = pub_topic_prefix

    # noinspection PyMethodOverriding
    def runtime(self, ogc_config: OGCConfiguration, pub_topic_prefix: str, dynamic_discovery=True):
        """ This method retrieves the THINGS from the Hamburg OGC server and convert them to MONICA OGC DATASTREAMS.
            These DATASTREAMS are published on MONICA OGC server.
            This is a "locking function"

        :param ogc_config: An instance of OGCConfiguration, it contains a representation of an OGC Sensor Things model.
        :param pub_topic_prefix: The prefix of the topic where you want to publish
        :param dynamic_discovery:  A boolean value that enable the dynamic discovery of new hamburg sensors
        """
        self.ogc_datastream_generation(ogc_config)
        self.update_mqtt_subscription(ogc_config.get_datastreams())

        if dynamic_discovery:
            th = Thread(target=self.dynamic_discovery, args=(ogc_config, ))
            th.start()
            self._mqtt_subscriber.loop_start()
            th.join()
        else:
            self._mqtt_subscriber.loop_forever()

    def ogc_datastream_generation(self, ogc_config):
        r = None
        try:
            r = requests.get(url=OGC_HAMBURG_THING_URL + OGC_HAMBURG_FILTER,
                             verify="./gps_tracker_poll/config/hamburg/hamburg_cert.cer")
        except SSLError as tls_exception:
            logging.error("Error during TLS connection, the connection could be insecure or "
                          "the certificate could be self-signed...\n" + str(tls_exception))
        except Exception as ex:
            logging.error(ex)

        if r is None or not r.ok:
            raise ConnectionError("Connection status: " + str(r.status_code) + "\nImpossible to establish a connection" +
                                  " or resources not found on: " + OGC_HAMBURG_THING_URL)
        else:
            logging.debug("Connection status: " + str(r.status_code))

        # Collect OGC information needed to build DATASTREAMs payload
        thing = ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor = ogc_config.get_sensors()[0]  # Assumption: only "GPS" Sensor is defined for this adapter
        sensor_id = sensor.get_id()
        sensor_name = sensor.get_name()

        property_id = ogc_config.get_observed_properties()[0].get_id()  # Assumpt.: only 1 observed property registered
        property_name = ogc_config.get_observed_properties()[0].get_name()

        # global resource_catalog
        if self._resource_catalog is None:
            self._resource_catalog = {}
        hamburg_devices = r.json()["value"]
        for hd in hamburg_devices:
            iot_id = str(hd[OGC_ID])
            device_id = hd["name"]

            if iot_id in self._resource_catalog:
                logging.debug("Device: "+device_id+" already registered with id: "+iot_id)
            else:
                datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + device_id
                description = hd["description"]
                datastream = OGCDatastream(name=datastream_name, description=description, ogc_property_id=property_id,
                                           ogc_sensor_id=sensor_id, ogc_thing_id=thing_id, x=0.0, y=0.0,
                                           unit_of_measurement=HAMBURG_UNIT_OF_MEASURE)
                datastream_id = ogc_config.entity_discovery(
                                    datastream, ogc_config.URL_DATASTREAMS, ogc_config.FILTER_NAME)

                datastream.set_id(datastream_id)
                datastream.set_mqtt_topic(THINGS_SUBSCRIBE_TOPIC + "(" + iot_id + ")/Locations")
                ogc_config.add_datastream(datastream)

                self._resource_catalog[iot_id] = datastream_id  # Store Hamburg to MONICA coupled information

    def update_mqtt_subscription(self, datastreams):
        """ This method updates the lists of MQTT subscription topics.

        :param datastreams: A Dictionary of OGCDatastream
        """
        # Get the listening topics and run the subscriptions
        for ds in datastreams.values():
            top = ds.get_mqtt_topic()
            logging.debug("Subscribing to MQTT topic: " + top)
            self._mqtt_subscriber.subscribe(top, DEFAULT_MQTT_QOS)

    def dynamic_discovery(self, ogc_config):
        time_to_wait = 60*60*8  # hours
        while True:
            sleep(time_to_wait)
            logging.debug("Starting Dynamic Discovery!")
            self.ogc_datastream_generation(ogc_config)
            self.update_mqtt_subscription(ogc_config.get_datastreams())

    def on_message_received(self, client, userdata, msg):
        logging.debug(msg.topic + ": " + str(msg.payload))
        observation_result = json.loads(msg.payload)["location"]["geometry"]  # Load the received message
        observation_timestamp = str(arrow.utcnow())
        thing_id = str(msg.topic.split('(')[1].split(')')[0])  # Get the thing_id associated to the physical device

        catalog = self._resource_catalog
        datastream_id = catalog[thing_id]  # Get the datastream_id from the resource catalog
        # topic = "GOST/Datastreams("+str(datastream_id)+")/Observations"
        topic_prefix = self._topic_prefix
        topic = topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # Create OGC Observation and publish
        ogc_observation = OGCObservation(datastream_id, observation_timestamp, observation_result,
                                         observation_timestamp)
        observation_payload = json.dumps(dict(ogc_observation.get_rest_payload()))
        logging.debug(
            "\nOn topic '" + topic + "' will be send the following Observation payload:\n" + str(observation_payload))
        publisher = self._mqtt_publisher
        publisher.publish(topic, observation_payload, DEFAULT_MQTT_QOS)
