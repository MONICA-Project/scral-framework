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
    This file contains useful constants for SCRAL framework.
"""

# REST headers
REST_HEADERS = {'Content-Type': 'application/json'}

# default value for pilot and configuration approach
DEFAULT_CONFIG = "local"

# Local catalog of the active DATASTREAM ID for each OBSERVEDPROPERTY associated to the registered Device IDs
CATALOG_FILENAME = 'resource_catalog.json'

OGC_SERVER_USERNAME = "scral"
OGC_SERVER_PASSWORD = "A5_xYY#HqNiao_12#b"

OGC_ID_KEY = "@iot.id"
OGC_DEVICE_NAME_KEY = "name"
GOST_RESULT_KEY = "value"

BROKER_PERT = "130.192.85.32"
BROKER_DEFAULT_PORT = 1883
DEFAULT_KEEPALIVE = 60
DEFAULT_MQTT_QOS = 2

# Debug, graphic and similiar
CREDITS = "(c) 2019, LINKS Foundation\ndeveloped by Jacopo Foglietti & Luca Mannella.\n"
END_MESSAGE = "\nThat's all folks! Thanks for choosing SCRAL!\n"+CREDITS

# ERROR CODES
ERROR_MISSING_CONNECTION_FILE = 1
ERROR_MISSING_OGC_FILE = 2
ERROR_WRONG_PILOT_NAME = 3
ERROR_NO_SERVER_CONNECTION = 4
