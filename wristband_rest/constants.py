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
    SCRAL - constants
    This file contains useful constants for this module.
"""
from wristband.constants import URI_DEFAULT, URI_WRISTBAND

# URI
URI_WRISTBAND_ASSOCIATION = URI_DEFAULT + "/friend-connect"
URI_WRISTBAND_LOCALIZATION = URI_WRISTBAND + "/localization"
URI_WRISTBAND_BUTTON = URI_WRISTBAND + "/button"
