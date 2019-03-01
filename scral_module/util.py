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
import json
import logging
import sys

import requests


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


def consistency_check(discovery_result, name, filter_name, verbose=False):
    """ This function checks if an OGC entity is already registered. """

    if len(discovery_result) > 1:
        logging.error("Duplicate found: please verify OGC-naming!")
        logging.info("Current Filter: " + filter_name + "'" + name + "'")
        if verbose:
            z = 0
            while z < len(discovery_result):
                logging.debug(discovery_result[z])
                z += 1
        return False

    return True


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


def signal_handler(signal, frame):
    logging.critical('You pressed Ctrl+C!')
    print("\nSCRAL is turning down now, thanks for choosing SCRAL!")
    print("(c) 2019, LINKS Foundation\n developed by Jacopo Foglietti & Luca Mannella.\n")
    sys.exit(0)


def build_ogc_unit_of_measure(property_name):
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
