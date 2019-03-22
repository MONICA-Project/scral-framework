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
import logging
import signal
import sys

from scral_module import util
from scral_module import mqtt_util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE, ERROR_WRONG_PILOT_NAME
from scral_module import BANNER, VERSION

from gps_tracker_poll.gps_poll_module import SCRALGPSPoll

verbose = False


def main():
    module_description = "GPS Tracker Polling instance"
    args = util.parse_command_line(module_description)

    # OGC-Configuration
    ogc_config = SCRALGPSPoll.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Retrieving pilot name --- 'local' is the default configuration value
    pilot_mqtt_topic_prefix = mqtt_util.get_publish_mqtt_topic(args.pilot)
    if not pilot_mqtt_topic_prefix:
        logging.critical('Wrong pilot name: "' + args.pilot + '"!')
        exit(ERROR_WRONG_PILOT_NAME)
    else:
        logging.debug("MQTT publishing topic prefix: " + pilot_mqtt_topic_prefix)

    # Module initialization and runtime phase
    global module
    module = SCRALGPSPoll(ogc_config, args.connection_file, pilot_mqtt_topic_prefix)
    module.runtime()


if __name__ == '__main__':
    print("\n"+BANNER % VERSION+"\n")
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
