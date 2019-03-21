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
#
# ROADMAP: these are main steps in which a SCRAL module is divided.
#
# PHASE: INIT + SETUP + BOOT
#   1. Init variables and setup server and MQTT connections
#   2. Read configuration File and load predefined OGC scheme (exit if integrity not satisfied)
#
# #PHASE: DISCOVERY
#   3. Check via discovery if loaded entities are already registered
#   4. If needed, register new entities    to OGC Server
#   5. Retrieve corresponding @iot.id's
#
# #PHASE: INTEGRATION
#   6. Get notified about new OneM2M "containers"
#   7. Upload DATASTREAM entities to OGC Server
#   8. Expose SCRAL endpoint and listen to incoming requests
#
####################################################################################################
import logging
import sys
import signal

from flask import Flask, request, jsonify, make_response

import scral_module as scral
import scral_ogc
from scral_module import util
from scral_module import mqtt_util
from scral_module.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, END_MESSAGE
from scral_module.ogc_configuration import OGCConfiguration

from sound_level_meter.slm_module import SCRALSoundLevelMeter
from sound_level_meter.constants import URL_SLM_LOGIN, CREDENTIALS, SLM_LOGIN_PREFIX, URI_DEFAULT, URI_SOUND_EVENT

flask_instance = Flask(__name__)
slm_module: SCRALSoundLevelMeter = None
verbose = False


def main():
    # parsing command line parameters, it has to be the first instruction
    args = util.parse_command_line("SLM integration instance")

    global verbose  # overwrite verbose flag from command line
    if args.verbose:
        verbose = True
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
        verbose = False

    util.init_logger(logging_level)  # logging initialization

    if not args.connection_file:  # has the connection_file been set?
        logging.critical("Connection file is missing!")
        exit(1)

    if not args.ogc_file:  # has the ogc_file been set?
        logging.critical("OGC configuration file is missing!")
        exit(2)

    pilot_mqtt_topic_prefix = mqtt_util.get_publish_mqtt_topic(args.pilot)  # 'local' is the default configuration value
    if not pilot_mqtt_topic_prefix:
        logging.critical('Wrong pilot name: "' + args.pilot + '"!')
        exit(3)

    logging.info("[PHASE-INIT] The connection file is: " + args.connection_file)
    logging.debug("OGC file: " + args.ogc_file)
    logging.debug("MQTT publishing topic prefix: " + pilot_mqtt_topic_prefix)

    # Storing the OGC server addresses
    connection_config_file = util.load_from_file(args.connection_file)
    ogc_server_address = connection_config_file["REST"]["ogc_server_address"]

    if not util.test_connectivity(ogc_server_address, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD):
        logging.critical("Network connectivity to " + ogc_server_address + " not available!")
        exit(4)

    # OGC model configuration and discovery
    ogc_config = OGCConfiguration(args.ogc_file, ogc_server_address)
    ogc_config.discovery(verbose)

    global slm_module  # Module initialization and runtime phase
    slm_module = SCRALSoundLevelMeter(ogc_config, args.connection_file, pilot_mqtt_topic_prefix,
                                      URL_SLM_LOGIN, CREDENTIALS, SLM_LOGIN_PREFIX)
    slm_module.runtime(flask_instance)


@flask_instance.route(URI_SOUND_EVENT, methods=["PUT"])
def new_sound_event():
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

    datastream_id = slm_module.new_datastream(obs_prop, device_id)
    if datastream_id is False:
        return make_response(jsonify({"Error": "deviceId not recognized."}), 400)
    elif datastream_id is None:
        return make_response(jsonify({"Error": "Internal server error."}), 500)
    else:
        slm_module.ogc_observation_registration(datastream_id, payload["startTime"], payload)
        return make_response(jsonify({"Result": "Ok"}), 201)


@flask_instance.route("/")
def test():
    """ Checking if Flask is working. """
    logging.debug(test.__name__ + " method called \n")

    return "<h1>Flask is running!</h1>"


@flask_instance.route(URI_DEFAULT)
def test_module():
    """ Checking if SCRAL is running. """
    logging.debug(test_module.__name__ + " method called \n")

    to_ret = "<h1>SCRAL module is running!</h1>\n"
    to_ret += "<h2> ToDo: Insert list of API here! </h2>"
    return to_ret


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
