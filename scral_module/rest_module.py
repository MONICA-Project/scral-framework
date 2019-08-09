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
from flask import Flask
import cherrypy
from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher

import scral_module.util as util
from scral_module.ogc_configuration import OGCConfiguration
from scral_module.constants import CATALOG_FILENAME, ENABLE_FLASK, ENABLE_CHERRYPY, ENABLE_WSGISERVER
from scral_module.scral_module import SCRALModule


class SCRALRestModule(SCRALModule):
    """ This class is the base entity of all REST Modules.
        When you want to develop a new Rest-SCRAL module, you have to extend this class and define what endpoints you
        want to expose.
        If necessary, you can also extend the __init__ initializer and the runtime method.
        Runtime method will start the web server and it is a blocking function.
    """

    def __init__(self, ogc_config: OGCConfiguration, connection_file: str, pilot: str, catalog_name=CATALOG_FILENAME):
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
    def runtime(self, flask_instance: Flask, mode=ENABLE_FLASK):
        """
            This method deploys a REST endpoint as using different technologies according to the "mode" value.
            This endpoint will listen for incoming REST requests on different route paths.
        """

        if mode == ENABLE_FLASK:
            # simply run Flask
            flask_instance.run(host="0.0.0.0", port=8000, threaded=True)
        elif mode == ENABLE_CHERRYPY:
            # Run Flask wrapped by Cherrypy
            cherrypy.tree.graft(flask_instance, "/")
            cherrypy.config.update({"server.socket_host": self._listening_address,
                                    "server.socket_port": self._listening_port,
                                    "engine.autoreload.on": False,
                                    })
            cherrypy.engine.start()
            cherrypy.engine.block()
        elif mode == ENABLE_WSGISERVER:
            # Run Flask wrapped by a WSGI Server.
            dispatcher = PathInfoDispatcher({'/': flask_instance})
            server = WSGIServer((self._listening_address, self._listening_port), dispatcher)
            try:
                server.start()
                # server.block
            except KeyboardInterrupt:
                server.stop()
        else:
            raise RuntimeError("Invalid runtime mode was selected.")

    def get_address(self) -> str:
        return self._listening_address

    def get_port(self) -> int:
        return self._listening_port
