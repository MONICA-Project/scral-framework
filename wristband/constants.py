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
# VPN-TEST = 8491 --- LST = 8490 --- IoTWeek = 8480 --- Movida = 8470
VPN_PORT = "8491"

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

SENSOR_ULTRAWIDEBAND_SCRAL = "UWB"
SENSOR_ULTRAWIDEBAND_DEXELS = "uwb"
SENSOR_ASSOCIATION_NAME = "WRISTBAND-GW/Friend-Connect/Friend-Connect-Request"
