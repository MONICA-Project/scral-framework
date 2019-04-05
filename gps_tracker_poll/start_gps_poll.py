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
  1. Init variables and setup an MQTT publisher connections

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
import signal
import sys

from scral_module import util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE
from scral_module import BANNER, VERSION

from gps_tracker_poll.gps_poll_module import SCRALGPSPoll


def main():
    module_description = "GPS Tracker Polling instance"
    args = util.parse_command_line(module_description)

    # OGC-Configuration
    ogc_config = SCRALGPSPoll.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Module initialization and runtime phase
    global module
    module = SCRALGPSPoll(ogc_config, args.connection_file, args.pilot)
    module.runtime()


if __name__ == '__main__':
    print("\n"+BANNER % VERSION+"\n")
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
