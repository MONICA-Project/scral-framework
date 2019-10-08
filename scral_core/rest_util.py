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
from typing import Tuple

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
