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

# PORT
# Movida = 8370 --- RIF = 8350 --- Tivoli = 8340 --- KFF = 8335
VPN_PORT = 8335

# URI
URI_DEFAULT = "/scral/v1.0/sfn"
URI_ACTIVE_DEVICES = URI_DEFAULT + "/active-devices"
URI_CAMERA = URI_DEFAULT + "/camera"
URI_CDG = URI_DEFAULT + "/crowd-density-global"

# Types
CAMERA_SENSOR_TYPE = "Camera"
CDG_SENSOR_TYPE = "Crowd-Density-Global"

CDG_PROPERTY = "CDG-Estimation"

# Keys
CAMERA_ID_KEY = "camera_id"
CAMERA_IDS_KEY = "camera_ids"
CAMERA_POSITION_KEY = 'camera_position'
MODULE_ID_KEY = "module_id"
TYPE_MODULE_KEY = "type_module"

FIGHT_KEY = "fighting_detection"
CROWD_KEY = "crowd_density_local"
FLOW_KEY = "flow_analysis"
OBJECT_KEY = "object_detection"
GATE_COUNT_KEY = "gate_count"

CDG_KEY = "crowd_density_global"
