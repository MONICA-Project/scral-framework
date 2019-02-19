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
# ROADMAP: these are main steps in which a SCRAL module is divided.
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
# #ToDo: INTEGRATION
#   6. Discovery of physical devices through external platform
#   7. Start threads and upload DATASTREAM entities to OGC Server
#   8. Subscribe to MQTT topics, listen to incoming data and publish OBSERVATIONS to OGC Broker
#
# #ToDO: DYNAMIC DISCOVERY (could be integrated)
#
####################################################################################################
import argparse
import logging
import sys

import scral_util
import mqtt_util
from ogc_configuration import OGCConfiguration
from scral_constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, BANNER, VERSION, DEFAULT_CONFIG
from scral_gps_poll_module import SCRALGPSPoll

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

    logging.info("[PHASE-INIT] The connection file is: " + args.connection_file)
    logging.debug("OGC file: " + args.ogc_file)
    logging.debug("MQTT publishing topic prefix: " + pilot_mqtt_topic_prefix)

    module = SCRALGPSPoll(args.connection_file)

    # 3 Storing the OGC server addresses
    connection_config_file = scral_util.load_from_file(args.connection_file)
    ogc_server_address = connection_config_file["REST"]["ogc_server_address"]

    if not scral_util.test_connectivity(ogc_server_address, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD):
        logging.critical("Network connectivity to " + ogc_server_address + " not available!")
        exit(4)

    ogc_config = OGCConfiguration(args.ogc_file, ogc_server_address)
    ogc_config.discovery(verbose)

    module.runtime(ogc_config, pilot_mqtt_topic_prefix)

    logging.info("That's all folks!\n")


def parse_command_line():
    """ This function parses the command line.
    :return: a dictionary with all the parsed parameters.
    """
    example_text = "example: start_gps_poll.py -v -f ./my_conf.conf -c external -p hamburg"

    parser = argparse.ArgumentParser(prog='SCRAL', epilog=example_text,
                                     description='... to be decided ...',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='enable verbose mode')
    parser.add_argument('-o', '--ogc', dest='ogc_file', type=str, help='the path of the OGC configuration file')
    parser.add_argument('-c', '--conn', dest='connection_file', type=str,  # choices=[0, 1, 2], default=0
                        help='the path of the connection configuration')
    parser.add_argument('-p', '--pilot', default=DEFAULT_CONFIG, type=str, help='the name of the desired pilot')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    print(BANNER % VERSION)
    sys.stdout.flush()
    main()
