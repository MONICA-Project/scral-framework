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
import random

BROKER_HAMBURG_ADDRESS = "test.geoportal-hamburg.de"  # testing address: "broker.mqttdashboard.com"
BROKER_HAMBURG_CLIENT_ID = "MONICA_GPS_"+str(random.randint(0, 1000000))

# HAMBURG OGC SERVER
OGC_HAMBURG_URL = "https://51.5.242.162/itsLGVhackathon/v1.0/"
# OGC_HAMBURG_URL = "https://test.geoportal-hamburg.de/itsLGVhackathon/v1.0/"
OGC_HAMBURG_THING_URL = OGC_HAMBURG_URL+"Things"
OGC_HAMBURG_FILTER = "?$filter=startswith(name,'MONICA_HAMBURG_GPS')"

# Hamburg default MQTT Topic
THINGS_SUBSCRIBE_TOPIC = "v1.0/Things"

# Hamburg Datastream constant
HAMBURG_UNIT_OF_MEASURE = {"name": "position", "symbol": "",
                           "definition": "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeAngle"}
