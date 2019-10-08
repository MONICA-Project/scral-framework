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
  1. Get notified about new OneM2M "containers"
  2. Upload DATASTREAM entities to OGC Server
  3. Upload new OGC OBSERVATION through MQTT
"""

##############################################################################
import json
import logging
import os
import signal
import sys
from typing import Optional

from flask import Flask, request, jsonify, make_response, Response

import scral_core as scral
from scral_core import util
from scral_core.constants import END_MESSAGE, ENABLE_CHERRYPY, DEFAULT_REST_CONFIG, \
                                   ENDPOINT_PORT_KEY, ENDPOINT_URL_KEY, \
                                   ERROR_RETURN_STRING, WRONG_CONTENT_TYPE, INTERNAL_SERVER_ERROR, UNKNOWN_CONTENT_TYPE

from env_sensor_onem2m.constants import URI_DEFAULT, URI_ACTIVE_DEVICES, URI_ENV_NODE, ONEM2M_CONTENT_TYPE
from env_sensor_onem2m.env_onem2m_module import SCRALEnvOneM2M

flask_instance = Flask(__name__)
scral_module: Optional[SCRALEnvOneM2M] = None

DOC = DEFAULT_REST_CONFIG


def main():
    module_description = "SCRAL-OneM2M Environmental Sensors adapter instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))

    global scral_module, DOC
    scral_module, args, DOC = util.initialize_module(module_description, abs_path, SCRALEnvOneM2M)
    scral_module.runtime(flask_instance, ENABLE_CHERRYPY)


@flask_instance.route(URI_ENV_NODE, methods=["POST"])
def new_onem2m_request() -> Response:
    """ This function is called when a OneM2M post request is received. """
    logging.debug(new_onem2m_request.__name__ + " method called from: "+request.remote_addr)

    container_path = str(request.json["m2m:sgn"]["sur"])
    substrings = container_path.split("/")
    env_node_id = None
    for i in range(len(substrings)):
        if substrings[i].startswith("env-node"):
            env_node_id = substrings[i]
            break
    if env_node_id is None:
        return make_response(jsonify({ERROR_RETURN_STRING: "Environmental Node ID not found!"}), 400)

    # logging.debug(request.json)
    content_type = request.json["m2m:sgn"]["nev"]["rep"]["m2m:cin"]["cnf"]
    if content_type != ONEM2M_CONTENT_TYPE:
        # raise TypeError("The content: <"+content_type+"> was not recognized! <"+ONEM2M_CONTENT_TYPE+"> is expected!")
        return make_response(jsonify({ERROR_RETURN_STRING: UNKNOWN_CONTENT_TYPE}), 400)

    raw_content = request.json["m2m:sgn"]["nev"]["rep"]["m2m:cin"]["con"]
    if type(raw_content) is str:
        content = json.loads(raw_content)
    elif type(raw_content) is dict:
        content = raw_content
    else:
        # raise TypeError("The content type is "+str(type(raw_content))+", it must be a String or a Dictionary")
        return make_response(jsonify({ERROR_RETURN_STRING: WRONG_CONTENT_TYPE}), 400)

    if scral_module is None:
        return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)

    # -> ### DATASTREAM REGISTRATION ###
    rc = scral_module.get_resource_catalog()
    if env_node_id not in rc:
        logging.info("Node: " + str(env_node_id) + " registration.")
        try:
            latitude = content["lat"]
        except KeyError:
            latitude = content["latitude"]
        try:
            longitude = content["lon"]
        except KeyError:
            longitude = content["longitude"]
        response = scral_module.ogc_datastream_registration(env_node_id, (latitude, longitude))
        if response.status_code != 200:
            return response

    # -> ### OBSERVATION REGISTRATION ###
    response = scral_module.ogc_observation_registration(env_node_id, content, request.json["m2m:sgn"])
    return response


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices() -> Response:
    """ This endpoint gives access to the resource catalog. """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    to_ret = jsonify(scral_module.get_resource_catalog())
    return make_response(to_ret, 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module() -> str:
    """ Checking if SCRAL is running.
        :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    to_ret = "<h1>SCRAL is running!</h1>\n"
    link = DOC[ENDPOINT_URL_KEY] + ":" + str(DOC[ENDPOINT_PORT_KEY])
    to_ret += "<h2>SCRALEnvOneM2M is listening on address: "+link+"</h2>"
    to_ret += "<h3>To have access to all active devices and to the relative DATASTREAM id, send a GET requesto to: " \
              + link + URI_ACTIVE_DEVICES + "</h3>"
    to_ret += "<h3>To send an OBSERVATION or to REGISTER a new device, send a POST request to: " \
              + link + URI_ENV_NODE + "</h3>"
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
