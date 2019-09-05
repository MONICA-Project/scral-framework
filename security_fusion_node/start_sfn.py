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
  1. Get notified about new camera registration and creates new DATASTREAM
  2. Upload OGC Observation through MQTT
"""

#############################################################################
import logging
import os
import sys
import signal
from urllib import request

from flask import Flask, request, jsonify, make_response

import scral_module as scral
from scral_module import util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE, \
                                   FILENAME_CONFIG, FILENAME_COMMAND_FILE

from security_fusion_node.constants import CAMERA_SENSOR_TYPE, CDG_SENSOR_TYPE, \
                                           URI_DEFAULT, URI_ACTIVE_DEVICES, URI_CAMERA, URI_CDG
from security_fusion_node.sfn_module import SCRALSecurityFusionNode

flask_instance = Flask(__name__)
module: SCRALSecurityFusionNode = None

MODULE_NAME: str = "SCRAL Module"
ENDPOINT_PORT: int = 8000
ENDPOINT_URL: str = "localhost"


def main():
    module_description = "SCRAL Security Fusion Node integration instance"
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
    ogc_config = SCRALSecurityFusionNode.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Initialize documentation variable
    global MODULE_NAME, ENDPOINT_PORT, ENDPOINT_URL
    MODULE_NAME = args["module_name"]
    ENDPOINT_PORT = args["endpoint_port"]
    ENDPOINT_URL = args["endpoint_url"]

    # Module initialization and runtime phase
    global module
    filename_connection = os.path.join(connection_path + args['connection_file'])
    catalog_name = args["pilot"] + "_SFN.json"
    module = SCRALSecurityFusionNode(ogc_config, filename_connection, args['pilot'], catalog_name)
    module.runtime(flask_instance, 1)


@flask_instance.route(URI_CAMERA, methods=["POST", "PUT"])
def new_camera_request():
    """ This function can register new camera in the OGC server or store new OGC OBSERVATIONs.

    :return: An HTTP Response.
    """
    logging.debug(new_camera_request.__name__ + ", " + request.method + " method called from: "+request.remote_addr)

    if not request.json:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)

    if not module:
        logging.critical("No Security Fusion Node instantiated!")
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    if request.method == "POST":  # POST
        camera_id = request.json["camera_id"]
        rc = module.get_resource_catalog()

        if camera_id not in rc:
            logging.info("Camera: '" + str(camera_id) + "' registration.")
            response = module.ogc_datastream_registration(camera_id, CAMERA_SENSOR_TYPE, request.json)
            return response
        else:
            logging.error("Camera already registered!")
            return make_response(jsonify({"Error": "Duplicate request!"}), 422)

    elif request.method == "PUT":  # PUT
        camera_id = str(request.json['camera_ids'][0])
        logging.info("New OBSERVATION from camera: '"+str(camera_id)+"'.")
        property_type = request.json["type_module"]

        if property_type == "fighting_detection":
            observed_property = "FD-Estimation"
        elif property_type == "crowd_density_local":
            observed_property = "CDL-Estimation"
        elif property_type == "flow_analysis":
            observed_property = "FA-Estimation"
        elif property_type == "object_detection":
            observed_property = "OD-Estimation"
        elif property_type == "gate_count":
            observed_property = "GC-Estimation"
        else:
            logging.error("Unknown property: <"+property_type+">.")
            return make_response(jsonify({"Error": "Unknown property <"+property_type+">."}), 400)

        response = put_observation(camera_id, observed_property, request.json)
        return response


@flask_instance.route(URI_CDG, methods=["POST", "PUT"])
def new_cdg_request():
    """ This function can register new Crowd Density Global in the OGC server or store new OGC OBSERVATIONs.

    :return: An HTTP Response.
    """
    logging.debug(new_cdg_request.__name__ + ", " + request.method + " method called from: "+request.remote_addr)

    if not request.json:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)

    cdg_module_id = request.json["module_id"]  # NB: module here is Crowd Density Global module

    if not module:
        logging.critical("No Security Fusion Node instantiated!")
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    if request.method == "POST":  # POST
        rc = module.get_resource_catalog()
        if cdg_module_id not in rc:
            logging.info("CDG: '" + str(cdg_module_id) + "' registration.")
            response = module.ogc_datastream_registration(cdg_module_id, CDG_SENSOR_TYPE, request.json)
            return response
        else:
            logging.error("CDG module already registered!")
            return make_response(jsonify({"Error": "Duplicate request!"}), 422)

    elif request.method == "PUT":  # PUT
        logging.info("New OBSERVATION from CDG: '" + str(cdg_module_id))

        property_type = request.json["type_module"]
        request.json["timestamp"] = request.json.pop("timestamp_1")  # renaming "timestamp_1" to "timestamp"

        if property_type == "crowd_density_global":
            observed_property = "CDG-Estimation"
        else:
            logging.error("Unknown property.")
            return make_response(jsonify({"Error": "Unknown property."}), 400)

        response = put_observation(cdg_module_id, observed_property, request.json)
        return response


def put_observation(resource_id, observed_property, payload):
    """ This function stores an OBSERVATION on OGC server.

    :param resource_id: The id of the resource.
    :param observed_property: The name of the OBSERVED PROPERTY
    :param payload: The payload to store.
    :return: An HTTP response.
    """
    if not payload:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)
    if not module:
        logging.critical("No Security Fusion Node instantiated!")
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    result = module.ogc_observation_registration(resource_id, observed_property, payload)
    if result is True:
        return make_response(jsonify({"result": "Ok"}), 201)
    elif result is None:
        logging.error("Device: '" + str(resource_id) + "' was not registered.")
        return make_response(jsonify({"Error": "Device: '" + str(resource_id) + "' was not registered!"}), 400)
    else:
        logging.error("Impossible to publish on MQTT server.")
        return make_response(jsonify({"Error": "Internal server error"}), 500)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices():
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    to_ret = jsonify(module.get_active_devices())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module():
    """ Checking if SCRAL is running.
    :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = ENDPOINT_URL + ":" + str(ENDPOINT_PORT)
    posts = (URI_CAMERA, URI_CDG)
    puts = (URI_CAMERA, URI_CDG)
    gets = (URI_ACTIVE_DEVICES, )
    to_ret = util.to_html_documentation(MODULE_NAME, link, posts, puts, gets)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
