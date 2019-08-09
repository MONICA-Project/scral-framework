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
import argparse
import logging
import signal
import sys

import scral_module as scral
from scral_module import util, mqtt_util
from scral_module.constants import END_MESSAGE, DEFAULT_CONFIG, FILENAME_CONFIG


def main():
    util.init_logger(logging.debug)

    parser = argparse.ArgumentParser(prog='MQTT Topic Generator',
                                     epilog="example: mqtt_topic_generator.py -p LST -d Wristband",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-p', '--pilot', default=DEFAULT_CONFIG, type=str, help='the name of the desired pilot')
    parser.add_argument('-d', '--device', type=str, help='the name of the device to integrate')
    parser.add_argument('-n', '--number', type=int, help='number of devices')
    args = parser.parse_args()

    path = FILENAME_CONFIG+"/"+args.pilot+"/"
    filename = args.device + "_" + args.pilot + ".txt"

    topic_prefix = mqtt_util.get_publish_mqtt_topic(args.pilot)
    topic = topic_prefix + "SCRAL/" + args.device + "/"

    with open(path+filename, 'w+') as outfile:
        for i in range(1, args.number):
            w_topic = topic+"("+str(i)+")/Observations"
            outfile.write(w_topic)
        outfile.write('\n')


if __name__ == '__main__':
    print(scral.BANNER % scral.VERSION)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, util.signal_handler)
    main()
    print(END_MESSAGE)
