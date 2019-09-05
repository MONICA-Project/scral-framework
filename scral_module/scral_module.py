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
ROADMAP: these are main steps in which SCRAL module processing is divided.

PHASE STARTUP: INIT + SETUP + BOOT
  1. Init variables and setup server and MQTT connections
  2. Read configuration File and load predefined OGC scheme
     (abort if integrity not satisfied)

PHASE INIT: DISCOVERY
  3. Check via discovery if loaded entities are already registered
  4. If needed, register new entities in OGC Server
  5. Retrieve corresponding @iot.id's

PHASE RUNTIME: INTEGRATION
  To be implemented by extender
"""

#############################################################################
import copy
import json
import logging
import os
from abc import abstractmethod

import arrow
import paho.mqtt.client as mqtt

from scral_module.constants import DEFAULT_KEEPALIVE, DEFAULT_MQTT_QOS, DEFAULT_UPDATE_INTERVAL, \
    CATALOG_FOLDER, CATALOG_FILENAME, \
    ERROR_MISSING_CONNECTION_FILE, ERROR_MISSING_OGC_FILE, ERROR_NO_SERVER_CONNECTION, ERROR_WRONG_PILOT_NAME
from scral_module.ogc_configuration import OGCConfiguration
from scral_module import util
from scral_module import mqtt_util

verbose = False


class SCRALModule(object):
    """ This class is the base entity of SCRAL framework.
        When you want to develop a new SCRAL module, you have to extend this class (or one of the realted subclasses
        e.g., SCRALRESTModule), extend (if necessary) the __init__ initializer and
        to implement the runtime method (that actually does not have a default implementation).
    """

    @staticmethod
    def startup(args, ogc_server_username=None, ogc_server_password=None):
        """ The startup method initializes an OGCConfiguration using some arguments.
            The OGCConfiguration have to be passed to the SCRALModule initializer.

        :param args: Some command line arguments, every module can extend this parameter, SCRALModule wants at least:
                     {"verbose": bool, "connection_file": str, "ogc_file": str}
        :param ogc_server_username: [OPT] The username of the OGC Server to use for OGC configuration.
        :param ogc_server_password: [OPT] The password related to the username.
        :return: An instance of OGCConfiguration.
        """

        global verbose  # overwrite verbose flag from command line
        if args['verbose']:
            verbose = True
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO
            verbose = False

        util.init_logger(logging_level)  # logging initialization

        if not args['connection_file']:  # has the connection_file been set?
            logging.critical("Connection file is missing!")
            exit(ERROR_MISSING_CONNECTION_FILE)
        if not args['ogc_file']:  # has the ogc_file been set?
            logging.critical("OGC configuration file is missing!")
            exit(ERROR_MISSING_OGC_FILE)

        logging.info("Connection file: " + args['connection_file'])
        logging.debug("Connection file stored in: " + args["connection_path"])
        logging.info("OGC file: " + args['ogc_file'])
        logging.debug("OGC file stored in: " + args["config_path"])

        # Storing the OGC server addresses
        filename_connection = args["connection_path"] + args['connection_file']
        connection_config_file = util.load_from_file(filename_connection)
        ogc_server_address = connection_config_file["REST"]["ogc_server_address"]

        # Testing OGC server connectivity
        if not util.test_connectivity(ogc_server_address, ogc_server_username, ogc_server_password):
            logging.critical("Network connectivity to " + ogc_server_address + " not available!")
            exit(ERROR_NO_SERVER_CONNECTION)

        # OGC model configuration and discovery
        full_ogc_filename = args["config_path"] + args['ogc_file']
        ogc_config = OGCConfiguration(full_ogc_filename, ogc_server_address)
        ogc_config.discovery(verbose)
        return ogc_config

    def __init__(self, ogc_config: OGCConfiguration, connection_file: str, pilot: str, catalog_name=CATALOG_FILENAME):
        """ Initialize the SCRALModule:
            Preparing the catalog, instantiating tje MQTT Client and stores all relevant connection information.

        :param ogc_config: An instance of an OGCConfiguration.
        :param connection_file: The path of the connection file, it has to contain the address of the MQTT broker.
        :param pilot: The prefix of the MQTT topic used to publish information.
        """

        # 1 Storing the OGC configuration
        self._ogc_config = ogc_config
        # 2 Load connection configuration file
        connection_config_file = util.load_from_file(connection_file)

        # 3 Load local resource catalog
        self._catalog_fullpath = CATALOG_FOLDER + catalog_name
        if os.path.exists(self._catalog_fullpath):
            self._resource_catalog = util.load_from_file(self._catalog_fullpath)
            self.print_catalog()
        else:
            logging.info("No resource catalog <" + catalog_name + "> available.")
            self._resource_catalog = {}

        # 4 Creating an MQTT Publisher
        # Retrieving pilot name --- 'local' is the default configuration value
        pilot_mqtt_topic_prefix = mqtt_util.get_publish_mqtt_topic(pilot)
        if not pilot_mqtt_topic_prefix:
            logging.critical('Wrong pilot name: "' + pilot + '"!')
            exit(ERROR_WRONG_PILOT_NAME)
        else:
            logging.debug("MQTT publishing topic prefix: " + pilot_mqtt_topic_prefix)
        self._topic_prefix = pilot_mqtt_topic_prefix
        self._pub_broker_address = connection_config_file["mqtt"]["pub_broker"]
        self._pub_broker_port = connection_config_file["mqtt"]["pub_broker_port"]
        self._pub_broker_keepalive = connection_config_file["mqtt"]["pub_broker_keepalive"]

        self._mqtt_publisher = mqtt.Client()
        self._mqtt_publisher.on_connect = mqtt_util.on_connect
        self._mqtt_publisher.on_disconnect = mqtt_util.automatic_reconnection

        logging.info(
            "Try to connect to broker: %s:%s for PUBLISHING..." % (self._pub_broker_address, self._pub_broker_port))
        logging.debug("MQTT Client ID is: " + str(self._mqtt_publisher._client_id))
        self._mqtt_publisher.connect(self._pub_broker_address, self._pub_broker_port, self._pub_broker_keepalive)
        self._mqtt_publisher.loop_start()

        # 5 Preparing module analysis information
        self._active_devices = {"actual_counter": 0, "last_update": arrow.utcnow()}
        try:
            self._active_devices["update_interval"] = connection_config_file["update_interval"]
            logging.info("Number of active devices will be refreshed (if an observation is received) every "
                         + str(self._active_devices["update_interval"]) + " seconds.")
        except KeyError:
            logging.warning("No update interval specified inside configuration file..." +
                            "Default value "+str(DEFAULT_UPDATE_INTERVAL)+" will be used!")
            self._active_devices["update_interval"] = DEFAULT_UPDATE_INTERVAL

    def get_mqtt_connection_address(self):
        return self._pub_broker_address

    def get_mqtt_connection_port(self):
        return self._pub_broker_port

    def get_ogc_config(self):
        return self._ogc_config

    def get_resource_catalog(self) -> dict:
        return self._resource_catalog

    def get_active_devices(self) -> dict:
        """ This method gives access to the resource catalog with few additional information. """

        tmp_rc = dict(self._resource_catalog)
        # active_devices_count = 0
        # for dev in tmp_rc:
        #    if "last_msg" in dev:
        #        timestamp = arrow.get(dev["last_msg"])
        #        diff = arrow.utcnow() - timestamp
        #        diff_sec = abs(diff.total_seconds())
        #        if abs(diff_sec) > 120:
        #            active_devices_count += 1

        tmp_rc["registered_devices"] = len(tmp_rc)
        # tmp_rc["active_devices"] = active_devices_count

        tmp_active_devices = copy.deepcopy(self._active_devices)
        tmp_active_devices["last_update"] = str(tmp_active_devices["last_update"])
        # x = json.dumps(tmp_active_devices, indent=2, sort_keys=True)
        tmp_rc["active_devices"] = tmp_active_devices

        return tmp_rc

    def get_topic_prefix(self) -> str:
        return self._topic_prefix

    def mqtt_publish(self, topic: str, payload, qos=DEFAULT_MQTT_QOS, to_print=True) -> bool:
        """ Publish the payload given as parameter to the MQTT publisher

        :param topic: The MQTT topic on which the client will publish the message.
        :param payload: Data to send (according to Paho documentation could be: None, str, bytearray, int or float).
        :param qos: The desired quality of service (it has an hardcoded default value).
        :param to_print: To enable or not a debug print.
        :return: True if the data was successfully sent, False otherwise.
        """
        if to_print:
            msg = "\nOn topic '" + topic + "' will be send the following payload:\n" + str(payload)
            logging.info(msg)

        info = None
        try:
            info = self._mqtt_publisher.publish(topic, payload, qos)
        except Exception as ex:
            logging.error("Exception caught during MQTT publish: {0}".format(ex))

        if not info:
            return False
        elif info.rc == mqtt.MQTT_ERR_SUCCESS:
            # time_format = 'YYYY-MM-DDTHH:mm:ss.SZ'

            now = arrow.utcnow()
            logging.info("Message successfully sent at: " + str(now))
            dict_payload = json.loads(payload)
            try:
                phenomenon_time = dict_payload["phenomenonTime"]
                diff = now - arrow.get(phenomenon_time)
                logging.debug("Time elapsed since PhenomenonTime: %.3f seconds." % diff.total_seconds())
            except KeyError:
                pass

            try:
                result_time = dict_payload["resultTime"]
                diff = now - arrow.get(result_time)
                logging.debug("Time elapsed since ResultTime: %.3f seconds." % diff.total_seconds())
            except KeyError:
                pass

            return True
        else:
            logging.error("Something wrong during MQTT publish. Error code retrieved: {0}".format(str(info.rc)))
            return False

    def print_catalog(self):
        """ Print resource catalog on log. """

        logging.info("[PHASE-INIT] Resource Catalog <" + self._catalog_fullpath + ">:")
        for key, value in self._resource_catalog.items():
            logging.info(key + ": " + json.dumps(value))
        logging.info("--- End of Resource Catalog ---\n")

    def update_file_catalog(self):
        """ Update the resource catalog on file. """

        # with open(self._catalog_fullpath, 'w+') as outfile:
        #     json.dump(self._resource_catalog, outfile)
        #     outfile.write('\n')
        with open(self._catalog_fullpath, 'w') as f:
            for chunk in json.JSONEncoder().iterencode(self._resource_catalog):
                f.write(chunk)

    def _update_active_devices_counter(self):
        if not self._active_devices:
            logging.error("Trying to update active_devices structure... But was not initialized!")
            return

        try:
            current_time = arrow.utcnow()
            time_diff = (current_time - self._active_devices["last_update"]).total_seconds()
            if time_diff < self._active_devices["update_interval"]:
                self._active_devices["actual_counter"] += 1
            else:
                self._active_devices["counter"] = self._active_devices["actual_counter"]
                self._active_devices["actual_counter"] = 1
                self._active_devices["last_update"] = current_time
        except KeyError:
            logging.error("KeyError: trying to update active_devices structure... But a field is missing!")


    @abstractmethod
    def runtime(self):
        """ This is an abstract method that has to be overwritten.
            It manages the runtime operation of the module.
        """
        raise NotImplementedError("Implement runtime method in subclasses")

# def ogc_datastream_registration(self, ogc_devices_server_url, certificate_path=None):
    #     """ It manages the registration of the data inside OGC server. """
    #     r = None
    #     try:
    #         r = requests.get(url=ogc_devices_server_url, verify=certificate_path)
    #     except SSLError as tls_exception:
    #         logging.error("Error during TLS connection, the connection could be insecure or "
    #                       "the certificate_path could be self-signed...\n" + str(tls_exception))
    #     except Exception as ex:
    #         logging.error(ex)
    #
    #     if r is None or not r.ok:
    #         raise ConnectionError(
    #             "Connection status: " + str(r.status_code) + "\nImpossible to establish a connection" +
    #             " or resources not found for: " + ogc_devices_server_url)
    #     else:
    #         logging.debug("Connection status: " + str(r.status_code))
    #
    #     # Collect OGC information needed to build DATASTREAMs payload
    #     thing = self._ogc_config.get_thing()  # Assumption: usually only 1 thing is defined for each module
    #     thing_id = thing.get_id()
    #     thing_name = thing.get_name()
    #
    #     devices = r.json()[GOST_RESULT_KEY]
    #     for dev in devices:
    #         iot_id = dev[OGC_ID_KEY]
    #         device_id = dev[OGC_DEVICE_NAME_KEY]
    #         self._resource_catalog[iot_id] = {}
    #
    #         for sensor in self._ogc_config.get_sensors():
    #             sensor_id = sensor.get_id()
    #             sensor_name = sensor.get_name()
    #
    #             for op in self._ogc_config.get_observed_properties():
    #                 property_id = op.get_id()
    #                 property_name = op.get_name()
    #                 property_description = op.get_description()
    #
    #                 datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + device_id
    #                 uom = util.build_ogc_unit_of_measure(property_name.lower())
    #
    #                 datastream = OGCDatastream(name=datastream_name,
    #                                            ogc_property_id=property_id, ogc_sensor_id=sensor_id,
    #                                            ogc_thing_id=thing_id,  x=0.0, y=0.0, unit_of_measurement=uom,
    #                                            description="Datastream for "+property_description+" of "+device_id)
    #                 datastream_id = self._ogc_config.entity_discovery(
    #                     datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)
    #
    #                 datastream.set_id(datastream_id)
    #                 self._ogc_config.add_datastream(datastream)
    #
    #                 self._resource_catalog[iot_id][property_name] = datastream_id
    #
    #       self.update_file_catalog()
