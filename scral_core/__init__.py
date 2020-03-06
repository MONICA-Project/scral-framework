#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    SCRAL Module
    This module is the starting point for developing a SCRAL module.
    In particular the class SCRALModule have to be extended and the runtime method have to be overwritten/overloaded.
"""

import logging
import sys

VERSION = "v3.2.3"
BANNER = """
        _____ __________  ___    __                                         
       / ___// ____/ __ \/   |  / /                                         
       \__ \/ /   / /_/ / /| | / /                                          
      ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Adaptation Layer 
     /____/\____/_/ |_/_/  |_/_____/   %s - suggested at least Python 3.6            

     (c) 2017-2020, LINKS Foundation
     developed by Jacopo Foglietti & Luca Mannella

"""

if sys.flags.optimize == 0:
    logging.debug("All debug checks are active, performances may be impaired")
