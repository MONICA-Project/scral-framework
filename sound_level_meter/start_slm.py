#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#############################################################################
#      _____ __________  ___    __                                          #
#     / ___// ____/ __ \/   |  / /                                          #
#     \__ \/ /   / /_/ / /| | / /                                           #
#    ___/ / /___/ _, _/ ___ |/ /___                                         #
#   /____/\____/_/ |_/_/  |_/_____/   Smart City Resource Adaptation Layer  #
#                                                                           #
# LINKS Foundation, (c) 2017-2020                                           #
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
from typing import Optional

from flask import Flask, request, jsonify, make_response, Response

from scral_ogc import OGCObservedProperty

import scral_core as scral
from scral_core import util, rest_util
from scral_core.constants import DEFAULT_REST_CONFIG, ENABLE_CHERRYPY, END_MESSAGE, SUCCESS_RETURN_STRING, \
    ENDPOINT_URL_KEY, ENDPOINT_PORT_KEY, MODULE_NAME_KEY, GOST_PREFIX_KEY, \
    ERROR_RETURN_STRING, INTERNAL_SERVER_ERROR, DEVICE_NOT_REGISTERED, D_CONFIG_KEY, D_CUSTOM_MODE, D_OGC_USER, \
    D_OGC_PWD, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD

from sound_level_meter.slm_module import SCRALSoundLevelMeter
from sound_level_meter.constants import URL_SLM_LOGIN, CREDENTIALS, SLM_LOGIN_PREFIX, \
    URI_DEFAULT, URI_ACTIVE_DEVICES, URI_SOUND_EVENT, URI_RESOURCE_CATALOG,  \
    DEVICE_ID_KEY, DEVICE_NAME_KEY, DESCRIPTION_KEY, DEFINITION_KEY, TYPE_KEY, START_TIME_KEY

flask_instance = Flask(__name__)
scral_module: Optional[SCRALSoundLevelMeter] = None
DOC = DEFAULT_REST_CONFIG


def main():
    global scral_module, DOC

    module_description = "Sound Level Meter integration instance"
    abs_path = os.path.abspath(os.path.dirname(__file__))

    if D_CONFIG_KEY in os.environ.keys() and os.environ[D_CONFIG_KEY].lower() == D_CUSTOM_MODE.lower():
        ogc_config, args, DOC, preference_folder, catalog_name = \
            util.startup_module_custom(SCRALSoundLevelMeter, abs_path)
        scral_module = SCRALSoundLevelMeter(ogc_config=ogc_config, config_filename=None, url_login=URL_SLM_LOGIN,
                                            credentials=CREDENTIALS, catalog_name=catalog_name,
                                            token_prefix=SLM_LOGIN_PREFIX)
    else:
        if D_CONFIG_KEY in os.environ.keys():
            preference_folder = os.environ[D_CONFIG_KEY].lower()
            print(D_CONFIG_KEY+": " + preference_folder)
        else:
            print("Developer mode: command line parameters are required.")
            cmd_line = util.parse_small_command_line(module_description)
            preference_folder = cmd_line.preference.lower()

        args, DOC = util.init_variables(preference_folder, abs_path)
        try:
            args[D_OGC_USER] = os.environ[D_OGC_USER]
            args[D_OGC_PWD] = os.environ[D_OGC_PWD]
        except KeyError:
            args[D_OGC_USER] = OGC_SERVER_USERNAME
            args[D_OGC_PWD] = OGC_SERVER_PASSWORD

        ogc_config, filename_config, catalog_name = util.scral_ogc_startup(SCRALSoundLevelMeter, args)
        scral_module = SCRALSoundLevelMeter(ogc_config=ogc_config, config_filename=filename_config,
                                            url_login=URL_SLM_LOGIN, credentials=CREDENTIALS,
                                            catalog_name=catalog_name, token_prefix=SLM_LOGIN_PREFIX)

    scral_module.runtime(flask_instance, ENABLE_CHERRYPY)


@flask_instance.route(URI_SOUND_EVENT, methods=["PUT"])
def new_sound_event() -> Response:
    """ This function can register an OBSERVATION in the OGC server.
        It is able to accept any new OBSERVED PROPERTY according to the content of "type" field.
        This new property is run-time generated.

    :return: An HTTP Response.
    """
    logging.debug(new_sound_event.__name__ + " method called from: "+request.remote_addr)

    ok, status = rest_util.tests_and_checks(DOC[MODULE_NAME_KEY], scral_module, request)
    if not ok:
        return status

    payload = request.json
    lower_payload = {k.lower(): v for k, v in request.json.items()}  # this payload has all the keys in lower case
    property_name = lower_payload[TYPE_KEY.lower()]  # accessing to lower_payload fields require to lower constants too
    try:
        property_description = lower_payload[DESCRIPTION_KEY.lower()]
    except KeyError:
        property_description = property_name + " description"
    try:
        property_definition = lower_payload[DEFINITION_KEY.lower()]
    except KeyError:
        property_definition = property_name + " definition"

    obs_prop = OGCObservedProperty(property_name, property_description, property_definition)
    device_id = lower_payload[DEVICE_ID_KEY.lower()]

    datastream_id = scral_module.new_datastream(device_id, obs_prop)
    if datastream_id is False:
        return make_response(jsonify({ERROR_RETURN_STRING: DEVICE_NOT_REGISTERED}), 400)
    elif datastream_id is None:
        return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)
    else:
        scral_module.ogc_observation_registration(datastream_id, lower_payload[START_TIME_KEY.lower()], payload)
        return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)


@flask_instance.route(URI_ACTIVE_DEVICES, methods=["GET"])
def get_active_devices() -> Response:
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr)

    rc_to_ret = {}
    rc_copy = copy.deepcopy(scral_module.get_active_devices())
    for key, item in rc_copy.items():
        if isinstance(item, dict):
            if DEVICE_NAME_KEY in item.keys():
                key = item.pop(DEVICE_NAME_KEY)
        rc_to_ret[key] = item

    return make_response(jsonify(rc_to_ret), 200)


@flask_instance.route(URI_RESOURCE_CATALOG, methods=["GET"])
def get_resource_catalog() -> Response:
    """ This endpoint gives access to the resource catalog.
    :return: A JSON containing thr resource catalog.
    """
    logging.debug(get_resource_catalog.__name__ + " method called from: "+request.remote_addr)
    return make_response(jsonify(scral_module.get_resource_catalog()), 200)


@flask_instance.route(URI_DEFAULT, methods=["GET"])
def test_module() -> str:
    """ Checking if SCRAL is running.
        :return: A str containing some information about possible endpoints.
    """
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr)

    link = DOC[ENDPOINT_URL_KEY]+":"+str(DOC[ENDPOINT_PORT_KEY])
    posts = ()
    puts = (URI_SOUND_EVENT, )
    gets = (URI_ACTIVE_DEVICES, )
    to_ret = util.to_html_documentation(DOC[MODULE_NAME_KEY], link, posts, puts, gets)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
