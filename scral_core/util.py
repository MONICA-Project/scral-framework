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

from arrow.arrow import Arrow

from scral_core.constants import CREDITS, DEFAULT_CONFIG, DEFAULT_LOG_FORMATTER, DEFAULT_URL, DEFAULT_MODULE_NAME, \
    MODULE_NAME_KEY, ENDPOINT_PORT_KEY, ENDPOINT_URL_KEY, GOST_PREFIX_KEY, OPT_LIST, \
    CONNECTION_PATH_KEY, CONNECTION_FILE_KEY, CATALOG_NAME_KEY, CONFIG_PATH_KEY, \
    FILENAME_CONFIG, FILENAME_COMMAND_FILE, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, \
    D_CONFIG_KEY, D_CUSTOM_MODE, DEFAULT_REST_PORT, VERBOSE_KEY, OGC_FILE_KEY, ERROR_MISSING_ENV_VARIABLE, D_OGC_USER, \
    D_OGC_PWD


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


def init_doc(args: dict) -> dict:
    """ Initialize documentation variable
    :param args: A dictionary containing relevant documentation fields
    :return:
    """
    doc = {}
    try:
        doc[ENDPOINT_PORT_KEY] = args[ENDPOINT_PORT_KEY]
    except KeyError:
        logging.warning("No port for documentation specified, default one will be used: "+str(DEFAULT_REST_PORT))
        doc[ENDPOINT_PORT_KEY] = DEFAULT_REST_PORT
    try:
        doc[ENDPOINT_URL_KEY] = args[ENDPOINT_URL_KEY]
    except KeyError:
        logging.warning("No URL for documentation specified, default one will be used: " + DEFAULT_URL)
        doc[ENDPOINT_URL_KEY] = DEFAULT_URL
    try:
        doc[MODULE_NAME_KEY] = args[MODULE_NAME_KEY]
    except KeyError:
        logging.warning("No module name for documentation specified, default one will be used: " + DEFAULT_MODULE_NAME)
        doc[MODULE_NAME_KEY] = DEFAULT_MODULE_NAME

    return doc


def init_variables(pilot_name: str, abs_path: str) -> (dict, Dict[str, str]):
    pilot_config_folder = pilot_name+"/"

    # Preparing all the necessary configuration paths
    config_path = os.path.join(abs_path, FILENAME_CONFIG)
    connection_path = os.path.join(config_path, pilot_config_folder)
    command_line_file = os.path.join(connection_path + FILENAME_COMMAND_FILE)

    # Taking and setting application parameters
    args = load_from_file(command_line_file)
    args[CONFIG_PATH_KEY] = config_path
    args[CONNECTION_PATH_KEY] = connection_path

    # Initialize documentation variable
    doc = init_doc(args)

    return args, doc


def init_variables_docker(abs_path: str) -> (dict, Dict[str, str]):
    # Initialize documentation variable
    doc = {}
    try:
        doc[ENDPOINT_PORT_KEY] = os.environ[ENDPOINT_PORT_KEY.upper()]
    except KeyError:
        pass
    try:
        doc[ENDPOINT_URL_KEY] = os.environ[ENDPOINT_URL_KEY.upper()]
    except KeyError:
        pass
    try:
        doc[MODULE_NAME_KEY] = os.environ[MODULE_NAME_KEY.upper()]
    except KeyError:
        pass
    doc = init_doc(doc)

    # Taking and setting application parameters
    args: dict = {}

    try:
        verbose = os.environ[VERBOSE_KEY.upper()]
    except KeyError:
        verbose = 0

    if not verbose:
        args[VERBOSE_KEY] = False
    else:
        args[VERBOSE_KEY] = True

    config_path = os.path.join(abs_path, FILENAME_CONFIG)
    args[CONFIG_PATH_KEY] = config_path

    if OGC_FILE_KEY.upper() not in os.environ.keys():
        logging.critical(OGC_FILE_KEY.upper() + " is missing!")
        exit(ERROR_MISSING_ENV_VARIABLE)
    else:
        args[OGC_FILE_KEY] = os.environ[OGC_FILE_KEY.upper()]

    return args, doc


