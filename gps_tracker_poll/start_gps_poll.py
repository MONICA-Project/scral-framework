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

"""
ROADMAP: these are main steps in which this SCRAL module is divided.

PHASE PRELIMINARY:
  0. SEE SCRALModule for previous steps.

PHASE STARTUP: INIT
  1. Init variables and setup an MQTT listener connection

PHASE RUNTIME: INTEGRATION
  2. Discovery of physical devices through external platform
  3. Upload DATASTREAM entities to OGC Server
  4. Subscribe to MQTT topics
  5. Launching dynamic discovery thread
  6. Listen to incoming data and publish OBSERVATIONS to OGC Broker

PHASE DYNAMIC DISCOVERY
  7. After a certain amount of time, if new devices are registered, new MQTT Subscriptions are executed
"""
#############################################################################
import os
import signal
import sys

from scral_module import util
from scral_module import BANNER, VERSION
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE, \
                                   FILENAME_CONFIG, FILENAME_COMMAND_FILE

from gps_tracker_poll.gps_poll_module import SCRALGPSPoll


def main():
    module_description = "SCRAL GPS Tracker Polling instance"
    cmd_line = util.parse_small_command_line(module_description)
    pilot_config_folder = cmd_line.pilot.lower() + "/"

    # Preparing all the necessary configuration paths
    abs_path = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(abs_path, FILENAME_CONFIG)
    connection_path = os.path.join(config_path, pilot_config_folder)
    command_line_file = os.path.join(connection_path + FILENAME_COMMAND_FILE)

    # Taking and setting application parameters
    args = util.load_from_file(command_line_file)
    args["config_path"] = config_path
    args["connection_path"] = connection_path

    # OGC-Configuration
    ogc_config = SCRALGPSPoll.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Module initialization and runtime phase
    global module
    filename_connection = os.path.join(connection_path + args['connection_file'])
    catalog_name = args["pilot"] + "_GPS-poll.json"
    module = SCRALGPSPoll(ogc_config, filename_connection, args['pilot'], catalog_name)
    module.runtime()


if __name__ == '__main__':
    print("\n"+BANNER % VERSION+"\n")
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
