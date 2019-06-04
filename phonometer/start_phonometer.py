###################################################################################################
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

PHASE: INTEGRATION
  1. Poll data from SmartDataNet (SDN) Platform
  2. Upload OGC Observation through MQTT
"""

#############################################################################
import sys
import signal

import scral_module as scral
from scral_module import util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE

from phonometer_module import SCRALPhonometer

module: SCRALPhonometer = None


def main():
    module_description = "Phonometer integration instance"
    args = util.parse_command_line(module_description)

    # OGC-Configuration
    ogc_config = SCRALPhonometer.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Module initialization and runtime phase
    global module
    catalog_name = args.pilot + "_phonometer.json"
    module = SCRALPhonometer(ogc_config, args.connection_file, args.pilot, catalog_name)
    module.runtime()


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
