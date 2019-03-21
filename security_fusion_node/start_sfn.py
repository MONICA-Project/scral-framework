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

from flask import Flask, request, jsonify, make_response

import scral_module as scral
from scral_module import util
from scral_module import mqtt_util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE
from scral_module.ogc_configuration import OGCConfiguration

from security_fusion_node.constants import URI_DEFAULT, URI_CAMERA, URI_CDG
from security_fusion_node.sfn_module import SCRALSecurityFusionNode

flask_instance = Flask(__name__)
module = None
verbose = False


def main():
    # parsing command line parameters, it has to be the first instruction
    args = util.parse_command_line("Smart Glasses integration instance")

    global verbose  # overwrite verbose flag from command line
    if args.verbose:
        verbose = True
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
        verbose = False

    util.init_logger(logging_level)  # logging initialization

    if not args.connection_file:  # has the connection_file been set?
        logging.critical("Connection file is missing!")
        exit(1)

    if not args.ogc_file:  # has the ogc_file been set?
        logging.critical("OGC configuration file is missing!")
        exit(2)

    pilot_mqtt_topic_prefix = mqtt_util.get_publish_mqtt_topic(args.pilot)  # 'local' is the default configuration value
    if not pilot_mqtt_topic_prefix:
        logging.critical('Wrong pilot name: "' + args.pilot + '"!')
        exit(3)

    logging.info("[PHASE-INIT] The connection file is: " + args.connection_file)
    logging.debug("OGC file: " + args.ogc_file)
    logging.debug("MQTT publishing topic prefix: " + pilot_mqtt_topic_prefix)

    # Storing the OGC server addresses
    connection_config_file = util.load_from_file(args.connection_file)
    ogc_server_address = connection_config_file["REST"]["ogc_server_address"]

    if not util.test_connectivity(ogc_server_address, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD):
        logging.critical("Network connectivity to " + ogc_server_address + " not available!")
        exit(4)

    # OGC model configuration and discovery
    ogc_config = OGCConfiguration(args.ogc_file, ogc_server_address)
    ogc_config.discovery(verbose)

    # Module initialization and runtime phase
    global module
    module = SCRALSecurityFusionNode(ogc_config, args.connection_file, pilot_mqtt_topic_prefix)
    module.runtime(flask_instance)


@flask_instance.route(URI_CAMERA, methods=["POST", "PUT"])
def new_camera_request():
    logging.debug(new_camera_request.__name__ + " method called")

    if not request.json:
        return jsonify({"Error": "Wrong request!"}), 400

    camera_id = request.json["camera_id"]
    sensor_type = request.json["type_module"]

    if module is None:
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    rc = module.get_resource_catalog()
    if request.method == "POST":  # POST
        if camera_id not in rc:
            logging.info("Camera: '" + str(camera_id) + "' registration.")
            ok = module.ogc_datastream_registration(camera_id, )
            if not ok:
                return make_response(jsonify({"Error": "Internal server error"}), 500)
        else:
            logging.error("Device already registered!")
            return make_response(jsonify({"Error": "Duplicate request!"}), 422)

    elif request.method == "PUT":  # PUT
        if camera_id not in rc:
            logging.error("Camera: '" + str(camera_id) + "' was not registered.")
            return make_response(jsonify({"Error": "Camera not registered!"}), 400)
        else:

    else:
        return make_response(jsonify({"Error": "Method not allowed!"}), 405)


@flask_instance.route(URI_CDG, methods=["POST", "PUT"])
def new_cdg_request():
    if request.method == "POST":
        module.cdg_registration()
    elif request.method == "PUT":
        module.cdg_observation()
    else:
        return make_response(jsonify({"Error": "Method not allowed!"}), 405)


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
