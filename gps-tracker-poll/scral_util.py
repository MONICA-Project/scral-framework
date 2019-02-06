##########################################################################
#        _____ __________  ___    __                                     #
#       / ___// ____/ __ \/   |  / /                                     #
#       \__ \/ /   / /_/ / /| | / /                                      #
#      ___/ / /___/ _, _/ ___ |/ /___                                    #
#     /____/\____/_/ |_/_/  |_/_____/  v.2.0 - enhanced by Python 3      #
#                                                                        #
# (c) 2019 by Jacopo Foglietti & Luca Mannella                           #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md  #
#                                                                        #
##########################################################################
import json


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
