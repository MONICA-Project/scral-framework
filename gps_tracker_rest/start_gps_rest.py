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

from flask import Flask, request, jsonify, make_response

import scral_module as scral
from scral_module import util, rest_util
from scral_module.constants import END_MESSAGE, DEFAULT_REST_CONFIG, ENABLE_CHERRYPY, \
                                   SUCCESS_RETURN_STRING, ENDPOINT_URL_KEY, ENDPOINT_PORT_KEY, MODULE_NAME_KEY, \
                                   ERROR_RETURN_STRING, WRONG_REQUEST, INTERNAL_SERVER_ERROR, DUPLICATE_REQUEST, \
                                   DEVICE_NOT_REGISTERED

from gps_tracker.constants import ALERT, LOCALIZATION
from gps_tracker_rest.constants import TAG_ID_KEY, \
    URI_GPS_TAG_REGISTRATION, URI_GPS_TAG_LOCALIZATION, URI_DEFAULT, URI_ACTIVE_DEVICES, URI_GPS_TAG_ALERT
from gps_tracker_rest.gps_rest_module import SCRALGPSRest

flask_instance = Flask(__name__)
scral_module: SCRALGPSRest = None
DOC = DEFAULT_REST_CONFIG


def main():
    module_description = "SCRAL GPS REST integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))

    global scral_module, DOC
    scral_module, args, DOC = util.initialize_module(module_description, abs_path, SCRALGPSRest)
    scral_module.runtime(flask_instance, ENABLE_CHERRYPY)


@flask_instance.route(URI_GPS_TAG_REGISTRATION, methods=["POST"])
def new_gps_tag_request():
    logging.debug(new_gps_tag_request.__name__ + " method called from: "+request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status

    gps_tag_id = request.json["tagId"]

    # -> ### DATASTREAM REGISTRATION ###
    rc = scral_module.get_resource_catalog()
    if gps_tag_id not in rc:
        logging.info("GPS tag: '" + str(gps_tag_id) + "' registration.")
        ok = scral_module.new_datastream(request.json)
        if not ok:
            return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)

        return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)

    else:
        logging.error("Device already registered!")
        return make_response(jsonify({ERROR_RETURN_STRING: DUPLICATE_REQUEST}), 422)


@flask_instance.route(URI_GPS_TAG_REGISTRATION, methods=["DELETE"])
def remove_gps_tag():
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


@flask_instance.route(URI_GPS_TAG_LOCALIZATION, methods=["PUT"])
def new_gps_tag_localization():
    logging.debug(new_gps_tag_alert.__name__ + " method called from: "+request.remote_addr)

    response = put_observation(LOCALIZATION, request.json)
    return response


@flask_instance.route(URI_GPS_TAG_ALERT, methods=["PUT"])
def new_gps_tag_alert():
    logging.debug(new_gps_tag_alert.__name__ + " method called from: "+request.remote_addr)

    response = put_observation(ALERT, request.json)
    return response


def put_observation(observed_property, payload):
    if not payload:
        return make_response(jsonify({ERROR_RETURN_STRING: WRONG_REQUEST}), 400)
    if not scral_module:
        return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)

    gps_tag_id = payload["tagId"]
    result = scral_module.ogc_observation_registration(observed_property, payload)
    if result is True:
        return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)
    elif result is None:
        logging.error("GPS: '" + str(gps_tag_id) + "' was not registered.")
        return make_response(jsonify({ERROR_RETURN_STRING: DEVICE_NOT_REGISTERED}), 400)
    else:
        logging.error("Impossible to publish on MQTT server.")
        return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices():
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    to_ret = jsonify(scral_module.get_active_devices())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT)
def test_module():
    """ Checking if SCRAL is running. """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = DOC[ENDPOINT_URL_KEY] + ":" + str(DOC[ENDPOINT_PORT_KEY])
    deletes = posts = (URI_GPS_TAG_REGISTRATION,)
    puts = (URI_GPS_TAG_LOCALIZATION, URI_GPS_TAG_ALERT)
    gets = (URI_ACTIVE_DEVICES,)
    to_ret = util.to_html_documentation(DOC[MODULE_NAME_KEY], link, posts, puts, gets, deletes)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
