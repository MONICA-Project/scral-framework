#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
from typing import Optional, Union, List, Tuple

CATALOG_FILENAME = "resource_catalog.json"
CATALOG_FOLDER = "catalogs/"

# HTTP STRINGS
REST_HEADERS = {'Content-Type': 'application/json'}

SUCCESS_RETURN_STRING = "Success"
SUCCESS_DELETE = "Device deleted"
TEST_PASSED = "Test passed"

ERROR_RETURN_STRING = "Error"
ERROR_DELETE = "Delete failed"
INTERNAL_SERVER_ERROR = "Internal server error"
WRONG_PAYLOAD_REQUEST = "Wrong payload request"
WRONG_REQUEST = "Wrong request"
WRONG_CONTENT_TYPE = "Wrong content type format"
UNKNOWN_CONTENT_TYPE = "Unrecognized content type"
UNKNOWN_PROPERTY = "Unknown property"
DUPLICATE_REQUEST = "Duplicate request"
INVALID_DATASTREAM = "Invalid DATASTREAM"
NO_DATASTREAM_ID = "Missing DATASTREAM ID"
DEVICE_NOT_REGISTERED = "Device not registered"
NO_MQTT_PUBLICATION = "Impossible to publish on MQTT broker."

# Username and password necessary for accessing OGC server
OGC_SERVER_USERNAME = "scral"
OGC_SERVER_PASSWORD = "A5_xYY#HqNiao_12#b"

# MQTT default values
MQTT_CLIENT_PREFIX = "SCRAL"
BROKER_PERT = "130.192.85.32"
BROKER_DEFAULT_PORT = 1883
DEFAULT_KEEPALIVE = 60
# MQTT quality of service:
# 0 --> Fire and Forget
# 1 --> At least one message will be received by the broker
# 2 --> Exactly 1 message is received by the broker
DEFAULT_MQTT_QOS = 1

# MQTT connector & resource manager
MQTT_KEY = "mqtt"
MQTT_SUB_BROKER_KEY = "sub_broker"
MQTT_SUB_BROKER_PORT_KEY = "sub_broker_port"
MQTT_SUB_BROKER_KEEP_KEY = "sub_broker_keepalive"

# Debug, graphic and similar
START_DATASTREAMS_REGISTRATION = "\n\n--- Start OGC DATASTREAMs registration ---\n"
END_DATASTREAMS_REGISTRATION = "--- End of OGC DATASTREAMs registration ---\n"
START_OBSERVATION_REGISTRATION = "\n\n--- Start OGC OBSERVATIONs registration ---\n"
CREDITS = "(c) 2019, LINKS Foundation\ndeveloped by Jacopo Foglietti & Luca Mannella.\n"
END_MESSAGE = "\nThat's all folks! Thanks for choosing SCRAL!\n"+CREDITS

# ERROR CODES
ERROR_MISSING_CONNECTION_FILE = 11
ERROR_MISSING_OGC_FILE = 22
ERROR_WRONG_PILOT_NAME = 33
ERROR_NO_SERVER_CONNECTION = 44

# CONFIGURATION FILES
FILENAME_CONFIG = "config/"
FILENAME_COMMAND_FILE = "cli_file.json"

# log
DEFAULT_LOG_FORMATTER = "%(asctime)s.%(msecs)04d %(name)-7s %(levelname)s: %(message)s"

# REST ENDPOINTS
ENABLE_FLASK = 0
ENABLE_CHERRYPY = 1
ENABLE_WSGISERVER = 2

# Arguments
VERBOSE_KEY = "verbose"
PILOT_KEY = "pilot"
CONNECTION_PATH_KEY = "connection_path"
CONNECTION_FILE_KEY = "connection_file"
CATALOG_NAME_KEY = "catalog_name"
CONFIG_PATH_KEY = "config_path"
OGC_FILE_KEY = "ogc_file"
REST_KEY = "REST"
OGC_SERVER_ADD_KEY = "ogc_server_address"

# Code keys constants
OGC_ID_KEY = "@iot.id"
OGC_DEVICE_NAME_KEY = "name"
GOST_RESULT_KEY = "value"

# Active Devices
REGISTERED_DEVICES_KEY = "registered_devices"

ACTIVE_DEVICES_KEY = "active_devices"
ACTUAL_COUNTER_KEY = "actual_counter"
COUNTER_KEY = "counter"
LAST_UPDATE_KEY = "last_update"
UPDATE_INTERVAL_KEY = "update_interval"

# Documentation
MODULE_NAME_KEY = "module_name"
ENDPOINT_PORT_KEY = "endpoint_port"
ENDPOINT_URL_KEY = "endpoint_url"

# Duck Typing / Type Hinting
COORD = Union[Tuple[float, float], List[float]]
OPT_COORD = Optional[COORD]
OPT_LIST = Optional[Union[tuple, list]]

# default values
DEFAULT_CONFIG = "local"
DEFAULT_MODULE_NAME = "SCRAL Module"
DEFAULT_URL = "localhost"
DEFAULT_REST_PORT = 8000
DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_REST_CONFIG = {
    MODULE_NAME_KEY: DEFAULT_MODULE_NAME,
    ENDPOINT_URL_KEY: DEFAULT_URL,
    ENDPOINT_PORT_KEY: DEFAULT_REST_PORT
}

# Payload keys
TAG_ID_KEY = "tagId"
TIMESTAMP_KEY = "timestamp"
LATITUDE_KEY = "latitude"
LONGITUDE_KEY = "longitude"
