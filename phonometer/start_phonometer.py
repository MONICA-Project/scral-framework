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
import os
import sys
import signal
from typing import Optional

import scral_core as scral
from scral_core import util
from scral_core.constants import END_MESSAGE, DEFAULT_REST_CONFIG

from phonometer_module import SCRALPhonometer

scral_module: Optional[SCRALPhonometer] = None
DOC = DEFAULT_REST_CONFIG


def main():
    module_description = "Phonometer integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))

    global scral_module, DOC
    scral_module, args, DOC = util.initialize_module(module_description, abs_path, SCRALPhonometer)
    scral_module.runtime()


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
