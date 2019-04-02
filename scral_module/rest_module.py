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
ROADMAP: these are main steps in which REST SCRAL module processing is divided.

PHASE PRELIMINARY:
  0. SEE SCRALModule for previous steps.

PHASE RUNTIME: INTEGRATION
  1. Expose SCRAL endpoints and listen to incoming requests
"""

#############################################################################
import cherrypy

import scral_module.util as util
from scral_module.constants import CATALOG_FILENAME
from scral_module.scral_module import SCRALModule


class SCRALRestModule(SCRALModule):
    """ This class is the base entity of all REST Modules.
        When you want to develop a new Rest-SCRAL module, you have to extend this class and define what endpoints you
        want to expose.
        If necessary, you can also extend the __init__ initializer and the runtime method. In runtime, we should call
        super().runtime() as last instruction to start the cherrypy service.
    """

    def __init__(self, ogc_config, connection_file, pilot, catalog_name=CATALOG_FILENAME):
        """ Load OGC configuration model, initialize MQTT Broker for publishing Observations and prepare Flask.

        :param ogc_config: The reference of the OGC configuration.
        :param connection_file: A file containing connection information.
        :param pilot: The MQTT topic prefix on which information will be published.
        """
        super().__init__(ogc_config, connection_file, pilot, catalog_name)

        # Creating endpoint for listening to REST requests
        connection_config_file = util.load_from_file(connection_file)
        self._listening_address = connection_config_file["REST"]["listening_address"]["address"]
        self._listening_port = int(connection_config_file["REST"]["listening_address"]["port"])

    # noinspection PyMethodOverriding
    def runtime(self, flask_instance):
        """
        This method deploys an REST endpoint as Flask application based on CherryPy WSGI web server.
        This endpoint will listen for incoming REST requests on different route paths.
        """
        cherrypy.tree.graft(flask_instance, "/")
        cherrypy.config.update({"server.socket_host": self._listening_address,
                                "server.socket_port": self._listening_port,
                                "engine.autoreload.on": False,
                                })
        cherrypy.engine.start()
        cherrypy.engine.block()

    def get_address(self):
        return self._listening_address

    def get_port(self):
        return self._listening_port
