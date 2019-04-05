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

import requests
import paho.mqtt.client as mqtt
import arrow

from requests.exceptions import SSLError

from scral_ogc import OGCDatastream, OGCObservation

from scral_module.constants import BROKER_DEFAULT_PORT, DEFAULT_KEEPALIVE, OGC_ID_KEY, DEFAULT_MQTT_QOS
from scral_module import mqtt_util
from scral_module import util
from scral_module.scral_module import SCRALModule

from gps_tracker_poll.hamburg_constants import BROKER_HAMBURG_ADDRESS, BROKER_HAMBURG_CLIENT_ID, OGC_HAMBURG_THING_URL, \
    OGC_HAMBURG_FILTER, HAMBURG_UNIT_OF_MEASURE, THINGS_SUBSCRIBE_TOPIC, DATASTREAM_ID_KEY, DEVICE_ID_KEY


class SCRALGPSPoll(SCRALModule):
    """ Resource manager for integration of the GPS-TRACKER-GW (by usage of LoRa devices). """

    def __init__(self, ogc_config, connection_file, pilot):
        """ Initialize MQTT Brokers for listening and publishing

        :param connection_file: A file containing connection information.
        :param pilot: The pilot name,
                      it will be used for generate the MQTT topic prefix on which information will be published.
        """

        super().__init__(ogc_config, connection_file, pilot)

        # Creating an MQTT Subscriber
        self._mqtt_subscriber = mqtt.Client(BROKER_HAMBURG_CLIENT_ID)
        self._mqtt_subscriber.on_connect = mqtt_util.on_connect
        self._mqtt_subscriber.on_disconnect = mqtt_util.automatic_reconnection
        self._mqtt_subscriber.on_message = self.on_message_received

        logging.info("Try to connect to broker: %s:%s for listening" % (BROKER_HAMBURG_ADDRESS, BROKER_DEFAULT_PORT))
        logging.debug("Client id is: '" + BROKER_HAMBURG_CLIENT_ID + "'")
        self._mqtt_subscriber.connect(BROKER_HAMBURG_ADDRESS, BROKER_DEFAULT_PORT, DEFAULT_KEEPALIVE)

    # noinspection PyMethodOverriding
    def runtime(self, dynamic_discovery=True):
        """ This method retrieves the THINGS from the Hamburg OGC server and convert them to MONICA OGC DATASTREAMS.
            These DATASTREAMS are published on MONICA OGC server.
            This is a "blocking function".

        :param dynamic_discovery:  A boolean value that enable the dynamic discovery of new hamburg sensors
        """
        self.ogc_datastream_registration()
        self.update_mqtt_subscription(self._ogc_config.get_datastreams())

        if dynamic_discovery:
            th = Thread(target=self.dynamic_discovery)
            th.start()
            self._mqtt_subscriber.loop_start()
            th.join()
        else:
            self._mqtt_subscriber.loop_forever()

    def ogc_datastream_registration(self):
        """ This method registers new DATASTREAMs in the OGC model. """
        r = None
        try:
            r = requests.get(url=OGC_HAMBURG_THING_URL + OGC_HAMBURG_FILTER)
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
        thing = self._ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor = self._ogc_config.get_sensors()[0]  # Assumption: only "GPS" Sensor is defined for this adapter
        sensor_id = sensor.get_id()
        sensor_name = sensor.get_name()

        # Assumption: only 1 observed property registered
        property_id = self._ogc_config.get_observed_properties()[0].get_id()
        property_name = self._ogc_config.get_observed_properties()[0].get_name()

        # global resource_catalog
        hamburg_devices = r.json()["value"]
        for hd in hamburg_devices:
            iot_id = str(hd[OGC_ID_KEY])
            device_id = hd["name"]

            if iot_id in self._resource_catalog:
                logging.debug("Device: "+device_id+" already registered with id: "+iot_id)
            else:
                datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + device_id
                description = hd["description"]
                datastream = OGCDatastream(name=datastream_name, description=description, ogc_property_id=property_id,
                                           ogc_sensor_id=sensor_id, ogc_thing_id=thing_id, x=0.0, y=0.0,
                                           unit_of_measurement=util.build_ogc_unit_of_measure(HAMBURG_UNIT_OF_MEASURE))
                datastream_id = self._ogc_config.entity_discovery(
                                    datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)

                if not datastream_id:
                    logging.critical("No DATASTREAM ID for: "+datastream_name)
                else:
                    datastream.set_id(datastream_id)
                    datastream.set_mqtt_topic(THINGS_SUBSCRIBE_TOPIC + "(" + iot_id + ")/Locations")
                    self._ogc_config.add_datastream(datastream)

                    self._resource_catalog[iot_id] = {
                        DATASTREAM_ID_KEY: datastream_id,
                        DEVICE_ID_KEY: device_id
                    }  # Associating HAMBURG THING id to MONICA DATASTREAM id (plus HAMBURG device_id)
                    self.update_file_catalog()

    def update_mqtt_subscription(self, datastreams):
        """ This method updates the lists of MQTT subscription topics.

        :param datastreams: A Dictionary of OGCDatastream
        """
        # Get the listening topics and run the subscriptions
        for ds in datastreams.values():
            top = ds.get_mqtt_topic()
            logging.debug("Subscribing to MQTT topic: " + top)
            self._mqtt_subscriber.subscribe(top, DEFAULT_MQTT_QOS)

    def dynamic_discovery(self):
        """ This method implements the dynamic discovery.
            This is a 'blocking function'.
        """
        time_to_wait = 60*60*8  # hours
        while True:
            sleep(time_to_wait)
            logging.debug("Starting Dynamic Discovery!")
            self.ogc_datastream_registration()
            self.update_mqtt_subscription(self._ogc_config.get_datastreams())

    def on_message_received(self, client, userdata, msg):
        logging.debug("\nOn topic: "+msg.topic + " - message received:\n" + str(msg.payload))
        observation_time = str(arrow.utcnow())
        thing_id = str(msg.topic.split('(')[1].split(')')[0])  # Get the thing_id associated to the physical device

        datastream_id = self._resource_catalog[thing_id][DATASTREAM_ID_KEY]
        device_id = self._resource_catalog[thing_id][DEVICE_ID_KEY]
        topic_prefix = self._topic_prefix
        topic = topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # OBSERVATION result
        hamburg_obs_result = json.loads(msg.payload)["location"]["geometry"]  # Load the received message
        observation_result = {
            "tagId": device_id,
            "lon": hamburg_obs_result["coordinates"][0],
            "lat": hamburg_obs_result["coordinates"][1]
        }

        # Create OGC Observation and publish
        ogc_observation = OGCObservation(datastream_id, observation_time, observation_result, observation_time)
        observation_payload = json.dumps(dict(ogc_observation.get_rest_payload()))
        ok = self.mqtt_publish(topic, observation_payload)
        if not ok:
            logging.error("Impossible to send MQTT message")
