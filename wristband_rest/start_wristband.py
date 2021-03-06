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

"""
#############################################################################
import json
import logging
import os
import sys
import signal
from typing import Optional

from flask import Flask, request, jsonify, make_response, Response

from scral_core.constants import END_MESSAGE, DEFAULT_REST_CONFIG, ENABLE_CHERRYPY, SUCCESS_RETURN_STRING, \
                                 ENDPOINT_URL_KEY, ENDPOINT_PORT_KEY, MODULE_NAME_KEY, \
                                 ERROR_RETURN_STRING, INTERNAL_SERVER_ERROR, WRONG_REQUEST, NO_MQTT_PUBLICATION
import scral_core as scral
from scral_core import util, rest_util

from wristband.constants import TAG_ID_KEY, ID1_ASSOCIATION_KEY, ID2_ASSOCIATION_KEY, \
                                PROPERTY_BUTTON_NAME, PROPERTY_LOCALIZATION_NAME, SENSOR_ASSOCIATION_NAME, \
                                URI_DEFAULT, URI_ACTIVE_DEVICES
from wristband.wristband_module import SCRALWristband

from wristband_rest.constants import URI_WRISTBAND_BUTTON, URI_WRISTBAND_LOCALIZATION, \
                                     URI_WRISTBAND, URI_WRISTBAND_ASSOCIATION

flask_instance = Flask(__name__)
scral_module: Optional[SCRALWristband] = None
DOC = DEFAULT_REST_CONFIG


def main():
    module_description = "Wristband REST integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))

    global scral_module, DOC
    scral_module, args, DOC = util.initialize_module(module_description, abs_path, SCRALWristband)
    scral_module.runtime(flask_instance, ENABLE_CHERRYPY)


@flask_instance.route(URI_WRISTBAND, methods=["POST", "DELETE"])
def wristband_request() -> Response:
    logging.debug(wristband_request.__name__ + " method called from: " + request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status

    try:
        wristband_id = request.json[TAG_ID_KEY]
    except KeyError as ke:
        logging.error("Inside request missing field: " + str(ke))
        return make_response(jsonify({ERROR_RETURN_STRING: WRONG_REQUEST}), 400)

    if request.method == "POST":  # Device Registration
        rc = scral_module.get_resource_catalog()
        if wristband_id not in rc:
            logging.info("Wristband: '" + str(wristband_id) + "' registration.")
        else:
            logging.warning("Device '" + str(wristband_id) + "' already registered... It will be overwritten on RC!")

        ok = scral_module.ogc_datastream_registration(wristband_id, request.json)
        if not ok:
            return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)
        else:
            return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)

    elif request.method == "DELETE":  # Remove Device
        response = scral_module.delete_device(wristband_id)
        return response


@flask_instance.route(URI_WRISTBAND_ASSOCIATION, methods=["PUT"])
def new_wristband_association_request() -> Response:
    logging.debug(new_wristband_association_request.__name__+" method called from: "+request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status

    wristband_id_1 = request.json[ID1_ASSOCIATION_KEY]
    wristband_id_2 = request.json[ID2_ASSOCIATION_KEY]

    rc = scral_module.get_resource_catalog()
    if wristband_id_1 not in rc or wristband_id_2 not in rc:
        logging.error("One of the wristbands is not registered.")
        return make_response(jsonify({ERROR_RETURN_STRING: "One of the wristbands is not registered!"}), 400)

    vds = scral_module.get_ogc_config().get_virtual_datastream(SENSOR_ASSOCIATION_NAME)
    if not vds:
        logging.critical('No Virtual DATASTREAM registered for Virtual SENSOR: "' + SENSOR_ASSOCIATION_NAME + '"')
        return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)

    result = scral_module.ogc_service_observation_registration(vds, request.json)
    if result is True:
        return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)
    else:
        logging.error("Impossible to publish on MQTT server.")
        return make_response(jsonify({ERROR_RETURN_STRING: NO_MQTT_PUBLICATION}), 502)


@flask_instance.route(URI_WRISTBAND_LOCALIZATION, methods=["PUT"])
def new_wristband_localization() -> Response:
    logging.debug(new_wristband_localization.__name__ + " method called from: "+request.remote_addr)

    response = put_observation(PROPERTY_LOCALIZATION_NAME, request.json)
    return response


@flask_instance.route(URI_WRISTBAND_BUTTON, methods=["PUT"])
def new_wristband_button() -> Response:
    logging.debug(new_wristband_button.__name__ + " method called from: "+request.remote_addr)

    response = put_observation(PROPERTY_BUTTON_NAME, request.json)
    return response


def put_observation(observed_property: str, payload: json) -> Response:
    if not payload:
        return make_response(jsonify({ERROR_RETURN_STRING: WRONG_REQUEST}), 400)
    if not scral_module:
        return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)

    try:
        wristband_id = payload[TAG_ID_KEY]
    except KeyError as ke:
        logging.error("Inside request missing field: " + str(ke))
        return make_response(jsonify({ERROR_RETURN_STRING: WRONG_REQUEST}), 400)

    result = scral_module.ogc_observation_registration(observed_property, payload)
    if result is True:
        return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)
    elif result is None:
        logging.error("Wristband: '" + str(wristband_id) + "' was not registered.")
        return make_response(jsonify({ERROR_RETURN_STRING: "Wristband not registered!"}), 400)
    else:
        logging.error("Impossible to publish on MQTT server.")
        return make_response(jsonify({ERROR_RETURN_STRING: NO_MQTT_PUBLICATION}), 502)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices() -> Response:
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__+" method called from: "+request.remote_addr)

    to_ret = jsonify(scral_module.get_active_devices())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module() -> str:
    """ Checking if SCRAL is running.
    :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    to_ret = util.to_html_documentation(
                                    module_name=DOC[MODULE_NAME_KEY],
                                    link=DOC[ENDPOINT_URL_KEY] + ":" + str(DOC[ENDPOINT_PORT_KEY]),
                                    gets=(URI_ACTIVE_DEVICES,),
                                    posts=(URI_WRISTBAND, ),
                                    deletes=(URI_WRISTBAND, ),
                                    puts=(URI_WRISTBAND_ASSOCIATION, URI_WRISTBAND_LOCALIZATION, URI_WRISTBAND_BUTTON)
    )
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
