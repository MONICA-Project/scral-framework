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
import copy
import logging
import os
import sys
import signal

from flask import Flask, request, jsonify, make_response

import scral_module as scral
import scral_ogc
from scral_module import util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE, \
                                   FILENAME_CONFIG, FILENAME_COMMAND_FILE

from sound_level_meter.slm_module import SCRALSoundLevelMeter
from sound_level_meter.constants import URL_SLM_LOGIN, CREDENTIALS, SLM_LOGIN_PREFIX, \
    URI_DEFAULT, URI_ACTIVE_DEVICES, URI_SOUND_EVENT, DEVICE_NAME_KEY

flask_instance = Flask(__name__)
module: SCRALSoundLevelMeter = None

MODULE_NAME: str = "SCRAL Module"
ENDPOINT_PORT: int = 8000
ENDPOINT_URL: str = "localhost"


def main():
    module_description = "Sound Level Meter integration instance"
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
    ogc_config = SCRALSoundLevelMeter.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Initialize documentation variable
    global MODULE_NAME, ENDPOINT_PORT, ENDPOINT_URL
    MODULE_NAME = args["module_name"]
    ENDPOINT_PORT = args["endpoint_port"]
    ENDPOINT_URL = args["endpoint_url"]

    # Module initialization and runtime phase
    global module
    filename_connection = os.path.join(connection_path + args['connection_file'])
    catalog_name = args["pilot"] + "_SLM.json"
    module = SCRALSoundLevelMeter(ogc_config, filename_connection, args['pilot'],
                                  URL_SLM_LOGIN, CREDENTIALS, catalog_name, SLM_LOGIN_PREFIX)
    module.runtime(flask_instance, 1)


@flask_instance.route(URI_SOUND_EVENT, methods=["PUT"])
def new_sound_event():
    """ This function can register an OBSERVATION in the OGC server.
        It is able to accept any new OBSERVED PROPERTY according to the content of "type" field.
        This new property is run-time generated.

    :return: An HTTP Response.
    """
    logging.debug(new_sound_event.__name__ + " method called from: "+request.remote_addr)

    payload = request.json
    property_name = payload["type"]
    try:
        property_description = payload["description"]
    except KeyError:
        property_description = property_name + " description"
    try:
        property_definition = payload["definition"]
    except KeyError:
        property_definition = property_name + " definition"

    obs_prop = scral_ogc.OGCObservedProperty(property_name, property_description, property_definition)
    device_id = payload["deviceId"]

    datastream_id = module.new_datastream(device_id, obs_prop)
    if datastream_id is False:
        return make_response(jsonify({"Error": "deviceId not recognized."}), 400)
    elif datastream_id is None:
        return make_response(jsonify({"Error": "Internal server error."}), 500)
    else:
        module.ogc_observation_registration(datastream_id, payload["startTime"], payload)
        return make_response(jsonify({"Result": "Ok"}), 201)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices():
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    rc_copy = copy.deepcopy(module.get_resource_catalog())
    new_rc = {}
    for item in rc_copy.values():
        key = item.pop(DEVICE_NAME_KEY)
        new_rc[key] = item

    return make_response(jsonify(new_rc), 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module():
    """ Checking if SCRAL is running.
    :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = ENDPOINT_URL+":"+str(ENDPOINT_PORT)
    posts = ()
    puts = (URI_SOUND_EVENT, )
    gets = (URI_ACTIVE_DEVICES, )
    to_ret = util.to_html_documentation(MODULE_NAME, link, posts, puts, gets)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
