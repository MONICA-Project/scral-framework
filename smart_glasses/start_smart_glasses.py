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
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE

from smart_glasses.constants import URI_DEFAULT, URI_GLASSES_REGISTRATION, URI_GLASSES_LOCALIZATION, \
    URI_GLASSES_INCIDENT, PROPERTY_LOCALIZATION_NAME, PROPERTY_INCIDENT_NAME, CATALOG_NAME_GLASSES
from smart_glasses.smart_glasses_module import SCRALSmartGlasses

flask_instance = Flask(__name__)
module: SCRALSmartGlasses = None


def main():
    module_description = "Smart Glasses integration instance"
    args = util.parse_command_line(module_description)

    # OGC-Configuration
    ogc_config = SCRALSmartGlasses.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Module initialization and runtime phase
    global module
    module = SCRALSmartGlasses(ogc_config, args.connection_file, args.pilot, CATALOG_NAME_GLASSES)
    module.runtime(flask_instance)


@flask_instance.route(URI_GLASSES_REGISTRATION, methods=["POST"])
def new_glasses_request():
    logging.debug(new_glasses_request.__name__ + " method called")

    if not request.json:
        return jsonify({"Error": "Wrong request!"}), 400

    glasses_id = request.json["tagId"]
    type = request.json["type"]

    if module is None:
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    # -> ### DATASTREAM REGISTRATION ###
    rc = module.get_resource_catalog()
    if glasses_id not in rc:
        logging.info("Glasses: '" + str(glasses_id) + "' registration.")
        ok = module.ogc_datastream_registration(glasses_id)
        if not ok:
            return make_response(jsonify({"Error": "Internal server error"}), 500)
    else:
        logging.error("Device already registered!")
        return make_response(jsonify({"Error": "Duplicate request!"}), 422)

    return make_response(jsonify({"result": "Ok"}), 201)


@flask_instance.route(URI_GLASSES_LOCALIZATION, methods=["PUT"])
def new_glasses_localization():
    logging.debug(new_glasses_localization.__name__ + " method called")
    response = put_observation(PROPERTY_LOCALIZATION_NAME, request.json)
    return response


@flask_instance.route(URI_GLASSES_INCIDENT, methods=["PUT"])
def new_glasses_incident():
    logging.debug(new_glasses_incident.__name__ + " method called")
    response = put_observation(PROPERTY_INCIDENT_NAME, request.json)
    return response


def put_observation(observed_property, payload):
    if not payload:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)

    if module is None:
        return make_response(jsonify({"Error": "Internal server error"}), 500)
    else:
        glasses_id = payload["tagId"]
        result = module.ogc_observation_registration(observed_property, payload)
        if result is True:
            return make_response(jsonify({"result": "Ok"}), 201)
        elif result is None:
            logging.error("Glasses: '" + str(glasses_id) + "' was not registered.")
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
