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
"""
    SCRAL util
    This file contains several utility functions that could be used in different modules.
"""

import json
import logging
import re
import sys

import requests
from arrow.arrow import Arrow


def init_logger(debug_level):
    """ This function configure the logger according to af specified debug_level taken from logging class. """

    logging.basicConfig(format="%(message)s")
    logging.getLogger().setLevel(level=debug_level)
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)04d %(levelname)s: %(message)s", datefmt="%H:%M:%S"))


def load_from_file(filename):
    """ Read information about a specific configuration from a file and return a JSON object with the related data.

        :param filename: the full-path of the configuration file
        :return: a Dictionary containing the configuration data
    """

    file_p = open(filename)
    if file_p:
        content_json = json.load(file_p)
        file_p.close()
        return content_json
    else:
        raise FileNotFoundError("File: "+filename+" not found or you don't have permission to read it!")


def write_to_file(filename, data):
    """ Update a configuration file (it will be created if does not exists.

        :param filename: the full-path of the configuration file
        :param data: a dictionary containing the configuration data
    """

    with open(filename, 'w+') as outfile:
        json.dump(data, outfile)
        outfile.write('\n')


def test_connectivity(server_address, server_username=None, server_password=None):
    """ This function checks if a REST connection is correctly configured.

    :param server_address: The address of the OGC server
    :param server_username: The username necessary to be authenticated on the server
    :param server_password: The password related to the given username
    :return: True, if it is possible to establish a connection, False otherwise.
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


def get_server_access_token(url, credentials, headers, token_prefix="", token_suffix=""):
    """ This function get authorized token from a target server

    :param: url: The URL of the target server
    :param: credentials: available access credentials
    :param: headers: REST query headers
    :return: a dictionary with limited-time-available access credentials
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
    print("\nSCRAL is turning down now, thanks for choosing SCRAL!")
    print("(c) 2019, LINKS Foundation\n developed by Jacopo Foglietti & Luca Mannella.\n")
    sys.exit(0)


def build_ogc_unit_of_measure(property_name):
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

    return uom


def from_utc_to_query(utc_timestamp: Arrow, remove_milliseconds=True):
    """ This function convert an arrow UTC timestamp in a data format adapted for a REST request.

    :param utc_timestamp: A timestamp in Arrow format (e.g. 2019-05-13T11:22:33+01:00)
    :param remove_milliseconds: if set to True, milliseconds are removed from timestamp
    :return: The timestamp adapted for a REST query (e.g. 2019-05-13T11%3A22%3A33Z)
    """
    time_stamp = str(utc_timestamp).split('+')[0]
    if remove_milliseconds:
        time_stamp = str(utc_timestamp).split('.')[0]
    time_stamp += 'Z'

    return re.sub(':', '%3A', str(time_stamp))
