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
  1. Get notified about new camera registration and creates new DATASTREAM
  2. Upload OGC Observation through MQTT
"""

#############################################################################
import logging
import os
import sys
import signal
from typing import Optional
from urllib import request

from flask import Flask, request, jsonify, make_response, Response

import scral_core as scral
from scral_core import util, rest_util
from scral_core.constants import END_MESSAGE, ENABLE_CHERRYPY, DEFAULT_REST_CONFIG, SUCCESS_RETURN_STRING, \
                                   ENDPOINT_PORT_KEY, ENDPOINT_URL_KEY, MODULE_NAME_KEY, TIMESTAMP_KEY, \
                                   ERROR_RETURN_STRING, WRONG_REQUEST, INTERNAL_SERVER_ERROR, DUPLICATE_REQUEST, \
                                   UNKNOWN_PROPERTY, WRONG_PAYLOAD_REQUEST

from security_fusion_node.constants import CAMERA_SENSOR_TYPE, CDG_SENSOR_TYPE, CDG_PROPERTY, \
                                           URI_DEFAULT, URI_ACTIVE_DEVICES, URI_CAMERA, URI_CDG, \
                                           CAMERA_ID_KEY, CAMERA_IDS_KEY, MODULE_ID_KEY, TYPE_MODULE_KEY, CDG_KEY, \
                                           FIGHT_KEY, CROWD_KEY, FLOW_KEY, OBJECT_KEY, GATE_COUNT_KEY
from security_fusion_node.sfn_module import SCRALSecurityFusionNode

flask_instance = Flask(__name__)
scral_module: Optional[SCRALSecurityFusionNode] = None
DOC = DEFAULT_REST_CONFIG


def main():
    module_description = "SCRAL Security Fusion Node integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))

    global scral_module, DOC
    scral_module, args, DOC = util.initialize_module(module_description, abs_path, SCRALSecurityFusionNode)
    scral_module.runtime(flask_instance, ENABLE_CHERRYPY)


@flask_instance.route(URI_CAMERA, methods=["POST", "PUT", "DELETE"])
def camera_request() -> Response:
    """ This function can register new camera in the OGC server or store new OGC OBSERVATIONs.

    :return: An HTTP Response.
    """
    logging.debug(camera_request.__name__ + ", " + request.method + " method called from: " + request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status

    if request.method == "POST":  # POST
        camera_id = request.json[CAMERA_ID_KEY]
        rc = scral_module.get_resource_catalog()

        if camera_id not in rc:
            logging.info('Camera: "' + str(camera_id) + '" registration.')
            response = scral_module.ogc_datastream_registration(camera_id, CAMERA_SENSOR_TYPE, request.json)
        else:
            logging.error("Camera already registered!")
            response = make_response(jsonify({ERROR_RETURN_STRING: DUPLICATE_REQUEST}), 422)
        return response

    elif request.method == "PUT":  # PUT
        camera_id = str(request.json[CAMERA_IDS_KEY][0])
        logging.info("New OBSERVATION from camera: '"+str(camera_id)+"'.")
        property_type = request.json[TYPE_MODULE_KEY]

        if property_type == FIGHT_KEY:
            observed_property = "FD-Estimation"
        elif property_type == CROWD_KEY:
            observed_property = "CDL-Estimation"
        elif property_type == FLOW_KEY:
            observed_property = "FA-Estimation"
        elif property_type == OBJECT_KEY:
            observed_property = "OD-Estimation"
        elif property_type == GATE_COUNT_KEY:
            observed_property = "GC-Estimation"
        else:
            logging.error("Unknown property: <"+property_type+">.")
            return make_response(jsonify({ERROR_RETURN_STRING: "Unknown property <"+property_type+">."}), 400)

        response = put_observation(camera_id, observed_property, request.json)
        return response

    elif request.method == "DELETE":
        try:
            camera_id = request.json[CAMERA_ID_KEY]
            logging.info('Try to delete camera: "'+camera_id+'"')
            response = scral_module.delete_device(camera_id)
        except KeyError:
            logging.error("Missing "+CAMERA_ID_KEY+". Delete aborted.")
            response = make_response(jsonify({ERROR_RETURN_STRING: WRONG_PAYLOAD_REQUEST}), 400)
        return response
    else:
        logging.critical("Unauthorized method!")
        return make_response(jsonify({ERROR_RETURN_STRING: WRONG_REQUEST}), 405)


@flask_instance.route(URI_CDG, methods=["POST", "PUT", "DELETE"])
def cdg_request() -> Response:
    """ This function can register new Crowd Density Global in the OGC server or store new OGC OBSERVATIONs.

    :return: An HTTP Response.
    """
    logging.debug(cdg_request.__name__ + ", " + request.method + " method called from: " + request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status

    cdg_module_id = None
    try:
        cdg_module_id = request.json[MODULE_ID_KEY]  # NB: module here is Crowd Density Global module
    except KeyError:
        logging.error("Missing " + MODULE_ID_KEY + ". Request aborted.")
        return make_response(jsonify({ERROR_RETURN_STRING: WRONG_PAYLOAD_REQUEST}), 400)

    if request.method == "POST":  # POST
        rc = scral_module.get_resource_catalog()
        if cdg_module_id not in rc:
            logging.info("CDG: '" + str(cdg_module_id) + "' registration.")
            response = scral_module.ogc_datastream_registration(cdg_module_id, CDG_SENSOR_TYPE, request.json)
        else:
            logging.error("CDG module already registered!")
            response = make_response(jsonify({ERROR_RETURN_STRING: DUPLICATE_REQUEST}), 422)
        return response

    elif request.method == "PUT":  # PUT
        logging.info("New OBSERVATION from CDG: '" + str(cdg_module_id))

        property_type = request.json[TYPE_MODULE_KEY]
        request.json[TIMESTAMP_KEY] = request.json.pop("timestamp_1")  # renaming "timestamp_1" to "timestamp"

        if property_type == CDG_KEY:
            observed_property = CDG_PROPERTY
        else:
            logging.error("Unknown property.")
            return make_response(jsonify({ERROR_RETURN_STRING: UNKNOWN_PROPERTY}), 400)

        response = put_observation(cdg_module_id, observed_property, request.json)
        return response

    elif request.method == "DELETE":  # DELETE
        logging.info('Try to delete CDG: "'+cdg_module_id+'"')
        response = scral_module.delete_device(cdg_module_id)
        return response

    else:
        logging.critical("Unauthorized method!")
        return make_response(jsonify({ERROR_RETURN_STRING: WRONG_REQUEST}), 405)


def put_observation(resource_id: str, observed_property: str, payload: dict) -> Response:
    """ This function stores an OBSERVATION on OGC server.

    :param resource_id: The id of the resource.
    :param observed_property: The name of the OBSERVED PROPERTY
    :param payload: The payload to store.
    :return: An HTTP response.
    """
    if not payload:
        return make_response(jsonify({ERROR_RETURN_STRING: WRONG_REQUEST}), 400)
    if not scral_module:
        logging.critical("No Security Fusion Node instantiated!")
        return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)

    result = scral_module.ogc_observation_registration(resource_id, observed_property, payload)
    if result is True:
        return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)
    elif result is None:
        logging.error("Device: '" + str(resource_id) + "' was not registered.")
        return make_response(jsonify({ERROR_RETURN_STRING: "Device: '" + str(resource_id) + "' was not registered!"}), 400)
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
    logging.debug(test_module.__name__+" method called from: "+request.remote_addr)

    link = DOC[ENDPOINT_URL_KEY] + ":" + str(DOC[ENDPOINT_PORT_KEY])
    deletes = posts = (URI_CAMERA, URI_CDG)
    puts = (URI_CAMERA, URI_CDG)
    gets = (URI_ACTIVE_DEVICES, )
    to_ret = util.to_html_documentation(DOC[MODULE_NAME_KEY], link, posts, puts, gets, deletes)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
