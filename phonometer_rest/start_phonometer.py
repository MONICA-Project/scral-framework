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

from microphone.constants import NAME_KEY
from phonometer.constants import URI_DEFAULT, URI_ACTIVE_DEVICES
from phonometer_rest.constants import URI_ADD_PHONOMETER, URI_OBSERVATION, URI_REMOVE_DEVICE
from phonometer_rest.phonometer_module import SCRALPhonometerREST

flask_instance = Flask(__name__)
scral_module: Optional[SCRALPhonometerREST] = None
DOC = DEFAULT_REST_CONFIG


def main():
    module_description = "Phonometer REST integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))

    global scral_module, DOC
    scral_module, args, DOC = util.initialize_module(module_description, abs_path, SCRALPhonometerREST)
    scral_module.runtime(flask_instance)


@flask_instance.route(URI_ADD_PHONOMETER, methods=["POST"])
def register_phonometer() -> Response:
    response = scral_module.ogc_datastream_registration(request.json)
    return response


@flask_instance.route(URI_REMOVE_DEVICE, methods=["DELETE"])
def delete_phonometer() -> Response:
    device_id = request.json[NAME_KEY]
    response = scral_module.delete_device(device_id)
    return response


@flask_instance.route(URI_OBSERVATION, methods=["PUT"])
def phonometer_observations() -> Response:
    response = scral_module.observation_registration(request.json)
    return response


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices() -> Response:
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)
    return make_response(jsonify(scral_module.get_active_devices()), 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module() -> str:
    """ Checking if SCRAL is running.
        :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = DOC[ENDPOINT_URL_KEY]+":"+str(DOC[ENDPOINT_PORT_KEY])
    gets = (URI_ACTIVE_DEVICES, )
    posts = (URI_ADD_PHONOMETER, )
    puts = (URI_OBSERVATION, )
    deletes = (URI_REMOVE_DEVICE, )
    to_ret = util.to_html_documentation(DOC[MODULE_NAME_KEY], link, gets=gets, posts=posts, deletes=deletes, puts=puts)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
