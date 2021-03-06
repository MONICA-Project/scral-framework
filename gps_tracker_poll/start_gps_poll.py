#############################################################################
#      _____ __________  ___    __                                          #
#     / ___// ____/ __ \/   |  / /                                          #
#     \__ \/ /   / /_/ / /| | / /                                           #
#    ___/ / /___/ _, _/ ___ |/ /___                                         #
#   /____/\____/_/ |_/_/  |_/_____/   Smart City Resource Adaptation Layer  #
#                                                                           #
# LINKS Foundation, (c) 2017-2020                                           #
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

from scral_core import util
from scral_core import BANNER, VERSION
from scral_core.constants import END_MESSAGE

from gps_tracker_poll.gps_poll_module import SCRALGPSPoll


def main():
    module_description = "SCRAL GPS Tracker Polling instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))
    scral_module: SCRALGPSPoll
    scral_module, args, doc = util.initialize_module(module_description, abs_path, SCRALGPSPoll)
    scral_module.runtime()


if __name__ == '__main__':
    print("\n"+BANNER % VERSION+"\n")
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
