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
URI_DEFAULT = "/scral/v1.0/monicora"
URI_ACTIVE_DEVICES = URI_DEFAULT + "/active-devices"

URI_GLASSES_REGISTRATION = URI_DEFAULT + "/glasses"
URI_GLASSES_LOCALIZATION = URI_GLASSES_REGISTRATION + "/localization"
URI_GLASSES_INCIDENT = URI_GLASSES_REGISTRATION + "/incident"

# Filters
FILTER_VIRTUAL_PROPERTY = "?$filter=startswith(name,'Incident-Notification')"
FILTER_VIRTUAL_SENSOR = "?$filter=startswith(name,'Incident')"

# Values
PROPERTY_LOCALIZATION_NAME = "Localization-Smart-Glasses"
PROPERTY_INCIDENT_NAME = "Incident-Reporting"
