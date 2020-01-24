#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
  0. SEE SCRALRestModule for previous steps.

PHASE: INTEGRATION
  1. Get notified about new glasses registration and creates new DATASTREAM
  2. Upload OGC Observation through MQTT
"""

#############################################################################
import logging
import os
import sys
import signal
from typing import Optional

from flask import Flask, request, jsonify, make_response, Response

import scral_core as scral
from scral_core.constants import END_MESSAGE, DEFAULT_REST_CONFIG, ENABLE_CHERRYPY, SUCCESS_RETURN_STRING, \
                                   MODULE_NAME_KEY, ENDPOINT_PORT_KEY, ENDPOINT_URL_KEY, \
                                   ERROR_RETURN_STRING, INTERNAL_SERVER_ERROR, DUPLICATE_REQUEST, \
                                   DEVICE_NOT_REGISTERED
from scral_core import util, rest_util


from smart_glasses.constants import PROPERTY_LOCALIZATION_NAME, PROPERTY_INCIDENT_NAME, TAG_ID_KEY, TYPE_KEY, \
    URI_DEFAULT, URI_ACTIVE_DEVICES, URI_GLASSES_REGISTRATION, URI_GLASSES_LOCALIZATION, URI_GLASSES_INCIDENT
from smart_glasses.smart_glasses_module import SCRALSmartGlasses

flask_instance = Flask(__name__)
scral_module: Optional[SCRALSmartGlasses] = None
DOC = DEFAULT_REST_CONFIG


def main():
    module_description = "Smart Glasses integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))

    global scral_module, DOC
    scral_module, args, DOC = util.initialize_module(module_description, abs_path, SCRALSmartGlasses)
    scral_module.runtime(flask_instance, ENABLE_CHERRYPY)


@flask_instance.route(URI_GLASSES_REGISTRATION, methods=["POST", "DELETE"])
def glasses_request() -> Response:
    """ This function can register new glasses in the OGC server.
    :return: An HTTP Response.
    """
    logging.debug(glasses_request.__name__ + " method called from: " + request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status

    glasses_id = request.json[TAG_ID_KEY]

    if request.method == "POST":  # POST
        # -> ### DATASTREAM REGISTRATION ###
        rc = scral_module.get_resource_catalog()
        if glasses_id in rc:
            logging.error("Device already registered!")
            return make_response(jsonify({ERROR_RETURN_STRING: DUPLICATE_REQUEST}), 422)

        logging.info("Glasses: '" + str(glasses_id) + "' registration.")
        ok = scral_module.ogc_datastream_registration(glasses_id)
        if not ok:
            return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)
        else:
            return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)

    elif request.method == "DELETE":  # DELETE
        response = scral_module.delete_device(glasses_id)
        return response


@flask_instance.route(URI_GLASSES_LOCALIZATION, methods=["PUT"])
def new_glasses_localization() -> Response:
    """ This function can register new glasses location in the OGC server.
    :return: An HTTP Response.
    """
    logging.debug(new_glasses_localization.__name__ + " method called from: "+request.remote_addr)
    response = put_observation(PROPERTY_LOCALIZATION_NAME, request.json)
    return response


@flask_instance.route(URI_GLASSES_INCIDENT, methods=["PUT"])
def new_glasses_incident() -> Response:
    """ This function can register new glasses incident in the OGC server.
    :return: An HTTP Response.
    """
    logging.debug(new_glasses_incident.__name__ + " method called from: "+request.remote_addr)

    response = put_observation(PROPERTY_INCIDENT_NAME, request.json)
    return response


def put_observation(observed_property: str, payload: dict) -> Response:
    """ This function is used to store a new OBSERVATION in the OGC Server.

    :param observed_property: The type of property
    :param payload: The payload of the observation
    :return: An HTTP request.
    """
    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status

    glasses_id = payload[TAG_ID_KEY]
    result = scral_module.ogc_observation_registration(observed_property, payload)
    if result is True:
        return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)
    elif result is None:
        logging.error("Glasses: '" + str(glasses_id) + "' was not registered.")
        return make_response(jsonify({ERROR_RETURN_STRING: DEVICE_NOT_REGISTERED}), 400)
    else:
        logging.error("Impossible to publish on MQTT server.")
        return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices() -> Response:
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    to_ret = jsonify(scral_module.get_active_devices())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module() -> str:
    """ Checking if SCRAL is running.
        :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = DOC[ENDPOINT_URL_KEY] + ":" + str(DOC[ENDPOINT_PORT_KEY])
    deletes = posts = (URI_GLASSES_REGISTRATION, )
    puts = (URI_GLASSES_LOCALIZATION, URI_GLASSES_INCIDENT)
    gets = (URI_ACTIVE_DEVICES, )
    to_ret = util.to_html_documentation(DOC[MODULE_NAME_KEY], link, posts, puts, gets, deletes)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
