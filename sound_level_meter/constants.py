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

# ToDo: Add URL for a SCRAL endpoint listening to "sound event detection" requests
URI_DEFAULT = ""
URI_SOUND_EVENT = URI_DEFAULT + ""

# ToDo: check which info is still valid and which needs to be updated

# CLOUD URLS and IDs
URL_SLM_CLOUD = "https://bkcluster-test.bksv.com/monica/api/v1"
URL_SLM_LOGIN = "https://bkcluster-test.bksv.com/monica/api/v1/account/login"

# CLOUD_HEADERS = {"Accept": "application/json", "Authorization": ""}
TENANT_ID = "f159a3d1-cde1-405e-bc46-754609125585"
SITE_ID = "54c9dd30-f915-42b7-b00c-c07c891fb0ce"

# CREDENTIALS
CREDENTIALS = {"clientId": "7aab9af4-d311-4091-8bfc-35cb6b96b491",
               "secret": "B4Ar3osyeYK2b8sAVcODPexREyBN3z9mW4WZ15VkDSA="}

SLM_LOGIN_PREFIX = "Bearer "

# DATETIMES
REQUIRED_START_DATETIME = "2019-03-01T09:00:00Z"
REQUIRED_END_DATETIME = ""
UPDATE_INTERVAL = 15
