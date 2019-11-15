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
import os
import logging

from flask import Flask, make_response, jsonify, Response
import cherrypy
from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher

import scral_core.util as util
from scral_core.ogc_configuration import OGCConfiguration
from scral_core.constants import CATALOG_FILENAME, D_CONFIG_KEY, ENABLE_FLASK, ENABLE_CHERRYPY, ENABLE_WSGISERVER, \
    SUCCESS_RETURN_STRING, SUCCESS_DELETE, ERROR_RETURN_STRING, ERROR_DELETE, ERROR_MISSING_ENV_VARIABLE, REST_KEY, \
    LISTENING_ADD_KEY, PORT_KEY, ADDRESS_KEY, D_CUSTOM_MODE, ERROR_MISSING_CONNECTION_FILE, LISTENING_PORT_KEY, \
    DEFAULT_LISTENING_ADD, DEFAULT_LISTENING_PORT
from scral_core.scral_module import SCRALModule


class SCRALRestModule(SCRALModule):
    """ This class is the base entity of all REST Modules.
        When you want to develop a new Rest-SCRAL module, you have to extend this class and define what endpoints you
        want to expose.
        If necessary, you can also extend the __init__ initializer and the runtime method.
        Runtime method will start the web server and it is a blocking function.
    """

    def __init__(self, ogc_config: OGCConfiguration, connection_file: str, pilot: str,
                 catalog_name: str = CATALOG_FILENAME):
        """ Load OGC configuration model, initialize MQTT Broker for publishing Observations and prepare Flask.

        :param ogc_config: The reference of the OGC configuration.
        :param connection_file: A file containing connection information.
        :param pilot: The MQTT topic prefix on which information will be published.
        :param catalog_name: The name of the resource catalog. If not specified a default one will be used.
        """
        super().__init__(ogc_config, connection_file, pilot, catalog_name)

        if not connection_file:
            if D_CONFIG_KEY in os.environ.keys():
                if os.environ[D_CONFIG_KEY] == D_CUSTOM_MODE:
                    try:
                        self._listening_address = os.environ[LISTENING_ADD_KEY.upper()]
                    except KeyError:
                        logging.warning(LISTENING_ADD_KEY.upper() + " not set, default listening address: "
                                        + DEFAULT_LISTENING_ADD)
                        self._listening_address = DEFAULT_LISTENING_ADD
                    try:
                        self._listening_port = int(os.environ[LISTENING_PORT_KEY.upper()])
                    except KeyError:
                        logging.warning(LISTENING_PORT_KEY.upper() + " not set, default listening port: "
                                        + str(DEFAULT_LISTENING_PORT))
                        self._listening_port = DEFAULT_LISTENING_PORT
                else:
                    logging.critical("No connection file for pilot: " + str(pilot))
                    exit(ERROR_MISSING_CONNECTION_FILE)
            else:
                logging.critical("Missing connection file or environmental variable!")
                exit(ERROR_MISSING_ENV_VARIABLE)
        else:
            # Retrieving endpoint information for listening to REST requests
            connection_config_file = util.load_from_file(connection_file)
            self._listening_address = connection_config_file[REST_KEY][LISTENING_ADD_KEY][ADDRESS_KEY]
            self._listening_port = int(connection_config_file[REST_KEY][LISTENING_ADD_KEY][PORT_KEY])

    # noinspection PyMethodOverriding
    def runtime(self, flask_instance: Flask, mode: int = ENABLE_FLASK):
        """
            This method deploys a REST endpoint as using different technologies according to the "mode" value.
            This endpoint will listen for incoming REST requests on different route paths.
        """

        if mode == ENABLE_FLASK:
            # simply run Flask
            flask_instance.run(host=self._listening_address, port=self._listening_port, threaded=True)
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

    def delete_device(self, device_id: str, remove_only_from_catalog: bool = False) -> Response:
        result, client_fault = super().delete_device(device_id, remove_only_from_catalog)
        if result:
            return make_response(jsonify({SUCCESS_RETURN_STRING: SUCCESS_DELETE}), 200)
        else:
            if client_fault:
                error_code = 400
            else:
                error_code = 500
            return make_response(jsonify({ERROR_RETURN_STRING: ERROR_DELETE}), error_code)

    def get_address(self) -> str:
        return self._listening_address

    def get_port(self) -> int:
        return self._listening_port