def scral_ogc_startup(scral_module_class: "SCRALModule".__class__, args: dict) -> ("OGCConfiguration", str, str):
    try:
        username = args[D_OGC_USER]
        password = args[D_OGC_PWD]
    except KeyError:
        username = OGC_SERVER_USERNAME
        password = OGC_SERVER_PASSWORD
    ogc_config = scral_module_class.startup(args, username, password)

    filename_connection = os.path.join(args[CONNECTION_PATH_KEY] + args[CONNECTION_FILE_KEY])
    try:
        catalog_name = args[CATALOG_NAME_KEY]
    except KeyError:
        catalog_name = args[GOST_PREFIX_KEY] + "_" + str(scral_module_class.__name__) + "_resource-catalog.json"
        logging.warning("No " + CATALOG_NAME_KEY + " specified. Default name was used '" + catalog_name + "'")

    return ogc_config, filename_connection, catalog_name


def initialize_module(description: str, abs_path: str, scral_module_class: "SCRALModule".__class__)\
        -> ("SCRALModule", dict, Dict[str, str]):

    # if CONFIG is set to "custom":
    if D_CONFIG_KEY in os.environ.keys() and os.environ[D_CONFIG_KEY].lower() == D_CUSTOM_MODE.lower():
        logging.debug("Custom mode")
        ogc_config, args, doc, pilot_name, catalog_name = startup_module_custom(scral_module_class, abs_path)
        module = scral_module_class(ogc_config, None, pilot_name, catalog_name)
    # if CONFIG not set up to "custom":
    else:
        # if CONFIG is set to a "pilot_name":
        if D_CONFIG_KEY in os.environ.keys():
            pilot_name = os.environ[D_CONFIG_KEY].lower()
            logging.info("Configuration environment variable recognized\nCONFIG: " + pilot_name)
        # if CONFIG not set up:
        else:
            logging.debug("Command line + config file mode")
            cmd_line = parse_small_command_line(description)
            pilot_name = cmd_line.pilot.lower()

        args, doc = init_variables(pilot_name, abs_path)
        try:
            args[D_OGC_USER] = os.environ[D_OGC_USER]
            args[D_OGC_PWD] = os.environ[D_OGC_PWD]
        except KeyError:
            args[D_OGC_USER] = OGC_SERVER_USERNAME
            args[D_OGC_PWD] = OGC_SERVER_PASSWORD

        ogc_config, filename_connection, catalog_name = scral_ogc_startup(scral_module_class, args)
        module = scral_module_class(ogc_config, filename_connection, args[GOST_PREFIX_KEY], catalog_name)

    return module, args, doc


def startup_module_custom(scral_module_class: "SCRALModule".__class__, abs_path: str):
    args, doc = init_variables_docker(abs_path)
    try:
        username = os.environ[D_OGC_USER]
        password = os.environ[D_OGC_PWD]
    except KeyError:
        username = OGC_SERVER_USERNAME
        password = OGC_SERVER_PASSWORD
    ogc_config = scral_module_class.startup(args, username, password)

    pilot_name = os.environ[D_CONFIG_KEY]
    logging.info("CONFIG: " + D_CUSTOM_MODE + "\n Environment variables will be used.")
    catalog_name = str(scral_module_class.__name__) + "_resource-catalog.json"
    return ogc_config, args, doc, pilot_name, catalog_name


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
                          gets: OPT_LIST = None, deletes: OPT_LIST = None,
                          additional_endpoint: bool = True) -> str:
    """ This function create a piece of HTML containing the list of the desired endpoints.

    :param module_name: The name of the SCRAL module, it will be visualized in the generated HTML.
    :param link: The base link of the endpoints.
    :param posts: All the available POST endpoints, if not available you can also provide an empty tuple/list.
    :param puts: All the available PUT endpoints, if not available you can also provide an empty tuple/list.
    :param gets: All the available GET endpoints, if not available you can also provide an empty tuple/list.
    :param deletes: All the available DELETE endpoints, if not available you can also provide an empty tuple/list.
    :param additional_endpoint: if set to true an additional endpoint is printed out.
    :return: Some HTML code properly formatted.
    """
    to_ret = "<h1>SCRAL is running!</h1>\n"
    to_ret += '<h2><em>'+module_name+'</em> is listening on address "'+link+'"</h2>'
    if additional_endpoint:
        to_ret += "<p>If you don't have a VPN connection, you can have access through the MONICA portal. <br>" \
                  "It is necessary to have a configured Keycloak account and to replace in each URL <br>" \
                  "this part: \""+link+"\"<br> " \
                  "with this part: \"https://portal.monica-cloud.eu/scral_container_name\"</p>"

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
            to_ret += '<li> <a href="http://'+link+get_url+'">'+link+get_url+'</a> </li>'
        to_ret += "</ul>"
    to_ret += "</h3>"

    return to_ret
