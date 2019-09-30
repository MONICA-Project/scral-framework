#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    SCRAL Module
    This module is the starting point for developing a SCRAL module.
    In particular the class SCRALModule have to be extended and the runtime method have to be overwritten/overloaded.
"""

import logging
import sys

VERSION = "v2.2"
BANNER = """
        _____ __________  ___    __                                         
       / ___// ____/ __ \/   |  / /                                         
       \__ \/ /   / /_/ / /| | / /                                          
      ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Adaptation Layer 
     /____/\____/_/ |_/_/  |_/_____/   %s - enhanced by Python 3            

     (c) 2019, LINKS Foundation
     developed by Jacopo Foglietti & Luca Mannella

"""

if sys.flags.optimize == 0:
    logging.debug("All debug checks are active, performances may be impaired")
