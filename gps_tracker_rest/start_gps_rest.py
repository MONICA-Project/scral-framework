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
from scral_module import util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE, \
                                   FILENAME_CONFIG, FILENAME_COMMAND_FILE

from gps_tracker.constants import ALERT, LOCALIZATION
from gps_tracker_rest.constants import \
    URI_GPS_TAG_REGISTRATION, URI_GPS_TAG_LOCALIZATION, URI_DEFAULT, URI_ACTIVE_DEVICES, URI_GPS_TAG_ALERT
from gps_tracker_rest.gps_rest_module import SCRALGPSRest

flask_instance = Flask(__name__)
module: SCRALGPSRest = None

MODULE_NAME: str = "SCRAL Module"
ENDPOINT_PORT: int = 8000
ENDPOINT_URL: str = "localhost"


def main():
    module_description = "SCRAL GPS REST integration instance"
    cmd_line = util.parse_small_command_line(module_description)
    pilot_config_folder = cmd_line.pilot.lower() + "/"

    # Preparing all the necessary configuration paths
    abs_path = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(abs_path, FILENAME_CONFIG)
    connection_path = os.path.join(config_path, pilot_config_folder)
    command_line_file = os.path.join(connection_path + FILENAME_COMMAND_FILE)

    # Taking and setting application parameters
    args = util.load_from_file(command_line_file)
    args["config_path"] = config_path
    args["connection_path"] = connection_path

    # OGC-Configuration
    ogc_config = SCRALGPSRest.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Initialize documentation variable
    global MODULE_NAME, ENDPOINT_PORT, ENDPOINT_URL
    MODULE_NAME = args["module_name"]
    ENDPOINT_PORT = args["endpoint_port"]
    ENDPOINT_URL = args["endpoint_url"]

    # Module initialization and runtime phase
    global module
    filename_connection = os.path.join(connection_path + args['connection_file'])
    catalog_name = args["pilot"] + "_GPS-Rest.json"
    module = SCRALGPSRest(ogc_config, filename_connection, args['pilot'], catalog_name)
    module.runtime(flask_instance, 1)


@flask_instance.route(URI_GPS_TAG_REGISTRATION, methods=["POST"])
def new_gps_tag_request():
    logging.debug(new_gps_tag_request.__name__ + " method called from: "+request.remote_addr)

    if not request.json:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)
    if module is None:
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    gps_tag_id = request.json["tagId"]

    # -> ### DATASTREAM REGISTRATION ###
    rc = module.get_resource_catalog()
    if gps_tag_id not in rc:
        logging.info("GPS tag: '" + str(gps_tag_id) + "' registration.")
        ok = module.new_datastream(request.json)
        if not ok:
            return make_response(jsonify({"Error": "Internal server error"}), 500)

        return make_response(jsonify({"result": "Ok"}), 201)

    else:
        logging.error("Device already registered!")
        return make_response(jsonify({"Error": "Duplicate request!"}), 422)


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
        return make_response(jsonify({"Error": "Wrong request!"}), 400)
    if not module:
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    gps_tag_id = payload["tagId"]
    result = module.ogc_observation_registration(observed_property, payload)
    if result is True:
        return make_response(jsonify({"result": "Ok"}), 201)
    elif result is None:
        logging.error("GPS: '" + str(gps_tag_id) + "' was not registered.")
        return make_response(jsonify({"Error": "GPS not registered!"}), 400)
    else:
        logging.error("Impossible to publish on MQTT server.")
        return make_response(jsonify({"Error": "Internal server error"}), 500)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices():
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    to_ret = jsonify(module.get_resource_catalog())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT)
def test_module():
    """ Checking if SCRAL is running. """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = ENDPOINT_URL + ":" + str(ENDPOINT_PORT)
    posts = (URI_GPS_TAG_REGISTRATION,)
    puts = (URI_GPS_TAG_LOCALIZATION, URI_GPS_TAG_ALERT)
    gets = (URI_ACTIVE_DEVICES,)
    to_ret = util.to_html_documentation(MODULE_NAME, link, posts, puts, gets)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
