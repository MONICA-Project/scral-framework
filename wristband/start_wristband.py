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
from scral_module.constants import END_MESSAGE
from wristband.constants import FILENAME_PILOT, \
                                PROPERTY_BUTTON_NAME, PROPERTY_LOCALIZATION_NAME, SENSOR_ASSOCIATION_NAME, \
                                URI_DEFAULT, URI_ACTIVE_DEVICES, URI_WRISTBAND_BUTTON, \
                                URI_WRISTBAND_LOCALIZATION, URI_WRISTBAND_REGISTRATION, URI_WRISTBAND_ASSOCIATION

from wristband.wristband_module import SCRALWristband
from wristband.wristband_util import instance_wb_module

flask_instance = Flask(__name__)
scral_module: SCRALWristband = None

MODULE_NAME: str = "SCRAL Module"
ENDPOINT_PORT: int = 8000
ENDPOINT_URL: str = "localhost"


def get_scral_module():
    global scral_module
    if not scral_module:
        # printing scral banner and instantiating a signal handler
        print(scral.BANNER % scral.VERSION)
        sys.stdout.flush()
        signal.signal(signal.SIGINT, util.signal_handler)

        scral_module = instance_wb_module(FILENAME_PILOT)

    return scral_module


@flask_instance.route(URI_WRISTBAND_REGISTRATION, methods=["POST"])
def new_wristband_request():
    logging.debug(new_wristband_request.__name__ + " method called from: "+request.remote_addr)

    module = get_scral_module()
    if module is None:
        return make_response(jsonify({"Error": "Internal server error"}), 600)

    if not request.json:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)

    wristband_id = request.json["tagId"]

    # -> ### DATASTREAM REGISTRATION ###
    rc = module.get_resource_catalog()

    if wristband_id not in rc:
        logging.info("Wristband: '" + str(wristband_id) + "' registration.")
    else:
        # logging.error("Device "+wristband_id+" already registered!")
        # return make_response(jsonify({"Error": "Duplicate request!"}), 422)
        logging.warning("Device '" + str(wristband_id) + "' already registered... It will be overwritten on RC!")

    ok = module.ogc_datastream_registration(wristband_id, request.json)
    if not ok:
        return make_response(jsonify({"Error": "Internal server error"}), 500)
    else:
        return make_response(jsonify({"result": "Ok"}), 201)


@flask_instance.route(URI_WRISTBAND_ASSOCIATION, methods=["PUT"])
def new_wristband_association_request():
    logging.debug(new_wristband_association_request.__name__ + " method called from: "+request.remote_addr)

    module = get_scral_module()
    if not module:
        return make_response(jsonify({"Error": "Internal server error"}), 500)
    if not request.json:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)

    wristband_id_1 = request.json["tagId_1"]
    wristband_id_2 = request.json["tagId_2"]

    rc = module.get_resource_catalog()
    if wristband_id_1 not in rc or wristband_id_2 not in rc:
        logging.error("One of the wristbands is not registered.")
        return make_response(jsonify({"Error": "One of the wristbands is not registered!"}), 400)

    vds = module.get_ogc_config().get_virtual_datastream(SENSOR_ASSOCIATION_NAME)
    if not vds:
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    response = put_service_observation(vds, request.json)

    return response


@flask_instance.route(URI_WRISTBAND_LOCALIZATION, methods=["PUT"])
def new_wristband_localization():
    logging.debug(new_wristband_localization.__name__ + " method called from: "+request.remote_addr)

    response = put_observation(PROPERTY_LOCALIZATION_NAME, request.json)
    return response


@flask_instance.route(URI_WRISTBAND_BUTTON, methods=["PUT"])
def new_wristband_button():
    logging.debug(new_wristband_button.__name__ + " method called from: "+request.remote_addr)

    response = put_observation(PROPERTY_BUTTON_NAME, request.json)
    return response


def put_observation(observed_property, payload):
    if not payload:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)

    module = get_scral_module()
    if not module:
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    wristband_id = payload["tagId"]
    result = module.ogc_observation_registration(observed_property, payload)
    if result is True:
        return make_response(jsonify({"result": "Ok"}), 201)
    elif result is None:
        logging.error("Wristband: '" + str(wristband_id) + "' was not registered.")
        return make_response(jsonify({"Error": "Wristband not registered!"}), 400)
    else:
        logging.error("Impossible to publish on MQTT server.")
        return make_response(jsonify({"Error": "Impossible to publish on MQTT server."}), 502)


def put_service_observation(datastream, payload):
    if not payload:
        return make_response(jsonify({"Error": "Wrong request!"}), 400)

    module = get_scral_module()
    if not module:
        return make_response(jsonify({"Error": "Internal server error"}), 500)

    result = module.ogc_service_observation_registration(datastream, payload)
    if result is True:
        return make_response(jsonify({"result": "Ok"}), 201)
    else:
        logging.error("Impossible to publish on MQTT server.")
        return make_response(jsonify({"Error": "Impossible to publish on MQTT server."}), 502)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices():
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    module = get_scral_module()
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
    to_ret = util.to_html_documentation(MODULE_NAME, link, posts, puts, gets)
    return to_ret


if __name__ == '__main__':
    get_scral_module()
    flask_instance.run(host="0.0.0.0", port=8000)
    print(END_MESSAGE)
