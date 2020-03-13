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
from phonometer.constants import URI_DEFAULT
"""
    SCRAL - constants
    This file contains useful constants for this module.
"""

# URL
URI_PHONOMETER = URI_DEFAULT + "/phonometer"
URI_ADD_PHONOMETER = URI_PHONOMETER + "/add"
URI_REMOVE_DEVICE = URI_PHONOMETER + "/remove"
URI_OBSERVATION = URI_PHONOMETER + "/observation"

# Keys
DEVICE_NAME_KEY = "deviceName"

DATA_KEY = "data"
MEASURES_KEY = "measures"
MEASURE_KEY = "measure"
SAMPLES_KEY = "samples"
SAMPLE_TIME_KEY = "time"
SAMPLE_START_TIME_KEY = "startTime"
SAMPLE_END_TIME_KEY = "endTime"
SAMPLE_VALUE_KEY = "value"

SAMPLE_OK_PROCESSED = "Sample succesfully processed"
WRONG_SAMPLES = "Wrong samples"
WRONG_MEASURES = "Wrong measures"
WRONG_PHONOMETERS = "Wrong phonometers"
