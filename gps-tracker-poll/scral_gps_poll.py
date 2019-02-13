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
# #ToDo: PHASE: INTEGRATION
#   6. Discovery of physical devices through external platform
#   7. Start threads and upload DATASTREAM entities to OGC Server
#   8. Subscribe to MQTT topics, listen to incoming data and publish OBSERVATIONS to OGC Broker
#
####################################################################################################
import argparse
import json
import logging
import os

import requests
import sys
import paho.mqtt.client as mqtt
from requests.exceptions import SSLError

from ogc_configuration import OGCConfiguration
from scral_ogc import OGCDatastream
import scral_util
import mqtt_util
from scral_constants import *


def main():
    """ Resource manager for integration of the GPS-TRACKER-GW (by usage of LoRa devices). """
    args = parse_command_line()  # parsing command line parameters, it has to be the first instruction
    global verbose  # overwrite verbose flag from command line
    if args.verbose:
        verbose = True
    else:
        verbose = False

    init_logger()  # logging initialization, it is suggested to call it after command line parsing

    if not args.connection_file:  # does the connection_file is set?
        logging.critical("Connection file is missing!")
        exit(1)
    if not args.ogc_file:  # does the ogc_file is set?
        logging.critical("OGC configuration file is missing!")
        exit(2)
    pilot_mqtt_topic = mqtt_util.get_publish_mqtt_topic(args.pilot)
    if not pilot_mqtt_topic:
        logging.critical('Wrong pilot name: "' + args.pilot + '"!')
        exit(3)

    logging.debug("Connection file: " + args.connection_file)
    logging.debug("OGC file: " + args.ogc_file)
    logging.debug("MQTT publishing topic: " + pilot_mqtt_topic)

    ogc_server_address = parse_connection_file(args.connection_file)
    ogc_config = OGCConfiguration(args.ogc_file, ogc_server_address)

    if not test_connectivity(ogc_config):
        logging.critical("Network connectivity to " + ogc_server_address + " not available!")
        exit(4)
    discovery(ogc_config)

    runtime(ogc_config)

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


def init_logger():
    """ This function configure the logger according to verbose flag. """
    logging.basicConfig(format="%(message)s")
    if verbose:
        logging.getLogger().setLevel(level=logging.DEBUG)
    else:
        logging.getLogger().setLevel(level=logging.INFO)
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)04d %(levelname)s: %(message)s", datefmt="%H:%M:%S"))


def parse_connection_file(connection_file):
    """ Parses the connection file and initialize the MQTT broker. """

    # 1 Load connection configuration file ##########
    logging.info("[PHASE-INIT] The connection type is: " + connection_file)
    connection_config_file = scral_util.load_from_file(connection_file)

    # Store broker address/port
    # global broker_ip
    broker_ip = connection_config_file["mqtt"]["broker"]
    # global broker_port
    broker_port = connection_config_file["mqtt"]["broker_port"]

    # 2 MQTT Broker Connection ##########
    global mqtt_publisher
    mqtt_publisher = mqtt.Client()

    # Map event handlers
    mqtt_publisher.on_connect = mqtt_util.on_connect
    mqtt_publisher.on_disconnect = mqtt_util.on_disconnect

    logging.info("Try to connect to broker: %s:%s" % (broker_ip, broker_port))
    mqtt_publisher.connect(broker_ip, broker_port, mqtt_util.DEFAULT_KEEPALIVE)
    mqtt_publisher.loop_start()

    # 3 Load local resource catalog ##########
    if os.path.exists(CATALOG_FILENAME):
        global resource_catalog
        resource_catalog = scral_util.load_from_file(CATALOG_FILENAME)
        logging.info('[PHASE-INIT] Resource Catalog: ', json.dumps(resource_catalog))
    else:
        logging.info("Resource catalog does not exist, it will be created at integration phase")

    # 4 Return the OGC server addresses ##########
    return connection_config_file["REST"]["ogc_server_address"]


