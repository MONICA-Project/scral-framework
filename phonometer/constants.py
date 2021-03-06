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
URL_CLOUD = "https://api.smartdatanet.it/api"
URL_TENANT = "https://api.smartdatanet.it/metadataapi/api/v02/search?tenant=cittato_rumore"

# Exposed URI
URI_DEFAULT = "/scral/v1.0/phono-gw"
URI_ACTIVE_DEVICES = URI_DEFAULT + "/active-devices"

ACTIVE_DEVICES = ["ds_S_01_1928", "ds_S_02_1926", "ds_S_03_1927", "ds_S_05_1932", "ds_S_06_1931", "ds_S_07_1933"]

FREQ_INTERVALS = ["16", "20", "25", "31_5", "40", "50", "63", "80", "100", "125", "160", "200",
                  "250", "315", "400", "500", "630", "800", "1000", "1250", "1600", "2000", "2500",
                  "3150", "4000", "5000", "6300", "8000", "10000", "12500", "16000", "20000"]

FILTER_SDN_1 = "Measures?%20&$format=json&$filter=time%20gt%20datetimeoffset%27"
FILTER_SDN_2 = "%27%20and%20time%20le%20datetimeoffset%27"
FILTER_SDN_3 = "%27&$orderby=time%20asc&$top=50"

# Timing
UPDATE_INTERVAL = 15
RETRY_INTERVAL = 120

# Keys
LAEQ_KEY = "LAeq"
SPECTRA_KEY = "CPBLZeq"
METADATA_KEY = "metadata"
STREAM_KEY = "stream"
SMART_OBJECT_KEY = "smartobject"
CODE_KEY = "code"
DATASET_KEY = "dataset"
DESCRIPTION_KEY = "description"
COUNT_KEY = "count"
TOTAL_COUNT_KEY = "totalCount"

OBS_DATA_KEY = "d"
OBS_DATA_RESULTS_KEY = "results"
VALUE_TYPE_KEY = "valueType"
RESPONSE_KEY = "response"
