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

URL_CLOUD = "https://api.smartdatanet.it/api"
URL_TENANT = "https://api.smartdatanet.it/metadataapi/api/v02/search?tenant=cittato_rumore&top=1000"

ACTIVE_DEVICES = ["ds_S_01_1928", "ds_S_02_1926", "ds_S_03_1927", "ds_S_05_1932", "ds_S_06_1931"]

FREQ_INTERVALS = ["16", "20", "25", "31_5", "40", "50", "63", "80", "100", "125", "160", "200",
                  "250", "315", "400", "500", "630", "800", "1000", "1250", "1600", "2000", "2500",
                  "3150", "4000", "5000", "6300", "8000", "10000", "12500", "16000", "20000"]

FILTER_SDN_1 = "Measures?%20&$format=json&$filter=time%20gt%20datetimeoffset%27"
FILTER_SDN_2 = "%27%20and%20time%20le%20datetimeoffset%27"
FILTER_SDN_3 = "%27&$orderby=time%20asc&$top=50"

LAEQ_KEY = "LAeq"
SPECTRA_KEY = "CPBLZeq"

UPDATE_INTERVAL = 15
RETRY_INTERVAL = 120