def test_connectivity(ogc_config):
    """ This function checks if the connection is correctly configured.

    :param ogc_config: An object containing all the data about the OGC model.
    :return: True, if it is possible to establish a connection, False otherwise.
    """
    try:
        r = requests.get(url=ogc_config.URL_RESOURCES, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
        if r.ok:
            logging.info("Network connectivity: VERIFIED")
            return True
        else:
            logging.info("Something wrong during connection!")
            return False

    except Exception as e:
        logging.debug(e)
        return False


def discovery(ogc_config):
    """ This function uploads the OGC model on the OGC Server and retrieves the @iot.id assigned by the server.
        If entities were already registered, they are not overwritten (or registered twice)
        and only their @iot.id are retrieved.

    :param ogc_config: An object containing all the data about the OGC model.
    :return: It can throw an exception if something wrong.
    """
    # LOCATION discovery
    location = ogc_config.get_location()
    logging.info('LOCATION "' + location.get_name() + '" discovery')
    location_id = entity_discovery(location, ogc_config.URL_LOCATIONS, ogc_config.FILTER_NAME)
    logging.debug('Location name: "' + location.get_name() + '" with id: ' + str(location_id))
    location.set_id(location_id)  # temporary useless

    # THING discovery
    thing = ogc_config.get_thing()
    thing.set_location_id(location_id)
    logging.info('THING "' + thing.get_name() + '" discovery')
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
        If the entity was already registered, it is not overwritten (or registered twice)
        and only its @iot.id is retrieved.

    :param ogc_entity: An object containing the data of the entity.
    :param url_entity: The URL of the request.
    :param url_filter: The filter to apply.
    :return: Returns the @iot.id of the entity if it is correctly registered,
             if something wrong during registration or id retrieving can throw an exception.
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
        if not consistency_check(discovery_result, ogc_entity_name, url_filter):
            raise ValueError("Multiple results for same Entity name: " + ogc_entity_name + "!")
        else:
            return discovery_result[0][OGC_ID]


def consistency_check(discovery_result, name, filter_name):
    """ This function checks if an OGC entity is already registered. """

    if len(discovery_result) > 1:
        logging.error("Duplicate found: please verigy OGC-naming!")
        logging.info("Current Filter: " + filter_name + "'" + name + "'")
        if verbose:
            z = 0
            while z < len(discovery_result):
                logging.debug(discovery_result[z])
                z += 1
        return False

    return True


def runtime(ogc_config):
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

    thing = ogc_config.get_thing()
    thing_id = thing.get_id()
    thing_name = thing.get_name()

    sensor = ogc_config.get_sensors()[0]  # it is supposed that only one type of sensor was loaded
    sensor_id = sensor.get_id()
    sensor_name = sensor.get_name()

    property_id = ogc_config.get_observed_properties()[0].get_id()
    property_name = ogc_config.get_observed_properties()[0].get_name()

    global resource_catalog
    hamburg_devices = r.json()["value"]
    for hd in hamburg_devices:
        iot_id = str(hd[OGC_ID])
        device_id = hd["name"]
        description = hd["description"]

        datastream_name = thing_name+"/"+sensor_name+"/"+property_name+"/"+device_id

        datastream = OGCDatastream(name=datastream_name, description=description, ogc_property_id=property_id,
                                   ogc_sensor_id=sensor_id, ogc_thing_id=thing_id, x=0.0, y=0.0,
                                   unit_of_measurement=HAMBURG_UNIT_OF_MEASURE)
        datastream_id = entity_discovery(datastream, ogc_config.URL_DATASTREAMS, ogc_config.FILTER_NAME)
        datastream.set_id(datastream_id)
        datastream.set_mqtt_topic(THINGS_SUBSCRIBE_TOPIC+"("+iot_id+")/Locations")
        ogc_config.add_datastream(datastream)

        resource_catalog[iot_id] = datastream_id

    mqtt_listening(ogc_config.get_datastreams())


def mqtt_listening(datastreams):
    mqtt_subscriber = mqtt.Client(BROKER_HAMBURG_CLIENT_ID)

    # Map event handlers
    mqtt_subscriber.on_connect = mqtt_util.on_connect
    mqtt_subscriber.on_disconnect = mqtt_util.on_disconnect
    mqtt_subscriber.on_message = mqtt_util.on_message_received

    logging.info("Try to connect to broker: %s:%s" % (BROKER_HAMBURG_ADDRESS, BROKER_DEFAULT_PORT))
    mqtt_subscriber.connect(BROKER_HAMBURG_ADDRESS, BROKER_DEFAULT_PORT,
                            DEFAULT_KEEPALIVE)

    for ds in datastreams:
        top = ds.get_mqtt_topic()
        logging.debug("Subscribing to MQTT topic: " + top)
        mqtt_subscriber.subscribe(top, DEFAULT_MQTT_QOS)

    mqtt_subscriber.loop_forever()


if __name__ == '__main__':
    print(BANNER % VERSION)
    sys.stdout.flush()
    main()
