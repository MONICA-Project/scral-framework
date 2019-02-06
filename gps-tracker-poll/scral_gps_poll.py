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
#
# ROADMAP: these are main steps in which the module processing is divided.
#
# #ToDo: PHASE: INIT + SETUP
#   1. Init variables and setup server and MQTT connections
#
# #ToDo: PHASE: BOOT
#   2. Read configuration File and load predefined OGC scheme (exit if integrity not satisfied)
#   3. Load OGC entities
#
# #ToDo: PHASE: DISCOVERY
#   4. Check via discovery if loaded entities are already registered
#   5. Register new entities if needed, otherwise stored corresponding @iot.id's
#
# #ToDo: PHASE: INTEGRATION
#
################################################################################################################
import argparse
import json
import logging
import os
import sys
from queue import Queue
from threading import Semaphore
import paho.mqtt.client as mqtt

import scral_util
import mqtt_util
from scral_constants import *

banner = """
        _____ __________  ___    __                                     
       / ___// ____/ __ \/   |  / /                                     
       \__ \/ /   / /_/ / /| | / /                                      
      ___/ / /___/ _, _/ ___ |/ /___                                    
     /____/\____/_/ |_/_/  |_/_____/  v.2.0 - enhanced by Python 3

"""

# configuration flags
can_run = True
verbose = True

# client MQTT
mqtt_client = None

# the observation messages queue and its semaphore
q = Queue()
que_sem = Semaphore(1)

# SCRAL local catalog
resource_catalog = {}


def main():
    """ Resource manager for integration of the GPS-TRACKER-GW (by usage of LoRa devices). """
    args = parse_command_line()
    global verbose
    if args.verbose:
        verbose = True
    else:
        verbose = False

    init(args.connection_file)

    global pilot_mqtt_topic
    pilot_mqtt_topic = args.pilot

    boot()
    discovery()
    runtime()

    logging.info("That's all folks!")


def parse_command_line():
    example_text = "example: scral_gps_poll.py -v -f ./my_conf.conf -c external -p hamburg"

    parser = argparse.ArgumentParser(prog='SCRAL GPS Poll', epilog=example_text,
                                     description='Implementation of SCRAL GPS tracker in polling approach',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='enable verbose mode')
    parser.add_argument('-f', '--file', dest='ogc_file', type=str, help='the path of the OGC configuration file')
    parser.add_argument('-c', '--conn', dest='connection_file', type=str,
                        help='the path of the connection configuration')
    parser.add_argument('-p', '--pilot', default=DEFAULT_CONFIG, type=str, help='the name of the desired pilot')
    args = parser.parse_args()
    return args


def init(connection_file):
    """ Setup for server, mqtt and cloud configuration """

    # ##### load connection configuration files ##########
    logging.info("[PHASE-INIT] The connection type is: " + connection_file)
    connection_config_file = scral_util.load_from_file(connection_file)

    # Store broker address/port
    global broker_ip
    broker_ip = connection_config_file["mqtt"]["broker"]
    global broker_port
    broker_port = connection_config_file["mqtt"]["broker_port"]
    ####################################

    # ##### MQTT Broker Connection ##########
    global mqtt_client
    mqtt_client = mqtt.Client()

    # Map event handlers
    mqtt_client.on_connect = mqtt_util.on_connect
    mqtt_client.on_disconnect = mqtt_util.on_disconnect

    logging.info("Try to connect to broker: %s:%s" % (broker_ip, broker_port))
    mqtt_client.connect(broker_ip, broker_port, mqtt_util.DEFAULT_KEEPALIVE)
    mqtt_client.loop_start()
    ###################################

    # Store OGC server addresses
    global ogc_server_address
    ogc_server_address = connection_config_file["REST"]["ogc_server_address"]

    # Load local resource catalog
    if os.path.exists(CATALOG_FILENAME):
        global resource_catalog
        resource_catalog = scral_util.load_from_file(CATALOG_FILENAME)
        logging.ingo('[PHASE-INIT] Resource Catalog: ', json.dumps(resource_catalog))
    else:
        logging.info("Resource catalog does not exist, it will be created later")


def boot():
    pass


def discovery():
    pass


def runtime():
    pass


def init_logger():
    logging.basicConfig(format="%(message)s")
    if verbose:
        logging.getLogger().setLevel(level=logging.DEBUG)
    else:
        logging.getLogger().setLevel(level=logging.INFO)
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)04d %(levelname)s: %(message)s", datefmt="%H:%M:%S"))


if __name__ == '__main__':
    # set default string encoding  # reload(sys)
    # sys.setdefaultencoding('utf-8')

    print(banner)
    sys.stdout.flush()
    init_logger()
    main()
