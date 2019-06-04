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

"""
ROADMAP: these are main steps in which this SCRAL module is divided.

PHASE PRELIMINARY:
  0. SEE SCRALRestModule for previous steps.

PHASE: INTEGRATION
  1. Get notified about new glasses registration and creates new DATASTREAM
  2. Upload OGC Observation through MQTT
"""

#############################################################################
import logging
import sys
import signal

from flask import Flask, request, jsonify, make_response

import scral_module as scral
from scral_module import util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE, VPN_URL

from smart_glasses.constants import URI_DEFAULT, VPN_PORT, PROPERTY_LOCALIZATION_NAME, PROPERTY_INCIDENT_NAME, \
    URI_ACTIVE_DEVICES, URI_GLASSES_REGISTRATION, URI_GLASSES_LOCALIZATION, URI_GLASSES_INCIDENT
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
    catalog_name = args.pilot + "_glasses.json"
    module = SCRALSmartGlasses(ogc_config, args.connection_file, args.pilot, catalog_name)
    module.runtime(flask_instance)


@flask_instance.route(URI_GLASSES_REGISTRATION, methods=["POST"])
def new_glasses_request():
    """ This function can register new glasses in the OGC server.
    :return: An HTTP Response.
    """
    logging.debug(new_glasses_request.__name__ + " method called from: "+request.remote_addr)

    if not request.json:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)

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
    """ This function can register new glasses location in the OGC server.
    :return: An HTTP Response.
    """
    logging.debug(new_glasses_localization.__name__ + " method called from: "+request.remote_addr)
    response = put_observation(PROPERTY_LOCALIZATION_NAME, request.json)
    return response


@flask_instance.route(URI_GLASSES_INCIDENT, methods=["PUT"])
def new_glasses_incident():
    """ This function can register new glasses incident in the OGC server.
    :return: An HTTP Response.
    """
    logging.debug(new_glasses_incident.__name__ + " method called from: "+request.remote_addr)

    response = put_observation(PROPERTY_INCIDENT_NAME, request.json)
    return response


def put_observation(observed_property, payload):
    """ This function is used to store a new OBSERVATION in the OGC Server.

    :param observed_property: The type of property
    :param payload: The payload of the observation
    :return: An HTTP request.
    """
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


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices():
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    to_ret = jsonify(module.get_resource_catalog())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module():
    """ Checking if SCRAL is running.
    :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = VPN_URL+":"+str(VPN_PORT)
    posts = (URI_GLASSES_REGISTRATION, )
    puts = (URI_GLASSES_LOCALIZATION, URI_GLASSES_INCIDENT)
    gets = (URI_ACTIVE_DEVICES, )
    to_ret = util.to_html_documentation("SCRALSmartGlasses", link, posts, puts, gets)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
