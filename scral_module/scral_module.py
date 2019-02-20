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

import json
import logging
import os

from .scral_constants import CATALOG_FILENAME
from . import scral_util


class SCRALModule(object):

    def __init__(self, connection_file):
        """ Parses the connection file and stores information about the MQTT broker.

        @:param The path of the connection file
        :return A tuple containing the OGC server address and broker ip/port information
        """

        # 1 Load connection configuration file
        connection_config_file = scral_util.load_from_file(connection_file)

        # Store broker address/port
        self._pub_broker_ip = connection_config_file["mqtt"]["pub_broker"]
        self._pub_broker_port = connection_config_file["mqtt"]["pub_broker_port"]

        # 2 Load local resource catalog / TEMPORARY USELESS
        if os.path.exists(CATALOG_FILENAME):
            self._resource_catalog = scral_util.load_from_file(CATALOG_FILENAME)
            logging.info('[PHASE-INIT] Resource Catalog: ', json.dumps(self._resource_catalog))
        else:
            logging.info("No resource catalog available on file.")
            self._resource_catalog = {}

    def runtime(self):
        raise NotImplementedError("Implement runtime method in subclasses")
