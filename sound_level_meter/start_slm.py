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
import sys
import signal

from flask import Flask, request, jsonify, make_response

import scral_module as scral
import scral_ogc
from scral_module import util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE, ERROR_WRONG_PILOT_NAME, \
    VPN_URL

from sound_level_meter.slm_module import SCRALSoundLevelMeter
from sound_level_meter.constants import VPN_PORT, URL_SLM_LOGIN, CREDENTIALS, SLM_LOGIN_PREFIX, \
    URI_DEFAULT, URI_ACTIVE_DEVICES, URI_SOUND_EVENT, DEVICE_NAME_KEY

flask_instance = Flask(__name__)
module: SCRALSoundLevelMeter = None


def main():
    module_description = "Sound Level Meter integration instance"
    args = util.parse_command_line(module_description)

    # OGC-Configuration
    ogc_config = SCRALSoundLevelMeter.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Module initialization and runtime phase
    global module
    module = SCRALSoundLevelMeter(ogc_config, args.connection_file, args.pilot,
                                  URL_SLM_LOGIN, CREDENTIALS, SLM_LOGIN_PREFIX)
    module.runtime(flask_instance)


@flask_instance.route(URI_SOUND_EVENT, methods=["PUT"])
def new_sound_event():
    """ This function can register an OBSERVATION in the OGC server.
        It is able to accept any new OBSERVED PROPERTY according to the content of "type" field.
        This new property is run-time generated.

    :return: An HTTP Response.
    """
    logging.debug(new_sound_event.__name__ + " method called from: "+request.remote_addr+" \n")

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
    logging.debug(get_active_devices.__name__ + " method called from: "+request.remote_addr+" \n")

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
    logging.debug(test_module.__name__ + " method called from: "+request.remote_addr+" \n")

    link = VPN_URL+":"+str(VPN_PORT)
    posts = ()
    puts = (URI_SOUND_EVENT, )
    gets = (URI_ACTIVE_DEVICES, )
    to_ret = util.to_html_documentation("SCRALSmartGlasses", link, posts, puts, gets)
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
