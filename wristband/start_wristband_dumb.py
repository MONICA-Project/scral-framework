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
import os
import logging
import sys
import signal

import arrow
from flask import Flask, request, jsonify, make_response

import scral_module as scral
from scral_module.constants import END_MESSAGE, ENABLE_FLASK, DEFAULT_REST_CONFIG, SUCCESS_RETURN_STRING, \
                                   ENDPOINT_URL_KEY, ENDPOINT_PORT_KEY, MODULE_NAME_KEY, TIMESTAMP_KEY
from scral_module import util

from wristband.constants import URI_DEFAULT, URI_ACTIVE_DEVICES, URI_WRISTBAND_BUTTON, URI_WRISTBAND_LOCALIZATION, \
                                URI_WRISTBAND_REGISTRATION, URI_WRISTBAND_ASSOCIATION
from wristband.wristband_module import SCRALWristband
from wristband import wristband_util as wb_util

flask_instance = Flask(__name__)
module: SCRALWristband = None
logger: bool = False
p_name: str = None

DOC = DEFAULT_REST_CONFIG
COUNTER = 0


def main():
    module_description = "Dumb Wristband integration instance"
    cmd_line = util.parse_small_command_line(module_description)
    pilot_config_folder = cmd_line.pilot.lower() + "/"

    global module
    module = wb_util.instance_wb_module(pilot_config_folder, DOC)
    module.runtime(flask_instance, ENABLE_FLASK)


@flask_instance.route(URI_WRISTBAND_REGISTRATION, methods=["POST"])
def new_wristband_request():
    print_time(new_wristband_request.__name__, request.json)
    return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 200)


@flask_instance.route(URI_WRISTBAND_ASSOCIATION, methods=["PUT"])
def new_wristband_association_request():
    print_time(new_wristband_association_request.__name__, request.json)
    return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 200)


@flask_instance.route(URI_WRISTBAND_LOCALIZATION, methods=["PUT"])
def new_wristband_localization():
    print_time(new_wristband_localization.__name__, request.json)
    return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 200)


@flask_instance.route(URI_WRISTBAND_BUTTON, methods=["PUT"])
def new_wristband_button():
    print_time(new_wristband_button.__name__, request.json)
    return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 200)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices():
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr+" \n")

    to_ret = jsonify(module.get_active_devices())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module():
    """ Checking if SCRAL is running.
    :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr+" \n")
    return wb_util.wristband_documentation(DOC[MODULE_NAME_KEY]+" (dumb version)",
                                           DOC[ENDPOINT_URL_KEY] + ":" + str(DOC[ENDPOINT_PORT_KEY]))


def print_time(method_name, payload):
    global logger, p_name
    if not logger:
        # p_name = current_process().name
        p_name = str(os.getpid())
        util.init_logger(logging.DEBUG)
        logger = True

    global COUNTER
    COUNTER += 1
    now = arrow.utcnow()
    logging.debug(p_name+" --- Method "+method_name+" called at: " + str(now))
    logging.debug(p_name+" --- Counter: "+str(COUNTER))
    try:
        phenomenon_time = payload[TIMESTAMP_KEY]
        diff = now - arrow.get(phenomenon_time)
        logging.debug(p_name+" --- Time elapsed since PhenomenonTime: %.3f seconds." % diff.total_seconds())
    except KeyError:
        logging.error(p_name+" --- Wrong field!")


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
