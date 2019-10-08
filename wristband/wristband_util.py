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
import os
from typing import Dict

from scral_core import util
from scral_core.constants import OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, FILENAME_CONFIG, FILENAME_COMMAND_FILE

from wristband.wristband_module import SCRALWristband
from wristband.constants import URI_WRISTBAND_REGISTRATION, URI_WRISTBAND_ASSOCIATION, URI_WRISTBAND_LOCALIZATION, \
                                URI_WRISTBAND_BUTTON, URI_ACTIVE_DEVICES


def instance_wb_module(pilot_name: str, documentation: Dict[str, any]):
    # Preparing all the necessary configuration paths
    abs_path = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(abs_path, FILENAME_CONFIG)
    connection_path = os.path.join(config_path, pilot_name)
    command_line_file = os.path.join(connection_path + FILENAME_COMMAND_FILE)

    # Taking and setting application parameters
    args = util.load_from_file(command_line_file)
    args["config_path"] = config_path
    args["connection_path"] = connection_path

    # OGC-Configuration
    ogc_config = SCRALWristband.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Initialize documentation variable
    documentation["module_name"] = args["module_name"]
    documentation["endpoint_port"] = args["endpoint_port"]
    documentation["endpoint_url"] = args["endpoint_url"]

    # Module initialization and runtime phase
    filename_connection = os.path.join(connection_path + args['connection_file'])
    catalog_name = args["pilot"] + "_wristband.json"
    return SCRALWristband(ogc_config, filename_connection, args['pilot'], catalog_name)


def wristband_documentation(module_name: str, url: str) -> str:
    deletes = posts = (URI_WRISTBAND_REGISTRATION,)
    puts = (URI_WRISTBAND_ASSOCIATION, URI_WRISTBAND_LOCALIZATION, URI_WRISTBAND_BUTTON)
    gets = (URI_ACTIVE_DEVICES,)
    to_ret = util.to_html_documentation(module_name+" (dumb version)", url, posts, puts, gets, deletes)
    return to_ret
