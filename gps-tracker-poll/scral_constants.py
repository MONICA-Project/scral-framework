##############################################################################
#      _____ __________  ___    __                                           #
#     / ___// ____/ __ \/   |  / /                                           #
#     \__ \/ /   / /_/ / /| | / /                                            #
#    ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Abstraction Layer  #
#   /____/\____/_/ |_/_/  |_/_____/   v.2.0 - enhanced by Python 3           #
#                                                                            #
# LINKS Foundation, (c) 2019                                                 #
# developed by Jacopo Foglietti & Luca Mannella                              #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md      #
#                                                                            #
##############################################################################

BANNER = """
        _____ __________  ___    __                                     
       / ___// ____/ __ \/   |  / /                                     
       \__ \/ /   / /_/ / /| | / /                                      
      ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Abstraction Layer                                 
     /____/\____/_/ |_/_/  |_/_____/   %s - enhanced by Python 3

     (c) 2019, LINKS Foundation
     developed by Jacopo Foglietti & Luca Mannella

"""
VERSION = "v2.0"

# REST headers
REST_HEADERS = {'Content-Type': 'application/json'}

# default value for pilot and configuration approach
DEFAULT_CONFIG = "local"

# Local catalog of the active DATASTREAM ID for each OBSERVEDPROPERTY associated to the registered Device IDs
CATALOG_FILENAME = 'resource_catalog.json'

OGC_SERVER_USERNAME = "scral"
OGC_SERVER_PASSWORD = "A5_xYY#HqNiao_12#b"

OGC_ID = "@iot.id"

# HAMBURG OGC SERVER
OGC_HAMBURG_URL = "https://51.5.242.162/itsLGVhackathon/v1.0/"
# OGC_HAMBURG_URL = "https://test.geoportal-hamburg.de/itsLGVhackathon/v1.0/"
OGC_HAMBURG_THING_URL = OGC_HAMBURG_URL+"Things"
OGC_HAMBURG_FILTER = "?$filter=startswith(name,'MONICA_HAMBURG_GPS')"

# Hamburg Datastream constant
HAMBURG_UNIT_OF_MEASURE = {"name": "position", "symbol": "",
                           "definition": "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeAngle"}
