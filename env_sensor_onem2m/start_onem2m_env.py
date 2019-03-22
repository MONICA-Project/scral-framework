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
#
# ROADMAP: these are main steps in which a SCRAL module is divided.
#
# PHASE: INIT + SETUP + BOOT
#   1. Init variables and setup server and MQTT connections
#   2. Read configuration File and load OGC scheme (exit if integrity not satisfied)
#
# #PHASE: DISCOVERY
#   3. Check via discovery if loaded entities are already registered
#   4. If needed, register new entities to OGC Server
#   5. Retrieve corresponding @iot.id's
#
# #PHASE: INTEGRATION
#   6. Get notified about new OneM2M "containers"
#   7. Upload DATASTREAM entities to OGC Server
#   8. Expose SCRAL endpoint and listen to incoming requests
#
##############################################################################
import json
import logging
import signal
import sys

from flask import Flask, request, jsonify

import scral_module as scral
from scral_module import util
from scral_module import mqtt_util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE, ERROR_WRONG_PILOT_NAME

from env_sensor_onem2m.constants import URI_DEFAULT, URI_ENV_NODE, ONEM2M_CONTENT_TYPE
from env_sensor_onem2m.env_onem2m_module import SCRALEnvOneM2M

flask_instance = Flask(__name__)
module: SCRALEnvOneM2M = None
verbose = False


def main():
    module_description = "OneM2M Environmental Sensors adapter instance"
    args = util.parse_command_line(module_description)

    # OGC-Configuration
    ogc_config = SCRALEnvOneM2M.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Retrieving pilot name --- 'local' is the default configuration value
    pilot_mqtt_topic_prefix = mqtt_util.get_publish_mqtt_topic(args.pilot)
    if not pilot_mqtt_topic_prefix:
        logging.critical('Wrong pilot name: "' + args.pilot + '"!')
        exit(ERROR_WRONG_PILOT_NAME)
    else:
        logging.debug("MQTT publishing topic prefix: " + pilot_mqtt_topic_prefix)

    # Module initialization and runtime phase
    global module
    module = SCRALEnvOneM2M(ogc_config, args.connection_file, pilot_mqtt_topic_prefix)
    module.runtime(flask_instance)


@flask_instance.route(URI_ENV_NODE, methods=["POST"])
def new_onem2m_request():
    logging.debug(new_onem2m_request.__name__ + " method called")

    container_path = str(request.json["m2m:sgn"]["sur"])
    substrings = container_path.split("/")
    env_node_id = None
    for i in range(len(substrings)):
        if substrings[i].startswith("env-node"):
            env_node_id = substrings[i]
            break
    if env_node_id is None:
        return jsonify({"Error": "Environmental Node ID not found!"}), 400

    content_type = request.json["m2m:sgn"]["nev"]["rep"]["m2m:cin"]["cnf"]
    if content_type != ONEM2M_CONTENT_TYPE:
        raise TypeError("The content: <"+content_type+"> was not recognized! <"+ONEM2M_CONTENT_TYPE+"> is expected!")

    raw_content = request.json["m2m:sgn"]["nev"]["rep"]["m2m:cin"]["con"]
    if type(raw_content) is str:
        content = json.loads(raw_content)
    elif type(raw_content) is dict:
        content = raw_content
    else:
        raise TypeError("The content type is "+str(type(raw_content))+", it must be a String or a Dictionary")

    if module is None:
        return jsonify({"Error": "Internal server error"}), 500

    # -> ### DATASTREAM REGISTRATION ###
    rc = module.get_resource_catalog()
    if env_node_id not in rc:
        logging.info("Node: " + str(env_node_id) + " registration.")
        module.ogc_datastream_registration(env_node_id)

    # -> ### OBSERVATION REGISTRATION ###
    module.ogc_observation_registration(env_node_id, content, request.json["m2m:sgn"])

    return jsonify({"result": "Ok"}), 201


@flask_instance.route("/")
def test():
    """ Checking if Flask is working. """
    logging.debug(test.__name__ + " method called")

    return "<h1>Flask is running!</h1>"


@flask_instance.route(URI_DEFAULT)
def test_module():
    """ Checking if SCRAL is running. """
    logging.debug(test_module.__name__ + " method called")

    to_ret = "<h1>SCRAL module is running!</h1>\n"
    to_ret += "<h2> ToDo: Insert list of API here! </h2>"
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
