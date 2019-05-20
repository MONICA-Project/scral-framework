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
# Movida = 8570 --- NS = 8560 --- RIF = 8550 --- Tivoli = 8540
VPN_PORT = 8560

# URI
URI_DEFAULT = "/scral/v1.0/slm-gw"
URI_ACTIVE_DEVICES = URI_DEFAULT + "/active-devices"
URI_SOUND_EVENT = URI_DEFAULT + "/sound-event"


# CLOUD URLS and IDs
URL_SLM_CLOUD = "https://bkcluster-test.bksv.com/monica/api/v1"
URL_SLM_LOGIN = "https://bkcluster-test.bksv.com/monica/api/v1/account/login"
# CLOUD_HEADERS = {"Accept": "application/json", "Authorization": ""}


# CREDENTIALS
CREDENTIALS = {"clientId": "7aab9af4-d311-4091-8bfc-35cb6b96b491",
               "secret": "B4Ar3osyeYK2b8sAVcODPexREyBN3z9mW4WZ15VkDSA="}

SLM_LOGIN_PREFIX = "Bearer "

# DATETIMES
REQUIRED_START_DATETIME = "2019-03-01T09:00:00Z"
REQUIRED_END_DATETIME = ""
UPDATE_INTERVAL = 15
RETRY_INTERVAL = 120

MIN5_IN_SECONDS = 300

# KEYS
DEVICE_NAME_KEY = "device_name"
