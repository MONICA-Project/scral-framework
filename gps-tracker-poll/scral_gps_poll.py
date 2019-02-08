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
# ROADMAP: these are main steps in which the module processing is divided.
#
# PHASE: INIT + SETUP + BOOT
#   1. Init variables and setup server and MQTT connections
#   2. Read configuration File and load predefined OGC scheme (exit if integrity not satisfied)
#   3. Load OGC entities
#
# #ToDo: PHASE: DISCOVERY
#   4. Check via discovery if loaded entities are already registered
#   5. Register new entities if needed, otherwise stored corresponding @iot.id's
#
# #ToDo: PHASE: INTEGRATION
#
####################################################################################################
import argparse
import json
import logging
import os
import sys
from queue import Queue
from threading import Semaphore
import paho.mqtt.client as mqtt
import requests

from ogc_configuration import OGCConfiguration
import scral_util
import mqtt_util
from scral_constants import *

# configuration flags
can_run = True
verbose = True

# client MQTT
mqtt_client = None

# the observation messages queue and its semaphore
q = Queue()
que_sem = Semaphore(1)

# SCRAL local catalog
resource_catalog = {}


def main():
    """ Resource manager for integration of the GPS-TRACKER-GW (by usage of LoRa devices). """
    args = parse_command_line()     # parsing command line parameters, it has to be the first instruction
    global verbose                  # overwrite verbose flag from command line
    if args.verbose:
        verbose = True
    else:
        verbose = False

    init_logger()                   # logging initialization, it is suggested to call it after command line parsing

    if not args.connection_file:    # does the connection_file is set?
        logging.critical("Connection file is missing!")
        exit(1)
    if not args.ogc_file:           # does the ogc_file is set?
        logging.critical("OGC configuration file is missing!")
        exit(2)
    pilot_mqtt_topic = mqtt_util.get_mqtt_topic(args.pilot)
    if not pilot_mqtt_topic:
        logging.critical('Wrong pilot name: "' + args.pilot + '"!')
        exit(3)

    logging.debug("Connection file: " + args.connection_file)
    logging.debug("OGC file: " + args.ogc_file)
    logging.debug("MQTT topic: " + pilot_mqtt_topic)

    ogc_server_address = parse_connection_file(args.connection_file)
    ogc_config = OGCConfiguration(args.ogc_file, ogc_server_address)

    if not test_connectivity(ogc_config):
        logging.critical("Network connectivity to "+ogc_server_address+" not available!")
        exit(4)
    discovery(ogc_config)

    runtime(pilot_mqtt_topic)

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
    global broker_ip
    broker_ip = connection_config_file["mqtt"]["broker"]
    global broker_port
    broker_port = connection_config_file["mqtt"]["broker_port"]

    # 2 MQTT Broker Connection ##########
    global mqtt_client
    mqtt_client = mqtt.Client()

    # Map event handlers
    mqtt_client.on_connect = mqtt_util.on_connect
    mqtt_client.on_disconnect = mqtt_util.on_disconnect

    logging.info("Try to connect to broker: %s:%s" % (broker_ip, broker_port))
    mqtt_client.connect(broker_ip, broker_port, mqtt_util.DEFAULT_KEEPALIVE)
    mqtt_client.loop_start()

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
    # LOCATION discovery
    location = ogc_config.get_location()
    logging.info('LOCATION "'+location.get_name()+'" discovery')
    location_id = entity_discovery(location, ogc_config.URL_LOCATIONS, ogc_config.FILTER_NAME)
    logging.debug('Entity Name: "' + location.get_name() + '" with id: ' + str(location_id))
    location.set_id(location_id)  # temporary useless

    # THING discovery
    thing = ogc_config.get_thing()
    thing.set_location_id(location_id)
    logging.info('THING "' + thing.get_name() + '" discovery')
    thing_id = entity_discovery(thing, ogc_config.URL_THINGS, ogc_config.FILTER_NAME)
    logging.debug('Entity Name: "' + thing.get_name() + '" with id: ' + str(thing_id))


def entity_discovery(ogc_entity, url_entity, url_filter):
    # Build URL for LOCATION discovery based on Location name
    ogc_entity_name = ogc_entity.get_name()
    url_entity_discovery = url_entity + url_filter + "'" + ogc_entity_name + "'"

    r = requests.get(url=url_entity_discovery, headers=REST_HEADERS, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
    discovery_result = r.json()['value']

    if not discovery_result or len(discovery_result) == 0:  # if response is empty
        logging.info("Entity not yet registered, registration is starting now!")
        payload = ogc_entity.get_rest_payload()
        r = requests.post(url=url_entity_discovery, data=json.dumps(payload),
                          headers=REST_HEADERS, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
        json_string = r.json()
        if OGC_ID not in json_string:
            raise ValueError("The Entity ID is not defined for: " + ogc_entity_name + "!\n"
                             "Please check the REST request!")

        return json_string[OGC_ID]

    else:
        if not consistency_check(discovery_result, ogc_entity_name, url_filter):
            raise ValueError("Multiple results for same Entity name: "+ogc_entity_name+"!")
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


def runtime(mqtt_topic):
    pass


if __name__ == '__main__':
    # set default string encoding  # reload(sys)
    # sys.setdefaultencoding('utf-8')

    print(BANNER % VERSION)
    sys.stdout.flush()
    main()
