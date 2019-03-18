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
# #PHASE: INTEGRATION
#   6. Discovery of physical devices through external platform
#   7. Upload DATASTREAM entities to OGC Server
#   8. Subscribe to MQTT topics, listen to incoming data and publish OBSERVATIONS to OGC Broker
#
# #PHASE: DYNAMIC DISCOVERY
#
####################################################################################################
import argparse
import logging
import signal
import sys

from scral_module import util
from scral_module import mqtt_util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE
from scral_module.ogc_configuration import OGCConfiguration
from scral_module import BANNER, VERSION

from gps_tracker_poll.gps_poll_module import SCRALGPSPoll

verbose = False


def main():
    # parsing command line parameters, it has to be the first instruction
    args = util.parse_command_line("GPS Tracker Polling instance")

    global verbose  # overwrite verbose flag from command line
    if args.verbose:
        verbose = True
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
        verbose = False

    util.init_logger(logging_level)  # logging initialization

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

    # Storing the OGC server addresses
    connection_config_file = util.load_from_file(args.connection_file)
    ogc_server_address = connection_config_file["REST"]["ogc_server_address"]

    if not util.test_connectivity(ogc_server_address, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD):
        logging.critical("Network connectivity to " + ogc_server_address + " not available!")
        exit(4)

    # OGC model configuration and discovery
    ogc_config = OGCConfiguration(args.ogc_file, ogc_server_address)
    ogc_config.discovery(verbose)

    # Module initialization and runtime phase
    module = SCRALGPSPoll(ogc_config, args.connection_file, pilot_mqtt_topic_prefix)
    module.runtime()


if __name__ == '__main__':
    print("\n"+BANNER % VERSION+"\n")
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
