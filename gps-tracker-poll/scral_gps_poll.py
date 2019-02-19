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
#
# ROADMAP: these are main steps in which the module is divided.
#
# PHASE: INIT + SETUP + BOOT
#   1. Init variables and setup server and MQTT connections
#   2. Read configuration File and load predefined OGC scheme (exit if integrity not satisfied)
#
# #PHASE: DISCOVERY
#   3. Check via discovery if loaded entities are already registered
#   4. If needed, register new entities to OGC Server
#   5. Retrieve corresponding @iot.id's
#
# #PHASE: INTEGRATION
#   6. Discovery of physical devices through external platform
#   7. Start threads and upload DATASTREAM entities to OGC Server
#   8. Subscribe to MQTT topics, listen to incoming data and publish OBSERVATIONS to OGC Broker
#
# #PHASE: DYNAMIC DISCOVERY
#   9. A thread is detached and continues listening for new devices
#
####################################################################################################
import argparse
import json
import logging
from threading import Thread
from time import sleep

import requests
import sys
import paho.mqtt.client as mqtt
from requests.exceptions import SSLError

from scral_constants import *
import scral_util
import mqtt_util
from ogc_configuration import OGCConfiguration
from scral_ogc import OGCDatastream

# global variables
verbose = True


def main():
    """ Resource manager for integration of the GPS-TRACKER-GW (by usage of LoRa devices). """
    args = parse_command_line()  # parsing command line parameters, it has to be the first instruction
    global verbose  # overwrite verbose flag from command line
    if args.verbose:
        verbose = True
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
        verbose = False

    scral_util.init_logger(logging_level)  # logging initialization

    if not args.connection_file:  # has the connection_file been set?
        logging.critical("Connection file is missing!")
        exit(1)
    if not args.ogc_file:  # has the ogc_file been set?
        logging.critical("OGC configuration file is missing!")
        exit(2)
    pilot_mqtt_topic_prefix = mqtt_util.get_publish_mqtt_topic(args.pilot)  # 'local' is the default configuration value
    if not pilot_mqtt_topic_prefix:
        logging.critical('Wrong pilot name: "' + args.pilot + '"!')
        exit(3)

    logging.debug("Connection file: " + args.connection_file)
    logging.debug("OGC file: " + args.ogc_file)
    logging.debug("MQTT publishing topic prefix: " + pilot_mqtt_topic_prefix)

    ogc_server_address, pub_broker_conn_info = parse_connection_file(args.connection_file)
    if not scral_util.test_connectivity(ogc_server_address, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD):
        logging.critical("Network connectivity to " + ogc_server_address + " not available!")
        exit(4)

    ogc_config = OGCConfiguration(args.ogc_file, ogc_server_address)

    discovery(ogc_config)

    runtime(ogc_config, pub_broker_conn_info[0], pub_broker_conn_info[1], pilot_mqtt_topic_prefix)

    logging.info("That's all folks!\n")


def parse_command_line():
    """ This function parses the command line.
    :return: a dictionary with all the parsed parameters.
    """
    example_text = "example: scral_gps_poll.py -v -f ./my_conf.conf -c external -p hamburg"

    parser = argparse.ArgumentParser(prog='SCRAL GPS Poll', epilog=example_text,
                                     description='Implementation of SCRAL GPS tracker in polling approach',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='enable verbose mode')
    parser.add_argument('-o', '--ogc', dest='ogc_file', type=str, help='the path of the OGC configuration file')
    parser.add_argument('-c', '--conn', dest='connection_file', type=str,  # choices=[0, 1, 2], default=0
                        help='the path of the connection configuration')
    parser.add_argument('-p', '--pilot', default=DEFAULT_CONFIG, type=str, help='the name of the desired pilot')
    args = parser.parse_args()

    return args


