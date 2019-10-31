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
  0. SEE SCRALRestModule for previous steps.

PHASE: INTEGRATION
  1. Get notified about new glasses registration and creates new DATASTREAM
  2. Upload OGC Observation through MQTT
"""

#############################################################################
import copy
import logging
import os
import sys
import signal
from typing import Optional

from flask import Flask, request, jsonify, make_response, Response

from scral_ogc import OGCObservedProperty

import scral_core as scral
from scral_core import util, rest_util
from scral_core.constants import DEFAULT_REST_CONFIG, ENABLE_CHERRYPY, END_MESSAGE, SUCCESS_RETURN_STRING, \
                                 ENDPOINT_URL_KEY, ENDPOINT_PORT_KEY, MODULE_NAME_KEY, PILOT_KEY, \
                                 ERROR_RETURN_STRING, INTERNAL_SERVER_ERROR, DEVICE_NOT_REGISTERED

from sound_level_meter.slm_module import SCRALSoundLevelMeter
from sound_level_meter.constants import URL_SLM_LOGIN, CREDENTIALS, SLM_LOGIN_PREFIX, \
    URI_DEFAULT, URI_ACTIVE_DEVICES, URI_SOUND_EVENT,URI_RESOURCE_CATALOG,  \
    DEVICE_ID_KEY, DEVICE_NAME_KEY, DESCRIPTION_KEY, DEFINITION_KEY, TYPE_KEY, START_TIME_KEY

flask_instance = Flask(__name__)
scral_module: Optional[SCRALSoundLevelMeter] = None
DOC = DEFAULT_REST_CONFIG


def main():
    global scral_module, DOC

    module_description = "Sound Level Meter integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))
    args, DOC = util.initialize_variables(module_description, abs_path)

    ogc_config, filename_connection, catalog_name = util.scral_ogc_startup(SCRALSoundLevelMeter, args)
    scral_module = SCRALSoundLevelMeter(ogc_config, filename_connection, args[PILOT_KEY],
                                        URL_SLM_LOGIN, CREDENTIALS, catalog_name, SLM_LOGIN_PREFIX)
    scral_module.runtime(flask_instance, ENABLE_CHERRYPY)


@flask_instance.route(URI_SOUND_EVENT, methods=["PUT"])
def new_sound_event() -> Response:
    """ This function can register an OBSERVATION in the OGC server.
        It is able to accept any new OBSERVED PROPERTY according to the content of "type" field.
        This new property is run-time generated.

    :return: An HTTP Response.
    """
    logging.debug(new_sound_event.__name__ + " method called from: "+request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status

    payload = request.json
    property_name = payload[TYPE_KEY]
    try:
        property_description = payload[DESCRIPTION_KEY]
    except KeyError:
        property_description = property_name + " description"
    try:
        property_definition = payload[DEFINITION_KEY]
    except KeyError:
        property_definition = property_name + " definition"

    obs_prop = OGCObservedProperty(property_name, property_description, property_definition)
    device_id = payload[DEVICE_ID_KEY]

    datastream_id = scral_module.new_datastream(device_id, obs_prop)
    if datastream_id is False:
        return make_response(jsonify({ERROR_RETURN_STRING: DEVICE_NOT_REGISTERED}), 400)
    elif datastream_id is None:
        return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)
    else:
        scral_module.ogc_observation_registration(datastream_id, payload[START_TIME_KEY], payload)
        return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices() -> Response:
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    rc_copy = copy.deepcopy(scral_module.get_resource_catalog())
    new_rc = {}
    for item in rc_copy.values():
        key = item.pop(DEVICE_NAME_KEY)
        new_rc[key] = item

    return make_response(jsonify(new_rc), 200)


@flask_instance.route(URI_RESOURCE_CATALOG, methods=["GET"])
def get_resource_catalog() -> Response:
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_resource_catalog.__name__ + " method called from: "+request.remote_addr)
    return make_response(jsonify(scral_module.get_resource_catalog()), 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module() -> str:
    """ Checking if SCRAL is running.
        :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = DOC[ENDPOINT_URL_KEY]+":"+str(DOC[ENDPOINT_PORT_KEY])
    posts = ()
    puts = (URI_SOUND_EVENT, )
    gets = (URI_ACTIVE_DEVICES, )
    to_ret = util.to_html_documentation(DOC[MODULE_NAME_KEY], link, posts, puts, gets)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
