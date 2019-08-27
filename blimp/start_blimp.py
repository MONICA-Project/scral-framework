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
  1. Get notified about new blimps
  2. Upload DATASTREAM entities to OGC Server
  3. Upload new OGC OBSERVATION through MQTT
"""

##############################################################################
import logging
import os
import signal
import sys

from flask import Flask, request, jsonify, make_response

import scral_module as scral
from scral_module import util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE, \
                                   FILENAME_CONFIG, FILENAME_COMMAND_FILE

from blimp.constants import URI_DEFAULT, URI_ACTIVE_DEVICES, BLIMP_KEY
from blimp.blimp_module import SCRALBlimp

flask_instance = Flask(__name__)
scral_module: SCRALBlimp = None

MODULE_NAME: str = "SCRAL Module"
ENDPOINT_PORT: int = 8000
ENDPOINT_URL: str = "localhost"


def main():
    module_description = "SCRAL Blimps integration instance"
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
    ogc_config = SCRALBlimp.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Initialize documentation variable
    global MODULE_NAME, ENDPOINT_PORT, ENDPOINT_URL
    MODULE_NAME = args["module_name"]
    ENDPOINT_PORT = args["endpoint_port"]
    ENDPOINT_URL = args["endpoint_url"]

    # Module initialization and runtime phase
    global module
    filename_connection = os.path.join(connection_path + args['connection_file'])
    catalog_name = args["pilot"] + "_Blimp.json"
    module = SCRALBlimp(ogc_config, filename_connection, args['pilot'], catalog_name)
    module.runtime(flask_instance, 1)


@flask_instance.route(URI_DEFAULT, methods=["POST"])
def new_blimp_registration():
    """ This function can register a new Blimp in the OGC server.

    :return: An HTTP Response.
    """
    logging.debug(new_blimp_registration.__name__ + ", " + request.method + " method called from: " + request.remote_addr)

    if not request.json:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)

    if not module:
        logging.critical("SCRAL Blimp module is not available!")
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    response = module.ogc_datastream_registration(request.json)
    return response


@flask_instance.route(URI_DEFAULT+"/Datastreams(<datastream_id>)/Observations", methods=["PUT"])
def new_blimp_observation(datastream_id=None):
    """ This function can register a new Blimp in the OGC server.

    :return: An HTTP Response.
    """
    logging.debug(new_blimp_observation.__name__ + ", " + request.method + " method called from: " + request.remote_addr)

    if not request.json:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)
    if datastream_id is None:
        return make_response(jsonify({"Error": "Missing DATASTREAM id!"}), 400)

    if not module:
        logging.critical("SCRAL Blimp module is not available!")
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    # Just for this particular case
    request.json[BLIMP_KEY] = "kappa-blimp"

    response = module.ogc_observation_registration(datastream_id, request.json)
    return response


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

    link = ENDPOINT_URL+":"+str(ENDPOINT_PORT)
    posts = (URI_DEFAULT,)
    puts = (URI_DEFAULT+"/Datastreams(id)/Observations",)
    gets = (URI_ACTIVE_DEVICES, )
    return util.to_html_documentation(MODULE_NAME, link, posts, puts, gets)


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