def parse_connection_file(connection_file):
    """ Parses the connection file and initialize the MQTT broker.

    @:param The path of the connection file
    :return A tuple containing the OGC server address and broker ip/port information
    """

    # 1 Load connection configuration file
    logging.info("[PHASE-INIT] The connection type is: " + connection_file)
    connection_config_file = scral_util.load_from_file(connection_file)

    # Store broker address/port
    pub_broker_ip = connection_config_file["mqtt"]["pub_broker"]
    pub_broker_port = connection_config_file["mqtt"]["pub_broker_port"]

    # # 2 Load local resource catalog / TEMPORARY USELESS
    # if os.path.exists(CATALOG_FILENAME):
    #     global resource_catalog
    #     resource_catalog = scral_util.load_from_file(CATALOG_FILENAME)
    #     logging.info('[PHASE-INIT] Resource Catalog: ', json.dumps(resource_catalog))
    # else:
    #     logging.info("Resource catalog does not exist, it will be created at integration phase")

    # 3 Return the OGC server addresses
    return connection_config_file["REST"]["ogc_server_address"], (pub_broker_ip, pub_broker_port)


def discovery(ogc_config):
    """ This function uploads the OGC model on the OGC Server and retrieves the @iot.id assigned by the server.
        If entities were already registered, they are not overwritten (or registered twice)
        and only their @iot.id are retrieved.

    :param ogc_config: An object containing all the data about the OGC model.
    :return: It can throw an exception if something wrong.
    """
    # LOCATION discovery
    location = ogc_config.get_location()
    logging.info('LOCATION "' + location.get_name() + '" found')
    location_id = entity_discovery(location, ogc_config.URL_LOCATIONS, ogc_config.FILTER_NAME)
    logging.debug('Location name: "' + location.get_name() + '" with id: ' + str(location_id))
    location.set_id(location_id)  # temporary useless

    # THING discovery
    thing = ogc_config.get_thing()
    thing.set_location_id(location_id)
    logging.info('THING "' + thing.get_name() + '" found')
    thing_id = entity_discovery(thing, ogc_config.URL_THINGS, ogc_config.FILTER_NAME)
    logging.debug('Thing name: "' + thing.get_name() + '" with id: ' + str(thing_id))
    thing.set_id(thing_id)

    # SENSORS discovery
    sensors = ogc_config.get_sensors()
    logging.info("SENSORS discovery")
    for s in sensors:
        sensor_id = entity_discovery(s, ogc_config.URL_SENSORS, ogc_config.FILTER_NAME)
        s.set_id(sensor_id)
        logging.debug('Sensor name: "' + s.get_name() + '" with id: ' + str(sensor_id))

    # PROPERTIES discovery
    properties = ogc_config.get_observed_properties()
    logging.info("OBSERVEDPROPERTIES discovery")
    for op in properties:
        op_id = entity_discovery(op, ogc_config.URL_PROPERTIES, ogc_config.FILTER_NAME)
        op.set_id(op_id)
        logging.debug('OBSERVED PROPERTY: "' + op.get_name() + '" with id: ' + str(op_id))


