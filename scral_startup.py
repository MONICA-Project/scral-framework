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
import the_module_that_you_want_to_use as module

if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    module.main()

    print("That's all folks! Thanks for choosing SCRAL!")
    print("(c) 2019, LINKS Foundation\n developed by Jacopo Foglietti & Luca Mannella")
