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
import json
import logging

import arrow

from scral_ogc import OGCObservation
from scral_ogc.ogc_datastream import OGCDatastream
from scral_module import util
from scral_module.rest_module import SCRALRestModule


class SCRALSecurityFusionNode(SCRALRestModule):

    def ogc_datastream_registration(self):
        pass

    def ogc_observation_registration(self):
        pass
