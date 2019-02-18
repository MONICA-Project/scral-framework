##############################################################################
#      _____ __________  ___    __                                           #
#     / ___// ____/ __ \/   |  / /                                           #
#     \__ \/ /   / /_/ / /| | / /                                            #
#    ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Abstraction Layer  #
#   /____/\____/_/ |_/_/  |_/_____/   v.2.0 - enhanced by Python 3           #
#                                                                            #
# LINKS Foundation, (c) 2019                                                 #
# developed by Jacopo Foglietti & Luca Mannella                              #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md      #
#                                                                            #
##############################################################################
import json
import logging

import requests


def load_from_file(filename):
    """ Read information about a specific configuration from a file and return a JSON object with the related data.

        :param filename: the full-path of the configuration file
        :return: a Dictionary containing the configuration data
    """

    file_p = open(filename)
    content_json = json.load(file_p)
    file_p.close()
    return content_json


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
            logging.info("Network connectivity: VERIFIED")
            return True
        else:
            logging.info("Something wrong during connection!")
            return False

    except Exception as e:
        logging.debug(e)
        return False
