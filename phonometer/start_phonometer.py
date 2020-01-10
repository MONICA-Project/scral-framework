###################################################################################################
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
ROADMAP: these are main steps in which this SCRAL module is divided.

PHASE PRELIMINARY:
  0. SEE SCRALModule for previous steps.

PHASE: INTEGRATION
  1. Poll data from SmartDataNet (SDN) Platform
  2. Upload OGC Observation through MQTT
"""

#############################################################################
import logging
import os
import sys
import signal
from typing import Optional

from flask import Flask, Response, request, make_response, jsonify

import scral_core as scral
from scral_core import util
from scral_core.constants import END_MESSAGE, DEFAULT_REST_CONFIG, ENDPOINT_URL_KEY, ENDPOINT_PORT_KEY, MODULE_NAME_KEY

from phonometer.constants import URI_DEFAULT, URI_ACTIVE_DEVICES
from phonometer_module import SCRALPhonometer

flask_instance = Flask(__name__)
scral_module: Optional[SCRALPhonometer] = None
DOC = DEFAULT_REST_CONFIG


def main():
    module_description = "Phonometer integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))

    global scral_module, DOC
    scral_module, args, DOC = util.initialize_module(module_description, abs_path, SCRALPhonometer)
    scral_module.runtime(flask_instance)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices() -> Response:
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)
    return make_response(jsonify(scral_module.get_resource_catalog()), 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module() -> str:
    """ Checking if SCRAL is running.
        :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = DOC[ENDPOINT_URL_KEY]+":"+str(DOC[ENDPOINT_PORT_KEY])
    gets = (URI_ACTIVE_DEVICES, )
    to_ret = util.to_html_documentation(DOC[MODULE_NAME_KEY], link, gets=gets)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
