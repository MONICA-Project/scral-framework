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

# URI
URI_DEFAULT = "/scral/v1.0/noise-app-manager"
URI_ACTIVE_DEVICES = URI_DEFAULT + "/active-devices"
URI_DEVICE = URI_DEFAULT + "/noise-device"

# KEYS
NOISE_PARTY_ID_KEY = "noise_party_id"
GEO_SERVER_KEY = "noise_party_server"

DATA_KEY = "data"
METADATA_KEY = "meta.properties"
TRACK_KEY = "track.geojson"
ID_KEY = "uuid"

# CONSTANTS
TIME_TO_SLEEP = 30

# REST, URL & FILTERS
REST_NOISE_PREFIX_REQUEST = "?REQUEST=Execute" \
                            "&SERVICE=wps" \
                            "&VERSION=1.0.0" \
                            "&IDENTIFIER=groovy:nc_raw_measurements" \
                            "&RawDataOutput=result%3dformat%40mimetype%3dapplication%2Fjson"
REST_NOISE_PARTY = "&DATAINPUTS=noiseparty%3D"
REST_NOISE_DATE_FILTER = "datefilter%3D"

# example:
# https://onomap-gs.noise-planet.org/geoserver/ows
#   ?REQUEST=Execute&SERVICE=wps&VERSION=1.0.0&IDENTIFIER=groovy:nc_raw_measurements
#    &RawDataOutput=result%3dformat%40mimetype%3dapplication%2Fjson
#    &DATAINPUTS=noiseparty%3D27%3Bdatefilter%3D2019-10-12T13:04:58
