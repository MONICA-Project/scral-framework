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
    SCRAL - constants
    This file contains useful constants for this module.
"""

# PORT
# Movida = 8370 --- RIF = 8350 --- Tivoli = 8340
VPN_PORT = 8370

# URI
URI_DEFAULT = "/scral/v1.0/sfn"
URI_ACTIVE_DEVICES = URI_DEFAULT + "/active-devices"
URI_CAMERA = URI_DEFAULT + "/camera"
URI_CDG = URI_DEFAULT + "/crowd-density-global"

# Types
CAMERA_SENSOR_TYPE = "Camera"
CDG_SENSOR_TYPE = "Crowd-Density-Global"
