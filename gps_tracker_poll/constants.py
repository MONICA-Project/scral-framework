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
import random

BROKER_HAMBURG_CLIENT_ID = "MONICA_GPS_"+str(random.randint(0, 1000000))

# HAMBURG OGC SERVER
OLD_OGC_HAMBURG_URL = "https://test.geoportal-hamburg.de/itsLGVhackathon/v1.0"
OGC_HAMBURG_URL = "https://iot.hamburg.de/v1.0"
OGC_HAMBURG_THING_URL = OGC_HAMBURG_URL+"/Things"
OGC_HAMBURG_FILTER = "?$filter=startswith(name,'MONICA_HAMBURG_GPS')"

# Hamburg default MQTT Topic
THINGS_SUBSCRIBE_TOPIC = "v1.0/Things"

# Hamburg Datastream constant
HAMBURG_UNIT_OF_MEASURE = "position"

# KEYS
DEVICE_ID_KEY = "device_id"

# Dynamic Discovery Sleep
DYNAMIC_DISCOVERY_SLEEP = 60*60*8  # 8 hours
