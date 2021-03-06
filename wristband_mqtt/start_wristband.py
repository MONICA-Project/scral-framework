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
import logging
import os
import sys
import signal
from typing import Optional

from flask import Flask, request, jsonify, make_response, Response

from scral_core.constants import END_MESSAGE, DEFAULT_REST_CONFIG, SUCCESS_RETURN_STRING, ENABLE_CHERRYPY, \
                                 ENDPOINT_URL_KEY, ENDPOINT_PORT_KEY, MODULE_NAME_KEY, \
                                 ERROR_RETURN_STRING, INTERNAL_SERVER_ERROR
import scral_core as scral
from scral_core import util, rest_util

from wristband.constants import TAG_ID_KEY, URI_DEFAULT, URI_ACTIVE_DEVICES, URI_WRISTBAND
from wristband_mqtt.constants import DEFAULT_SUBSCRIPTION_WB
from wristband_mqtt.wristband_mqtt_module import SCRALMQTTWristband

flask_instance = Flask(__name__)
scral_module: Optional[SCRALMQTTWristband] = None
DOC = DEFAULT_REST_CONFIG


def main():
    module_description = "Wristband MQTT integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))

    global scral_module, DOC
    scral_module, args, DOC = util.initialize_module(module_description, abs_path, SCRALMQTTWristband)
    scral_module.mqtt_subscriptions(DEFAULT_SUBSCRIPTION_WB)
    scral_module.runtime(flask_instance, ENABLE_CHERRYPY)


@flask_instance.route(URI_WRISTBAND, methods=["POST", "DELETE"])
def wristband_request() -> Response:
    logging.debug(wristband_request.__name__ + " method called from: " + request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status

    wristband_id = request.json[TAG_ID_KEY]

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
                                    posts=(URI_WRISTBAND,),
                                    deletes=(URI_WRISTBAND,)
    )
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
