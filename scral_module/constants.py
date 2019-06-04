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

# Local catalog of the active DATASTREAM ID for each OBSERVEDPROPERTY associated to the registered Device IDs
CATALOG_FILENAME = "resource_catalog.json"
CATALOG_FOLDER = "catalogs/"

# REST headers
REST_HEADERS = {'Content-Type': 'application/json'}

# default value for pilot and configuration approach
DEFAULT_CONFIG = "local"

# Username and password necessary for accessing OGC server
OGC_SERVER_USERNAME = "scral"
OGC_SERVER_PASSWORD = "A5_xYY#HqNiao_12#b"

# HTTP
VPN_URL = "monappdwp3.monica-cloud.eu"
# VPN_URL = "monapp-lst.monica-cloud.eu"

# MQTT default values
BROKER_PERT = "130.192.85.32"
BROKER_DEFAULT_PORT = 1883
DEFAULT_KEEPALIVE = 60
# MQTT quality of service:
# 0 --> Fire and Forget
# 1 --> At least one message will be received by the broker
# 2 --> Exactly 1 message is received by the broker
DEFAULT_MQTT_QOS = 1


# Debug, graphic and similiar
CREDITS = "(c) 2019, LINKS Foundation\ndeveloped by Jacopo Foglietti & Luca Mannella.\n"
END_MESSAGE = "\nThat's all folks! Thanks for choosing SCRAL!\n"+CREDITS

# ERROR CODES
ERROR_MISSING_CONNECTION_FILE = 11
ERROR_MISSING_OGC_FILE = 22
ERROR_WRONG_PILOT_NAME = 33
ERROR_NO_SERVER_CONNECTION = 44

# Code keys constants
OGC_ID_KEY = "@iot.id"
OGC_DEVICE_NAME_KEY = "name"
GOST_RESULT_KEY = "value"

# log
DEFAULT_LOG_FORMATTER = "%(asctime)s.%(msecs)04d %(name)-7s %(levelname)s: %(message)s"
