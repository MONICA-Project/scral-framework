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
    SCRAL - rest_util
    This file contains several REST utility functions that could be used in different modules.
"""
import logging
from typing import Tuple, Optional

import requests
from flask import make_response, jsonify, Request, Response

from scral_core.scral_module import SCRALModule
from scral_core.constants import SUCCESS_RETURN_STRING, TEST_PASSED, \
                                 ERROR_RETURN_STRING, WRONG_REQUEST, INTERNAL_SERVER_ERROR


def tests_and_checks(module_name: str, module: SCRALModule, request: Request) -> Tuple[bool, Response]:
    if not request.json:
        return False, make_response(jsonify({ERROR_RETURN_STRING: WRONG_REQUEST}), 400)

    if not module:
        logging.critical(module_name + "module is not available!")
        return False, make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)

    return True, make_response(jsonify({SUCCESS_RETURN_STRING: TEST_PASSED}), 200)


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
