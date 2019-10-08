#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

""" This file contains several utility functions that could be used in different modules. """

import argparse
import json
from logging import Logger
import logging
import os
import re
import sys

from configparser import ConfigParser
from typing import Union, Optional, Dict

import requests
from arrow.arrow import Arrow

from ogc_configuration import OGCConfiguration
from scral_core.scral_module import SCRALModule
from scral_core.constants import DEFAULT_CONFIG, DEFAULT_REST_CONFIG, CREDITS, DEFAULT_LOG_FORMATTER, \
                                 MODULE_NAME_KEY, ENDPOINT_PORT_KEY, ENDPOINT_URL_KEY, PILOT_KEY, \
                                 CONNECTION_PATH_KEY, CONNECTION_FILE_KEY, CATALOG_NAME_KEY, CONFIG_PATH_KEY, \
                                 FILENAME_CONFIG, FILENAME_COMMAND_FILE, \
                                 OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, OPT_LIST


def init_logger(debug_level: Union[int, str]):
    """ This function configure the logger according to the specified debug_level taken from logging class. """

    logging.basicConfig(format="%(message)s")
    logging.getLogger().setLevel(level=debug_level)
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(DEFAULT_LOG_FORMATTER, datefmt="(%b-%d) %H:%M:%S"))


def init_mirrored_logger(log_name: str, debug_level: Union[int, str], output_filename: Optional[str] = None) -> Logger:
    """ This function configure the logger according to the specified debug_level taken from logging class.
        It is possible also to specify a filename on which the log will be mirrored.

    :param log_name: The name assigned to the new generated log.
    :param output_filename: A filename (or filepath) on which the log will be mirrored.
    :param debug_level: A debug value taken from logging class.
    :return: An entity of logging class.
    """

    logger = logging.getLogger(log_name)

    if output_filename:
        fh = logging.FileHandler(output_filename)
        fh.setLevel(level=debug_level)
        fh.setFormatter(logging.Formatter(DEFAULT_LOG_FORMATTER, datefmt="(%b-%d) %H:%M:%S"))
        logger.addHandler(fh)

    return logger


def init_parser(file_to_parse: str) -> ConfigParser:
    parser = ConfigParser()
    files_read = parser.read(file_to_parse)
    if len(files_read) <= 0:
        raise FileNotFoundError("File: '" + file_to_parse + "' not found or you don't have permission to read it!")
    parser.sections()
    return parser


