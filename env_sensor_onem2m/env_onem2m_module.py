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
import logging

import cherrypy as cherrypy
from flask import Flask

from scral_module.scral_module import SCRALModule
import scral_module.util as util

app = Flask(__name__)


class SCRALEnvOneM2M(SCRALModule):

    def __init__(self, connection_file, pub_topic_prefix):
        super().__init__(connection_file, pub_topic_prefix)

        connection_config_file = util.load_from_file(connection_file)
        self._listening_address = connection_config_file["REST"]["listening_address"]["address"]
        self._listening_port = int(connection_config_file["REST"]["listening_address"]["port"])

    def runtime(self, ogc_config, topic):
        cherrypy.tree.graft(app, '/')
        cherrypy.config.update({'server.socket_host': self._listening_address,
                                'server.socket_port': self._listening_port,
                                'engine.autoreload.on': False,
                                })
        cherrypy.engine.start()


@app.route('/')
def test():
    """ Checking if Flask is working. """
    logging.debug(test.__name__ + " method called")

    return "<h1>Flask is running!</h1>"
