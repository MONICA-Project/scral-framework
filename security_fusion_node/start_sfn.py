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
#
# ROADMAP: these are main steps in which a SCRAL module is divided.
#
# PHASE: INIT + SETUP + BOOT
#   1. Init variables and setup server and MQTT connections
#   2. Read configuration File and load predefined OGC scheme (exit if integrity not satisfied)
#
# #PHASE: DISCOVERY
#   3. Check via discovery if loaded entities are already registered
#   4. If needed, register new entities    to OGC Server
#   5. Retrieve corresponding @iot.id's
#
# #PHASE: INTEGRATION
#   6. Get notified about new OneM2M "containers"
#   7. Upload DATASTREAM entities to OGC Server
#   8. Expose SCRAL endpoint and listen to incoming requests
#
####################################################################################################
import logging
import sys
import signal
from urllib import request

from flask import Flask, request, jsonify, make_response

import scral_module as scral
from scral_module import util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE

from security_fusion_node.constants import URI_DEFAULT, URI_CAMERA, URI_CDG, CAMERA_SENSOR_TYPE, CDG_SENSOR_TYPE
from security_fusion_node.sfn_module import SCRALSecurityFusionNode

flask_instance = Flask(__name__)
module: SCRALSecurityFusionNode = None


def main():
    module_description = "Smart Glasses integration instance"
    args = util.parse_command_line(module_description)

    # OGC-Configuration
    ogc_config = SCRALSecurityFusionNode.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Module initialization and runtime phase
    global module
    module = SCRALSecurityFusionNode(ogc_config, args.connection_file, args.pilot)
    module.runtime(flask_instance)


@flask_instance.route(URI_CAMERA, methods=["POST", "PUT"])
def new_camera_request():
    logging.debug(new_camera_request.__name__ + ", " + request.method + " method called")

    if not request.json:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)

    camera_id = request.json["camera_id"]

    if not module:
        logging.critical("No Security Fusion Node instantiated!")
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    if request.method == "POST":  # POST
        rc = module.get_resource_catalog()
        if camera_id not in rc:
            logging.info("Camera: '" + str(camera_id) + "' registration.")
            response = module.ogc_datastream_registration(camera_id, CAMERA_SENSOR_TYPE, request.json)
            return response
        else:
            logging.error("Camera already registered!")
            return make_response(jsonify({"Error": "Duplicate request!"}), 422)

    elif request.method == "PUT":  # PUT
        logging.info("New OBSERVATION from camera: '" + str(camera_id))
        property_type = request.json["type_module"]

        if property_type == "fighting_detection":
            observed_property = "FD-Estimation"
        elif property_type == "crowd_density_local":
            observed_property = "CDL-Estimation"
        elif property_type == "flow_analysis":
            observed_property = "FA-Estimation"
        elif property_type == "object_detection":
            observed_property = "OD-Estimation"
        elif property_type == "gate_count ":
            observed_property = "GC-Estimation"
        else:
            logging.error("Unknown property.")
            return make_response(jsonify({"Error": "Unknown property."}), 400)

        response = put_observation(observed_property, request.json, camera_id)
        return response


@flask_instance.route(URI_CDG, methods=["POST", "PUT"])
def new_cdg_request():
    logging.debug(new_cdg_request.__name__ + ", " + request.method + " method called")

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

        response = put_observation(observed_property, request.json, cdg_module_id)
        return response


def put_observation(observed_property, payload, resource_id):
    if not payload:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)
    if not module:
        logging.critical("No Security Fusion Node instantiated!")
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    result = module.ogc_observation_registration(observed_property, payload, resource_id)
    if result is True:
        return make_response(jsonify({"result": "Ok"}), 201)
    elif result is None:
        logging.error("Device: '" + str(resource_id) + "' was not registered.")
        return make_response(jsonify({"Error": "Security Fusion Node not registered!"}), 400)
    else:
        logging.error("Impossible to publish on MQTT server.")
        return make_response(jsonify({"Error": "Internal server error"}), 500)


@flask_instance.route("/")
def test():
    """ Checking if Flask is working. """
    logging.debug(test.__name__ + " method called \n")

    return "<h1>Flask is running!</h1>"


@flask_instance.route(URI_DEFAULT)
def test_module():
    """ Checking if SCRAL is running. """
    logging.debug(test_module.__name__ + " method called \n")

    to_ret = "<h1>SCRAL module is running!</h1>\n"
    to_ret += "<h2> ToDo: Insert list of API here! </h2>"
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
