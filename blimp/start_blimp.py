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
  0. SEE SCRALRestModule for previous steps.

PHASE: INTEGRATION
  1. Get notified about new blimps
  2. Upload DATASTREAM entities to OGC Server
  3. Upload new OGC OBSERVATION through MQTT
"""

##############################################################################
import logging
import os
import signal
import sys
from typing import Optional

from flask import Flask, request, jsonify, make_response, Response

import scral_core as scral
from scral_core import util, rest_util
from scral_core.constants import END_MESSAGE, ENABLE_CHERRYPY, DEFAULT_REST_CONFIG, \
                                 MODULE_NAME_KEY, ENDPOINT_PORT_KEY, ENDPOINT_URL_KEY, CATALOG_NAME_KEY, PILOT_KEY, \
                                 ERROR_RETURN_STRING, NO_DATASTREAM_ID

from blimp.constants import URI_DEFAULT, URI_ACTIVE_DEVICES, BLIMP_ID_KEY, BLIMP_NAME_KEY
from blimp.blimp_module import SCRALBlimp

flask_instance = Flask(__name__)
scral_module: Optional[SCRALBlimp] = None
BLIMP_NAME = "blimp"

DOC = DEFAULT_REST_CONFIG


def main():
    module_description = "SCRAL Blimps integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))
    global scral_module, DOC
    scral_module, args, doc = util.initialize_module(module_description, abs_path, SCRALBlimp)

    # Taking additional parameters
    global BLIMP_NAME
    try:
        BLIMP_NAME = args[BLIMP_NAME_KEY]
    except KeyError:
        logging.warning("No "+BLIMP_NAME_KEY+" specified. Default name was used '"+BLIMP_NAME+"'")
    try:
        catalog_name = args[CATALOG_NAME_KEY]
    except KeyError:
        catalog_name = args[PILOT_KEY] + "_Blimp.json"
        logging.warning("No "+CATALOG_NAME_KEY+" specified. Default name was used '"+catalog_name+"'")

    # runtime
    scral_module.runtime(flask_instance, ENABLE_CHERRYPY)


@flask_instance.route(URI_DEFAULT, methods=["POST"])
def new_blimp_registration() -> Response:
    """ This function can register a new Blimp in the OGC server. """
    logging.debug(new_blimp_registration.__name__+", "+request.method+" method called from: "+request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status
    else:
        response = scral_module.ogc_datastream_registration(request.json)
        return response


@flask_instance.route(URI_DEFAULT, methods=["DELETE"])
def remove_blimp() -> Response:
    """ This function delete all the DATASTREAM associated with a particular Blimp
        on the resource catalog and on the OGC server.

    :return: An HTTP Response.
    """
    logging.debug(remove_blimp.__name__ + ", " + request.method + " method called from: " + request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status
    else:
        response = scral_module.delete_device(request.json[BLIMP_ID_KEY])
        return response


@flask_instance.route(URI_DEFAULT+"/Datastreams(<datastream_id>)/Observations", methods=["PUT"])
def new_blimp_observation(datastream_id: Optional[int] = None) -> Response:
    """ This function can register a new Blimp in the OGC server. """
    logging.debug(new_blimp_observation.__name__ + ", " + request.method + " method called from: " + request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status
    elif datastream_id is None:
        logging.error("Missing DATASTREAM ID!")
        return make_response(jsonify({ERROR_RETURN_STRING: NO_DATASTREAM_ID}), 400)
    else:
        # Just for this particular case
        try:
            blimp_name = request.json[BLIMP_ID_KEY]
        except KeyError:
            request.json[BLIMP_ID_KEY] = BLIMP_NAME

        response = scral_module.ogc_observation_registration(datastream_id, request.json)
        return response


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices() -> Response:
    """ This endpoint gives access to the resource catalog. """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    to_ret = jsonify(scral_module.get_active_devices())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module() -> str:
    """ Checking if SCRAL is running.
        :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = DOC[ENDPOINT_URL_KEY]+":"+str(DOC[ENDPOINT_PORT_KEY])
    deletes = posts = (URI_DEFAULT,)
    puts = (URI_DEFAULT+"/Datastreams(id)/Observations",)
    gets = (URI_ACTIVE_DEVICES, )
    return util.to_html_documentation(DOC[MODULE_NAME_KEY], link, posts, puts, gets, deletes)


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
