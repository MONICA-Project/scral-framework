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
from flask import make_response, jsonify


def tests_and_checks(module_name, module, request):
    if not request.json:
        return False, make_response(jsonify({"Error": "Wrong request!"}), 400)

    if not module:
        logging.critical(module_name + "module is not available!")
        return False, make_response(jsonify({"Error": "Internal server error"}), 500)

    return True, "Ok"
