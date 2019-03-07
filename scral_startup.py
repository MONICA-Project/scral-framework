# !/usr/bin/env python3
# -*- coding: utf-8 -*-
##############################################################################
#      _____ __________  ___    __                                           #
#     / ___// ____/ __ \/   |  / /                                           #
#     \__ \/ /   / /_/ / /| | / /                                            #
#    ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Adaptation Layer  #
#   /____/\____/_/ |_/_/  |_/_____/   v.2.0 - enhanced by Python 3           #
#                                                                            #
# LINKS Foundation, (c) 2019                                                 #
# developed by Jacopo Foglietti & Luca Mannella                              #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md      #
#                                                                            #
##############################################################################
import signal
import sys

import scral_module as scral
from scral_module import util
# from gps_tracker_poll import start_gps_poll as module
# from env_sensor_onem2m import start_onem2m_env as module
from sound_level_meter import start_slm as module


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    module.main()

    print("\nThat's all folks! Thanks for choosing SCRAL!")
    print("(c) 2019, LINKS Foundation\n developed by Jacopo Foglietti & Luca Mannella.\n")
