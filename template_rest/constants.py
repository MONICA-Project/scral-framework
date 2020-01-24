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
URI_SCRAL_ROOT = "/scral/v1.0"
URI_DEFAULT = URI_SCRAL_ROOT + "/your_module"
URI_ACTIVE_DEVICES = URI_DEFAULT + "/active-devices"

URI_DEVICE_REGISTRATION = URI_DEFAULT + "/new-device"
URI_DEVICE_DELETE = URI_DEFAULT + "/delete-device"
URI_DEVICE_OBSERVATION = URI_DEFAULT + "/observation"

# Keyes
DEVICE_ID_KEY = "deviceId"
