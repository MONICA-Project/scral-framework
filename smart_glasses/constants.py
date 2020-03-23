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

# KEYS
TAG_ID_KEY = "tagId"
TYPE_KEY = "type"
TIMESTAMP_KEY = "timestamp"
