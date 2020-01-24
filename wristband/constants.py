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

# URI
URI_DEFAULT = "/scral/v1.0/wristband-gw"
URI_ACTIVE_DEVICES = URI_DEFAULT + "/active-devices"

URI_WRISTBAND_ASSOCIATION = URI_DEFAULT + "/friend-connect"
URI_WRISTBAND_REGISTRATION = URI_DEFAULT + "/wearable"
URI_WRISTBAND_LOCALIZATION = URI_WRISTBAND_REGISTRATION + "/localization"
URI_WRISTBAND_BUTTON = URI_WRISTBAND_REGISTRATION + "/button"

# Observed Property
PROPERTY_LOCALIZATION_NAME = "Localization-Wristband"
PROPERTY_BUTTON_NAME = "Button-Wristband"

# Fixed values
SENSOR_ULTRAWIDEBAND_SCRAL = "UWB"
SENSOR_ULTRAWIDEBAND_DEXELS = "uwb"
SENSOR_ASSOCIATION_NAME = "WRISTBAND-GW/Friend-Connect/Friend-Connect-Request"

# Keys
TAG_ID_KEY = "tagId"
ID1_ASSOCIATION_KEY = "tagId_1"
ID2_ASSOCIATION_KEY = "tagId_2"

# CONFIGURATION FILE
FILENAME_PILOT = "lst/"