def entity_discovery(ogc_entity, url_entity, url_filter):
    """ This function uploads an OGC entity on the OGC Server and retrieves its @iot.id assigned by the server.
        If the entity is already registered, it is not overwritten (or registered twice)
        and only its @iot.id is retrieved.

    :param ogc_entity: An object containing the data of the entity.
    :param url_entity: The URL of the request.
    :param url_filter: The filter to apply.
    :return: Returns the @iot.id of the entity if it is correctly registered,
             if something goes wrong during registration, an exception can be generated.
    """
    # Build URL for LOCATION discovery based on Location name
    ogc_entity_name = ogc_entity.get_name()
    url_entity_discovery = url_entity + url_filter + "'" + ogc_entity_name + "'"

    r = requests.get(url=url_entity_discovery, headers=REST_HEADERS, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
    discovery_result = r.json()['value']

    if not discovery_result or len(discovery_result) == 0:  # if response is empty
        logging.info(ogc_entity_name + " not yet registered, registration is starting now!")
        payload = ogc_entity.get_rest_payload()
        r = requests.post(url=url_entity_discovery, data=json.dumps(payload),
                          headers=REST_HEADERS, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
        json_string = r.json()
        if OGC_ID not in json_string:
            raise ValueError("The Entity ID is not defined for: "+ogc_entity_name+"!\nPlease check the REST request!")

        return json_string[OGC_ID]

    else:
        if not scral_util.consistency_check(discovery_result, ogc_entity_name, url_filter, verbose):
            raise ValueError("Multiple results for same Entity name: " + ogc_entity_name + "!")
        else:
            return discovery_result[0][OGC_ID]


def runtime(ogc_config, pub_broker_address, pub_broker_port, pub_topic_prefix):
    """ This function retrieves the THINGS from the Hamburg OGC server and convert them to MONICA OGC DATASTREAMS.
        These DATASTREAMS are published on MONICA OGC server.

    :param ogc_config: An instance of OGCConfiguration, it contains a representation of an OGC Sensor Things model.
    :param pub_broker_address: The address of the MQTT broker on which you want to publish.
    :param pub_broker_port: The port of the MQTT broker
    :param pub_topic_prefix: The prefix of the topic where you want to publish
    """
    res_cat = ogc_datastream_generation(ogc_config)  # res_cat = {}
    mqtt_util.init_connection_manager(pub_broker_address, pub_broker_port, pub_topic_prefix, res_cat)
    mqtt_subscriber = mqtt_listening(ogc_config.get_datastreams())

    th = Thread(target=dynamic_discovery, args=(ogc_config, res_cat, mqtt_subscriber, ))
    th.start()
    mqtt_subscriber.loop_start()
    th.join()


def ogc_datastream_generation(ogc_config, res_cat=None):
    r = None
    try:
        r = requests.get(url=OGC_HAMBURG_THING_URL + OGC_HAMBURG_FILTER, verify="./config/hamburg/hamburg_cert.cer")
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

    property_id = ogc_config.get_observed_properties()[0].get_id()  # Assumption: only an observed property registered
    property_name = ogc_config.get_observed_properties()[0].get_name()

    # global resource_catalog
    if res_cat is None:
        res_cat = {}
    hamburg_devices = r.json()["value"]
    for hd in hamburg_devices:
        iot_id = str(hd[OGC_ID])
        device_id = hd["name"]

        if iot_id in res_cat:
            logging.debug("Device: "+device_id+" already registered with id: "+iot_id)
        else:
            datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + device_id
            description = hd["description"]
            datastream = OGCDatastream(name=datastream_name, description=description, ogc_property_id=property_id,
                                       ogc_sensor_id=sensor_id, ogc_thing_id=thing_id, x=0.0, y=0.0,
                                       unit_of_measurement=HAMBURG_UNIT_OF_MEASURE)
            datastream_id = entity_discovery(datastream, ogc_config.URL_DATASTREAMS, ogc_config.FILTER_NAME)

            datastream.set_id(datastream_id)
            datastream.set_mqtt_topic(THINGS_SUBSCRIBE_TOPIC + "(" + iot_id + ")/Locations")
            ogc_config.add_datastream(datastream)

            res_cat[iot_id] = datastream_id  # Store Hamburg to MONICA coupled information

    return res_cat


def mqtt_listening(datastreams):
    """ This function listens on MQTT topics of Hamburg Broker and forward them to the MONICA MQTT Broker.

    :param datastreams: A Dictionary of OGCDatastream
    """
    mqtt_subscriber = mqtt.Client(BROKER_HAMBURG_CLIENT_ID)

    # Map event handlers
    mqtt_subscriber.on_connect = mqtt_util.on_connect
    mqtt_subscriber.on_disconnect = mqtt_util.on_disconnect
    mqtt_subscriber.on_message = mqtt_util.on_message_received

    logging.info("Try to connect to broker: %s:%s" % (BROKER_HAMBURG_ADDRESS, BROKER_DEFAULT_PORT))
    mqtt_subscriber.connect(BROKER_HAMBURG_ADDRESS, BROKER_DEFAULT_PORT, DEFAULT_KEEPALIVE)

    # Get the listening topics and run the subscriptions
    for ds in datastreams.values():
        top = ds.get_mqtt_topic()
        logging.debug("Subscribing to MQTT topic: " + top)
        mqtt_subscriber.subscribe(top, DEFAULT_MQTT_QOS)

    return mqtt_subscriber


def dynamic_discovery(ogc_config, res_cat, mqtt_subscriber):
    hours = 8
    catalog = res_cat
    while True:
        sleep(60*60*hours)
        logging.debug("Good morning!")
        catalog = ogc_datastream_generation(ogc_config, catalog)

        # Get the listening topics and run the subscriptions
        for ds in ogc_config.get_datastreams().values():
            top = ds.get_mqtt_topic()
            logging.debug("(Re)subscribing to MQTT topic: " + top)
            mqtt_subscriber.subscribe(top, DEFAULT_MQTT_QOS)


if __name__ == '__main__':
    print(BANNER % VERSION)
    sys.stdout.flush()
    main()