def parse_small_command_line(description: str) -> argparse.Namespace:
    """ This function parses a small version of the "original" command line.

    :param description: The module description that you want to show in -h option.
    :return: an object with all the parsed parameters.
    """
    example_text = "example: start_module.py -p MOVIDA"

    parser = argparse.ArgumentParser(prog='SCRAL', epilog=example_text,
                                     description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-p', '--pilot', default=DEFAULT_CONFIG, type=str, help='the name of the desired pilot')
    args = parser.parse_args()

    return args


def parse_command_line(description: str) -> argparse.Namespace:
    """ This function parses the command line.

    :param description: The module description that you want to show in -h option.
    :return: an object with all the parsed parameters.
    """
    example_text = "example: start_module.py -v -f ./my_conf.conf -c external -p MOVIDA"

    parser = argparse.ArgumentParser(prog='SCRAL', epilog=example_text,
                                     description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='enable verbose mode')
    parser.add_argument('-o', '--ogc', dest='ogc_file', type=str, help='the path of the OGC configuration file')
    parser.add_argument('-c', '--conn', dest='connection_file', type=str,
                        help='the path of the connection configuration')
    parser.add_argument('-p', '--pilot', default=DEFAULT_CONFIG, type=str, help='the name of the desired pilot')
    args = parser.parse_args()

    return args


def initialize_variables(description: str, abs_path: str) -> (dict, Dict[str, str]):
    cmd_line = parse_small_command_line(description)
    pilot_config_folder = cmd_line.pilot.lower() + "/"

    # Preparing all the necessary configuration paths
    config_path = os.path.join(abs_path, FILENAME_CONFIG)
    connection_path = os.path.join(config_path, pilot_config_folder)
    command_line_file = os.path.join(connection_path + FILENAME_COMMAND_FILE)

    # Taking and setting application parameters
    args = load_from_file(command_line_file)
    args[CONFIG_PATH_KEY] = config_path
    args[CONNECTION_PATH_KEY] = connection_path

    # Initialize documentation variable
    try:
        doc = {
            MODULE_NAME_KEY: args[MODULE_NAME_KEY],
            ENDPOINT_PORT_KEY: args[ENDPOINT_PORT_KEY],
            ENDPOINT_URL_KEY: args[ENDPOINT_URL_KEY]
        }
    except KeyError:
        doc = DEFAULT_REST_CONFIG

    return args, doc


def scral_ogc_startup(scral_module_class: SCRALModule.__class__, args: dict) -> (OGCConfiguration, str, str):
    ogc_config = scral_module_class.startup(args, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD)

    # Module initialization and runtime phase
    filename_connection = os.path.join(args[CONNECTION_PATH_KEY] + args[CONNECTION_FILE_KEY])
    try:
        catalog_name = args[CATALOG_NAME_KEY]
    except KeyError:
        catalog_name = args[PILOT_KEY] + "_resource-catalog.json"
        logging.warning("No " + CATALOG_NAME_KEY + " specified. Default name was used '" + catalog_name + "'")

    return ogc_config, filename_connection, catalog_name


def initialize_module(description: str, abs_path: str, scral_module_class: SCRALModule.__class__)\
        -> (SCRALModule, dict, Dict[str, str]):
    args, doc = initialize_variables(description, abs_path)
    ogc_config, filename_connection, catalog_name = scral_ogc_startup(scral_module_class, args)

    module = scral_module_class(ogc_config, filename_connection, args[PILOT_KEY], catalog_name)
    return module, args, doc


def load_from_file(filename: str) -> dict:
    """ Read information about a specific configuration from a file and return a JSON object with the related data.

        :param filename: the full-path of the configuration file.
        :return: a Dictionary containing the configuration data.
    """

    file_p = open(filename)
    if file_p:
        content_json = json.load(file_p)
        file_p.close()
        return content_json
    else:
        raise FileNotFoundError("File: "+filename+" not found or you don't have permission to read it!")


def write_to_file(filename: str, data):
    """ Update a configuration file (it will be created if does not exists.

        :param filename: the full-path of the configuration file.
        :param data: a dictionary containing the configuration data.
    """

    with open(filename, 'w+') as outfile:
        json.dump(data, outfile)
        outfile.write('\n')


def test_connectivity(server_address: str,
                      server_username: Optional[str] = None, server_password: Optional[str] = None):
    """ This function checks if a REST connection is correctly configured.

    :param server_address: The address of the OGC server.
    :param server_username: The username necessary to be authenticated on the server.
    :param server_password: The password related to the given username.
    :return: True if it is possible to establish a connection, False otherwise.
    """

    try:
        if server_username is None and server_password is None:
            r = requests.get(url=server_address)
        else:
            r = requests.get(url=server_address, auth=(server_username, server_password))
        if r.ok:
            logging.info("Network connectivity: VERIFIED. Server "+server_address+" is reachable!")
            return True
        else:
            logging.error("Something wrong during connection!")
            return False

    except Exception as e:
        logging.debug(e)
        return False


def get_server_access_token(url: str, credentials, headers,
                            token_prefix: Optional[str] = "", token_suffix: Optional[str] = ""):
    """ This function get authorized token from a target server.

    :param: url: The URL of the target server.
    :param: credentials: available access credentials.
    :param: headers: REST query headers.
    :return: A dictionary with limited-time-available access credentials.
    """

    auth = None
    try:
        auth = requests.post(url=url, data=json.dumps(credentials), headers=headers)
    except Exception as ex:
        logging.error(ex)

    if auth:
        # enable authorization
        cloud_token = dict()
        cloud_token["Accept"] = "application/json"
        access_token = auth.json()['accessToken']
        cloud_token['Authorization'] = token_prefix + str(access_token) + token_suffix
    else:
        raise ValueError("Credentials " + credentials + " have been denied by the server.")

    logging.info("Access token successfully authorized!")
    return cloud_token


def signal_handler(signal, frame):
    """ This signal handler overwrite the default behaviour of SIGKILL (pressing CTRL+C). """

    logging.critical('You pressed Ctrl+C!')
    print("\nSCRAL is turning down now, thanks for choosing SCRAL!\n"+CREDITS)
    sys.exit(0)


def build_ogc_unit_of_measure(property_name: str) -> Dict[str, str]:
    """ This utility function build a unit of measure dictionary from the specified property_name.
        It was developed for OneM2M Environmental Sensors integration.

    :param property_name: A str containing the name of the property.
    :return: A dict containing more information about the measure.
    """
    uom = {"name": property_name}

    if property_name == "wind-speed":
        uom["symbol"] = "m s^-1"
        uom["definition"] = "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#MeterPerSecond"
    elif property_name == "temperature":
        uom["symbol"] = "degC"
        uom["definition"] = "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeCelsius"
    elif property_name == "pressure":
        uom["symbol"] = "Pa"
        uom["definition"] = "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#Pascal"
    elif property_name == "humidity":
        uom["symbol"] = "kg/m^3"
        uom["definition"] = "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#KilogramPerCubicMeter"
    elif property_name == "position":
        uom["symbol"] = "",
        uom["definition"] = "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeAngle"

    return uom


def from_utc_to_query(utc_timestamp: Arrow, remove_milliseconds: bool = True, html_formatting: bool = False) -> str:
    """ This function convert an arrow UTC timestamp in a data format adapted for a REST request.

    :param utc_timestamp: A timestamp in Arrow format (e.g. 2019-05-13T11:22:33+01:00).
    :param remove_milliseconds: if is set to True, milliseconds are removed from timestamp.
    :param html_formatting: If true the string is HTML encoded (e.g.: ':' converted to "%3A".
    :return: A string timestamp adapted for a REST query (e.g. 2019-05-13T11%3A22%3A33Z).
    """
    time_stamp = str(utc_timestamp).split('+')[0]
    if remove_milliseconds:
        time_stamp = str(utc_timestamp).split('.')[0]
    time_stamp += 'Z'

    if html_formatting:
        return re.sub(':', '%3A', str(time_stamp))

    return time_stamp


def to_html_documentation(module_name: str, link: str,
                          posts: OPT_LIST = None, puts: OPT_LIST = None,
                          gets: OPT_LIST = None, deletes: OPT_LIST = None) -> str:
    """ This function create a piece of HTML containing the list of the desired endpoints.

    :param module_name: The name of the SCRAL module, it will be visualized in the generated HTML.
    :param link: The base link of the endpoints.
    :param posts: All the available POST endpoints, if not available you can also provide an empty tuple/list.
    :param puts: All the available PUT endpoints, if not available you can also provide an empty tuple/list.
    :param gets: All the available GET endpoints, if not available you can also provide an empty tuple/list.
    :param deletes: All the available DELETE endpoints, if not available you can also provide an empty tuple/list.
    :return: Some HTML code properly formatted.
    """
    to_ret = "<h1>SCRAL is running!</h1>\n"
    to_ret += "<h2> "+module_name+" is listening on address \""+link+"\"</h2>"

    to_ret += "<h3>"
    if (posts is not None) and (len(posts) > 0):
        to_ret += "To REGISTER a new device, please send a POST request to: <ul>"
        for post_url in posts:
            to_ret += "<li>" + link + post_url + "</li>"
        to_ret += "</ul>"
    if (deletes is not None) and (len(deletes) > 0):
        to_ret += "To DELETE a registered device, please send a DELETE request to: <ul>"
        for delete_url in deletes:
            to_ret += "<li>" + link + delete_url + "</li>"
        to_ret += "</ul>"
    if (puts is not None) and (len(puts) > 0):
        to_ret += "To send a new OBSERVATION, please send a PUT request to: <ul>"
        for put_url in puts:
            to_ret += "<li>" + link + put_url + "</li>"
        to_ret += "</ul>"
    if (gets is not None) and (len(gets) > 0):
        to_ret += "To retrieve a particular resource, please send a GET request to: <ul>"
        for get_url in gets:
            to_ret += "<li>" + link + get_url + "</li>"
        to_ret += "</ul>"
    to_ret += "</h3>"

    return to_ret
