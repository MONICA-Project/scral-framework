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

# URI
URI_DEFAULT = "/scral/v1.0/gps-tracker-gw"
URI_ACTIVE_DEVICES = URI_DEFAULT + "/active-devices"

URI_GPS_TAG_REGISTRATION = URI_DEFAULT + "/gps-tag"
URI_GPS_TAG_LOCALIZATION = URI_GPS_TAG_REGISTRATION + "/localization"
URI_GPS_TAG_ALERT = URI_GPS_TAG_REGISTRATION + "/alert"

# Dictionary keys
TIMESTAMP_KEY = "timestamp"
TAG_ID_KEY = "tagId"
TYPE_KEY = "type"
