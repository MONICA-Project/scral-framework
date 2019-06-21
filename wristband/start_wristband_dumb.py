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
import sys
import signal

from flask import Flask, request, jsonify, make_response

import scral_module as scral
from scral_module import util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE, \
                                   FILENAME_CONFIG, FILENAME_COMMAND_FILE
from wristband.constants import PROPERTY_BUTTON_NAME, PROPERTY_LOCALIZATION_NAME, SENSOR_ASSOCIATION_NAME, \
                                URI_DEFAULT, URI_ACTIVE_DEVICES, URI_WRISTBAND_BUTTON, URI_WRISTBAND_LOCALIZATION, \
                                URI_WRISTBAND_REGISTRATION, URI_WRISTBAND_ASSOCIATION

from wristband.wristband_module import SCRALWristband
from wristband import wristband_util as wb_util

flask_instance = Flask(__name__)
module: SCRALWristband = None

MODULE_NAME: str = "SCRAL Module"
ENDPOINT_PORT: int = 8000
ENDPOINT_URL: str = "localhost"


def main():
    module_description = "Dumb Wristband integration instance"
    cmd_line = util.parse_small_command_line(module_description)
    pilot_config_folder = cmd_line.pilot.lower() + "/"

    global module
    module = wb_util.instance_wb_module(pilot_config_folder)
    module.runtime(flask_instance, 1)


@flask_instance.route(URI_WRISTBAND_REGISTRATION, methods=["POST"])
def new_wristband_request():
    logging.debug(new_wristband_request.__name__ + " method called from: "+request.remote_addr+" \n")
    return make_response(jsonify({"result": "Ok"}), 200)


@flask_instance.route(URI_WRISTBAND_ASSOCIATION, methods=["PUT"])
def new_wristband_association_request():
    logging.debug(new_wristband_association_request.__name__ + " method called from: "+request.remote_addr+" \n")
    return make_response(jsonify({"result": "Ok"}), 200)


@flask_instance.route(URI_WRISTBAND_LOCALIZATION, methods=["PUT"])
def new_wristband_localization():
    logging.debug(new_wristband_localization.__name__ + " method called from: "+request.remote_addr+" \n")
    return make_response(jsonify({"result": "Ok"}), 200)


@flask_instance.route(URI_WRISTBAND_BUTTON, methods=["PUT"])
def new_wristband_button():
    logging.debug(new_wristband_button.__name__ + " method called from: "+request.remote_addr+" \n")
    return make_response(jsonify({"result": "Ok"}), 200)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices():
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr+" \n")
    to_ret = jsonify(module.get_resource_catalog())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module():
    """ Checking if SCRAL is running.
    :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr+" \n")

    link = ENDPOINT_URL + ":" + str(ENDPOINT_PORT)
    posts = (URI_WRISTBAND_REGISTRATION, )
    puts = (URI_WRISTBAND_ASSOCIATION, URI_WRISTBAND_LOCALIZATION, URI_WRISTBAND_BUTTON)
    gets = (URI_ACTIVE_DEVICES, )
    to_ret = util.to_html_documentation(MODULE_NAME+" (dumb version)", link, posts, puts, gets)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
