# !/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import sys

import scral_module as scral
import gps_tracker_poll.start_gps_poll as pd

if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()
    pd.main()
    print("That's all folks!\n")
