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

"""
#############################################################################
import logging
import os
import sys
import signal

from flask import Flask, request, jsonify, make_response

import scral_module as scral
from scral_module import util
from scral_module.constants import END_MESSAGE, ENABLE_FLASK, FILENAME_CONFIG, FILENAME_COMMAND_FILE, \
                                   OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD
from wristband.constants import URI_DEFAULT, URI_ACTIVE_DEVICES, URI_WRISTBAND_REGISTRATION
from wristband_mqtt.wristband_mqtt_module import SCRALMQTTWristband


flask_instance = Flask(__name__)
module: SCRALMQTTWristband = None

DOC = {"module_name": "SCRAL Module", "endpoint_port": 8000, "endpoint_url": "localhost"}


def main():
    module_description = "Wristband MQTT integration instance"
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
    ogc_config = SCRALMQTTWristband.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Initialize documentation variable
    DOC["module_name"] = args["module_name"]
    DOC["endpoint_port"] = args["endpoint_port"]
    DOC["endpoint_url"] = args["endpoint_url"]

    # Module initialization and runtime phase
    filename_connection = os.path.join(connection_path + args['connection_file'])
    catalog_name = args["pilot"] + "_wristband.json"

    global module
    module = SCRALMQTTWristband(ogc_config, filename_connection, args['pilot'], catalog_name)
    module.mqtt_subscriptions("Wristband")
    module.runtime(flask_instance, ENABLE_FLASK)


@flask_instance.route(URI_WRISTBAND_REGISTRATION, methods=["POST"])
def new_wristband_request():
    logging.debug(new_wristband_request.__name__+" method called from: "+request.remote_addr)

    if not request.json:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)

    wristband_id = request.json["tagId"]

    if module is None:
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    # -> ### DATASTREAM REGISTRATION ###
    rc = module.get_resource_catalog()
    if wristband_id not in rc:
        logging.info("Wristband: '" + str(wristband_id) + "' registration.")
    else:
        logging.warning("Device '" + str(wristband_id) + "' already registered... It will be overwritten on RC!")

    ok = module.ogc_datastream_registration(wristband_id, request.json)
    if not ok:
        return make_response(jsonify({"Error": "Internal server error"}), 500)
    else:
        return make_response(jsonify({"result": "Ok"}), 201)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices():
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__+" method called from: "+request.remote_addr)

    to_ret = jsonify(module.get_active_devices())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module():
    """ Checking if SCRAL is running.
    :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr+" \n")

    link = DOC["endpoint_url"] + ":" + str(DOC["endpoint_port"])
    gets = (URI_ACTIVE_DEVICES, )
    to_ret = util.to_html_documentation(DOC["module_name"], link, (), (), gets)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
