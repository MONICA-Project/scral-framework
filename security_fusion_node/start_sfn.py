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
from scral_module import mqtt_util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE, ERROR_WRONG_PILOT_NAME

from security_fusion_node.constants import URI_DEFAULT, URI_CAMERA, URI_CDG
from security_fusion_node.sfn_module import SCRALSecurityFusionNode

flask_instance = Flask(__name__)
module: SCRALSecurityFusionNode = None
verbose = False


def main():
    module_description = "Smart Glasses integration instance"
    args = util.parse_command_line(module_description)

    # OGC-Configuration
    ogc_config = SCRALSecurityFusionNode.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Retrieving pilot name --- 'local' is the default configuration value
    pilot_mqtt_topic_prefix = mqtt_util.get_publish_mqtt_topic(args.pilot)
    if not pilot_mqtt_topic_prefix:
        logging.critical('Wrong pilot name: "' + args.pilot + '"!')
        exit(ERROR_WRONG_PILOT_NAME)
    else:
        logging.debug("MQTT publishing topic prefix: " + pilot_mqtt_topic_prefix)

    # Module initialization and runtime phase
    global module
    module = SCRALSecurityFusionNode(ogc_config, args.connection_file, pilot_mqtt_topic_prefix)
    module.runtime(flask_instance)


@flask_instance.route(URI_CAMERA, methods=["POST", "PUT"])
def new_camera_request():
    logging.debug(new_camera_request.__name__ + ", " + request.method + " method called")

    if not request.json:
        return jsonify({"Error": "Wrong request!"}), 400

    camera_id = request.json["camera_id"]

    if not module:
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    rc = module.get_resource_catalog()
    if request.method == "POST":  # POST
        sensor_type = "Camera"  # TO FIX
        if camera_id not in rc:
            logging.info("Camera: '" + str(camera_id) + "' registration.")
            ok = module.ogc_datastream_registration(camera_id, sensor_type, request.json)
            if not ok:
                return make_response(jsonify({"Error": "Internal server error"}), 500)
        else:
            logging.error("Device already registered!")
            return make_response(jsonify({"Error": "Duplicate request!"}), 422)

        return make_response(jsonify({"result": "Ok"}), 201)

    elif request.method == "PUT":  # PUT
        logging.info("New OBSERVATION from camera: '" + str(camera_id))
        property_type = request.json["type_module"]

        if property_type == "fighting_detection":
            observed_property = "FD-Estimation"
        else:  # ToDO: add controls for other properties and look for a smart way to handle these controls
            observed_property = "unknown"

        response = put_observation(observed_property, request.json, camera_id)
        return response


@flask_instance.route(URI_CDG, methods=["POST", "PUT"])
def new_cdg_request():
    logging.debug(new_cdg_request.__name__ + ", " + request.method + " method called")

    if not request.json:
        return jsonify({"Error": "Wrong request!"}), 400

    module_id = request.json["module_id"]  # NB: module here is Crowd Density Global module
    module_type = "Crowd-Density-Global"

    if not module:
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    rc = module.get_resource_catalog()
    if request.method == "POST":  # POST
        if module_id not in rc:
            logging.info("CDG: '" + str(module_id) + "' registration.")
            ok = module.ogc_datastream_registration(module_id, module_type, request.json)
            if not ok:
                return make_response(jsonify({"Error": "Internal server error"}), 500)
        else:
            logging.error("Device already registered!")
            return make_response(jsonify({"Error": "Duplicate request!"}), 422)

        return make_response(jsonify({"result": "Ok"}), 201)

    elif request.method == "PUT":  # PUT
        logging.info("New OBSERVATION from CDG: '" + str(module_id))

        property_type = request.json["type_module"]
        timestamp = request.json.pop("timestamp_1")  # forcing "timestamp_1" to be called "timestamp"
        request.json["timestamp"] = timestamp

        if property_type == "crowd_density_global":
            observed_property = "CDG-Estimation"
        else:  # ToDO: add controls for other properties and look for a smart way to handle these controls
            observed_property = "unknown"

        response = put_observation(observed_property, request.json, module_id)
        return response


def put_observation(observed_property, payload, resource_id):
    if not payload:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)
    if not module:
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    result = module.ogc_observation_registration(observed_property, payload, resource_id)
    if result is True:
        return make_response(jsonify({"result": "Ok"}), 201)
    elif result is None:
        logging.error("Device: '" + str(resource_id) + "' was not registered.")
        return make_response(jsonify({"Error": "Glasses not registered!"}), 400)
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
