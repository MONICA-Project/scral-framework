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
ROADMAP: these are main steps in which this SCRAL module is divided.

PHASE PRELIMINARY:
  0. SEE SCRALRESTModule for previous steps.

PHASE RUNTIME: INTEGRATION
  1. Listening for new device registration and uploading DATASTREAM entities to OGC Server.
  2. Listening for incoming data and publish OBSERVATIONS to OGC Broker.
"""

#############################################################################
import logging
import os
import sys
import signal
from typing import Optional

from flask import Flask, request, jsonify, make_response, Response

import scral_core as scral
from noise_app.noise_app_module import SCRALNoiseApp
from scral_core import util, rest_util
from scral_core.constants import END_MESSAGE, DEFAULT_REST_CONFIG, ENABLE_CHERRYPY, TAG_ID_KEY, \
                                 ENDPOINT_URL_KEY, ENDPOINT_PORT_KEY, MODULE_NAME_KEY
from noise_app.constants import URI_DEFAULT, URI_DEVICE, URI_ACTIVE_DEVICES

flask_instance = Flask(__name__)
scral_module: Optional[SCRALNoiseApp] = None
DOC = DEFAULT_REST_CONFIG


def main():
    module_description = "Noise app integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))

    global scral_module, DOC
    scral_module, args, DOC = util.initialize_module(module_description, abs_path, SCRALNoiseApp)
    scral_module.runtime(flask_instance, ENABLE_CHERRYPY)


@flask_instance.route(URI_DEVICE, methods=["DELETE"])
def remove_gps_tag() -> Response:
    """ This function delete all the DATASTREAM associated with a particular device
        on the resource catalog and on the OGC server.

    :return: An HTTP Response.
    """
    logging.debug(remove_gps_tag.__name__ + ", " + request.method + " method called from: " + request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status
    else:
        response = scral_module.delete_device(request.json[TAG_ID_KEY])
        return response


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices() -> Response:
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    to_ret = jsonify(scral_module.get_active_devices())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT)
def test_module() -> str:
    """ Checking if SCRAL is running. """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = DOC[ENDPOINT_URL_KEY] + ":" + str(DOC[ENDPOINT_PORT_KEY])
    deletes = (URI_DEVICE,)
    gets = (URI_ACTIVE_DEVICES,)
    to_ret = util.to_html_documentation(DOC[MODULE_NAME_KEY], link, gets=gets, deletes=deletes)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
