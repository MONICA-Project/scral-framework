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
import random
import sys
from abc import abstractmethod
from typing import Dict, Optional

import arrow
import paho.mqtt.client as mqtt

from scral_core.constants import DEFAULT_KEEPALIVE, DEFAULT_MQTT_QOS, DEFAULT_UPDATE_INTERVAL, MQTT_CLIENT_PREFIX, \
    CONNECTION_FILE_KEY, CONNECTION_PATH_KEY, CONFIG_PATH_KEY, OGC_FILE_KEY, REST_KEY, OGC_SERVER_ADD_KEY, COUNTER_KEY, \
    REGISTERED_DEVICES_KEY, LAST_UPDATE_KEY, ACTUAL_COUNTER_KEY, UPDATE_INTERVAL_KEY, ACTIVE_DEVICES_KEY, VERBOSE_KEY, \
    ERROR_MISSING_CONNECTION_FILE, ERROR_MISSING_OGC_FILE, ERROR_NO_SERVER_CONNECTION, ERROR_WRONG_PILOT_NAME, \
    CATALOG_FOLDER, CATALOG_FILENAME, D_CUSTOM_MODE, D_CONFIG_KEY, ERROR_MISSING_ENV_VARIABLE, D_PUB_BROKER_URI_KEY, \
    D_PUB_BROKER_PORT_KEY, BROKER_DEFAULT_PORT, D_PUB_BROKER_KEEPALIVE_KEY, DEFAULT_CONFIG, D_GOST_MQTT_PREFIX_KEY, \
    DEFAULT_GOST_PREFIX

from scral_core.ogc_configuration import OGCConfiguration
from scral_core import util, mqtt_util, rest_util

verbose = False


class SCRALModule(object):
    """ This class is the base entity of SCRAL framework.
        When you want to develop a new SCRAL module, you have to extend this class (or one of the related subclasses
        e.g., SCRALRESTModule), extend (if necessary) the __init__ initializer and you have to implement
        the runtime method (that actually does not have a default implementation).
    """

    @staticmethod
    def startup(args: Dict[str, str],
                ogc_server_username: Optional[str] = None, ogc_server_password: Optional[str] = None) \
            -> OGCConfiguration:
        """ The startup method initializes an OGCConfiguration using some arguments.
            The OGCConfiguration have to be passed to the SCRALModule initializer.

        :param args: Some command line arguments, every module can extend this parameter, SCRALModule wants at least:
                     { "verbose": bool, "connection_file": str, "ogc_file": str, "connection_file": str,
                     "connection_path": str , "config_path": str }
        :param ogc_server_username: [OPT] The username of the OGC Server to use for OGC configuration.
        :param ogc_server_password: [OPT] The password related to the username.
        :return: An instance of OGCConfiguration.
        """

        global verbose
        # 0) overwrite verbose flag from args
        if args[VERBOSE_KEY]:
            verbose = True
            logging_level = logging.DEBUG
        else:
            verbose = False
            logging_level = logging.INFO

        # 1) logging initialization
        util.init_logger(logging_level)

        # 2) has the ogc_file been set?
        if not args[OGC_FILE_KEY]:
            logging.critical("OGC configuration file is missing!")
            exit(ERROR_MISSING_OGC_FILE)
        else:
            logging.info("OGC file: " + args[OGC_FILE_KEY])
            logging.debug("OGC file stored in: " + args[CONFIG_PATH_KEY])

        # 3) Is there a connection file?
        ogc_server_address = None
        # 3a) Custom mode
        if D_CONFIG_KEY in os.environ.keys() and os.environ[D_CONFIG_KEY].lower() == D_CUSTOM_MODE:
            logging.info("Custom mode, no connection file required.")

            if OGC_SERVER_ADD_KEY.upper() not in os.environ.keys():
                logging.critical(OGC_SERVER_ADD_KEY.upper() + " is missing!")
                exit(ERROR_MISSING_ENV_VARIABLE)
            else:
                ogc_server_address = os.environ[OGC_SERVER_ADD_KEY.upper()]
        # 3b) No connection file
        elif not args[CONNECTION_FILE_KEY]:  # has the connection_file been set?
            logging.critical("Connection file is missing!")
            exit(ERROR_MISSING_CONNECTION_FILE)
        # 3c) Connection file properly set
        else:
            logging.info("Connection file: " + args[CONNECTION_FILE_KEY])
            logging.debug("Connection file stored in: " + args[CONNECTION_PATH_KEY])

            # Storing the OGC server addresses
            filename_connection = args[CONNECTION_PATH_KEY] + args[CONNECTION_FILE_KEY]
            connection_config_file = util.load_from_file(filename_connection)
            ogc_server_address = connection_config_file[REST_KEY][OGC_SERVER_ADD_KEY]

        # 4) Testing OGC server connectivity
        if not rest_util.test_connectivity(ogc_server_address, ogc_server_username, ogc_server_password):
            logging.critical("Network connectivity to " + ogc_server_address + " not available!")
            exit(ERROR_NO_SERVER_CONNECTION)

        # 5) OGC model configuration and discovery
        full_ogc_filename = args[CONFIG_PATH_KEY] + args[OGC_FILE_KEY]
        ogc_config = OGCConfiguration(full_ogc_filename, ogc_server_address)
        ogc_config.discovery(verbose)
        return ogc_config

    def __init__(self, ogc_config: OGCConfiguration, connection_file: str, pilot: str,
                 catalog_name: str = CATALOG_FILENAME):
        """ Initialize the SCRALModule:
            Preparing the catalog, instantiating the MQTT Client and stores all relevant connection information.

        :param ogc_config: An instance of an OGCConfiguration.
        :param connection_file: The path of the connection file, it has to contain the address of the MQTT broker.
        :param pilot: The prefix of the MQTT topic used to publish information.
        """

        # 1 Storing the OGC configuration
        self._ogc_config = ogc_config

        # 2 Load local resource catalog
        self._catalog_fullpath = CATALOG_FOLDER + catalog_name
        if os.path.exists(self._catalog_fullpath):
            self._resource_catalog = util.load_from_file(self._catalog_fullpath)
            self.print_catalog()
        else:
            logging.info("No resource catalog <" + catalog_name + "> available.")
            self._resource_catalog = {}

        # 3 Load connection configuration file
        if connection_file:
            connection_config_file = util.load_from_file(connection_file)
            self._pub_broker_address = connection_config_file["mqtt"]["pub_broker"]
            self._pub_broker_port = connection_config_file["mqtt"]["pub_broker_port"]
            try:
                self._pub_broker_keepalive = connection_config_file["mqtt"]["pub_broker_keepalive"]
            except KeyError:
                logging.warning(
                    "No broker keepalive specified, will be used the default one: " + str(DEFAULT_KEEPALIVE) + " s")
                self._pub_broker_keepalive = DEFAULT_KEEPALIVE
        else:
            try:
                self._pub_broker_address = os.environ[D_PUB_BROKER_URI_KEY]
            except KeyError:
                logging.error("Missing environment variable: "+D_PUB_BROKER_URI_KEY)
                exit(ERROR_MISSING_ENV_VARIABLE)
            try:
                self._pub_broker_port = int(os.environ[D_PUB_BROKER_PORT_KEY])
            except KeyError:
                logging.warning("No broker port specified, will be used the default one: "+str(DEFAULT_KEEPALIVE)+" s")
                self._pub_broker_port = BROKER_DEFAULT_PORT
            try:
                self._pub_broker_keepalive = int(os.environ[D_PUB_BROKER_KEEPALIVE_KEY])
            except KeyError:
                logging.warning(
                    "No broker keepalive specified, will be used the default one: " + str(DEFAULT_KEEPALIVE) + " s")
                self._pub_broker_keepalive = DEFAULT_KEEPALIVE

        # 4 Creating an MQTT Publisher
        if pilot == D_CUSTOM_MODE:
            try:
                pilot_mqtt_topic_prefix = os.environ[D_GOST_MQTT_PREFIX_KEY]
            except KeyError:
                logging.warning('No MQTT topic prefix configured, default one will be used: "'+DEFAULT_GOST_PREFIX+'"')
                pilot_mqtt_topic_prefix = DEFAULT_GOST_PREFIX
        else:
            # Retrieving pilot name --- 'local' is the default configuration value
            pilot_mqtt_topic_prefix = mqtt_util.get_publish_mqtt_topic(pilot)
            if not pilot_mqtt_topic_prefix:
                logging.critical('Wrong pilot name: "' + pilot + '"!')
                exit(ERROR_WRONG_PILOT_NAME)

        logging.debug("MQTT publishing topic prefix: " + pilot_mqtt_topic_prefix)
        self._topic_prefix = pilot_mqtt_topic_prefix

        if catalog_name != CATALOG_FILENAME:
            client_id = MQTT_CLIENT_PREFIX + "-" + str(self.__class__.__name__)  # catalog_name).replace(".json", "")
        else:
            client_id = MQTT_CLIENT_PREFIX
        client_id = client_id + "-" + str(random.randint(1, sys.maxsize))
        self._mqtt_publisher = mqtt.Client(client_id=client_id)

        self._mqtt_publisher.on_connect = mqtt_util.on_connect
        self._mqtt_publisher.on_disconnect = mqtt_util.automatic_reconnection

        logging.info(
            "Try to connect to broker: %s:%s for PUBLISHING..." % (self._pub_broker_address, self._pub_broker_port))
        logging.debug("MQTT Client ID is: " + str(self._mqtt_publisher._client_id))
        self._mqtt_publisher.connect(self._pub_broker_address, self._pub_broker_port, self._pub_broker_keepalive)
        self._mqtt_publisher.loop_start()

        # 5 Preparing module analysis information
        self._active_devices = {ACTUAL_COUNTER_KEY: 0, LAST_UPDATE_KEY: arrow.utcnow()}
        update_interval = None
        warning_msg = " not configured, default value will be used: " + str(DEFAULT_UPDATE_INTERVAL) + "s"
        if pilot is D_CUSTOM_MODE:
            try:
                update_interval = int(os.environ[UPDATE_INTERVAL_KEY.upper()])
            except KeyError:
                warning_msg = UPDATE_INTERVAL_KEY.upper() + warning_msg
        elif connection_file:
            try:
                update_interval = int(connection_config_file[UPDATE_INTERVAL_KEY])
            except KeyError:
                warning_msg = UPDATE_INTERVAL_KEY + warning_msg
        else:
            warning_msg = "Error: " + UPDATE_INTERVAL_KEY + warning_msg
            update_interval = DEFAULT_UPDATE_INTERVAL

        if not update_interval:
            logging.warning(warning_msg)
            self._active_devices[UPDATE_INTERVAL_KEY] = DEFAULT_UPDATE_INTERVAL
        else:
            self._active_devices[UPDATE_INTERVAL_KEY] = update_interval

        logging.info("If observations flow, number of active devices will be refreshed every "
                     + str(self._active_devices[UPDATE_INTERVAL_KEY]) + " seconds.")

    def get_mqtt_connection_address(self) -> str:
        return self._pub_broker_address

    def get_mqtt_connection_port(self) -> int:
        return self._pub_broker_port

    def get_ogc_config(self) -> OGCConfiguration:
        return self._ogc_config

    def get_topic_prefix(self) -> str:
        return self._topic_prefix

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
        tmp_rc[REGISTERED_DEVICES_KEY] = len(tmp_rc)
        # tmp_rc["active_devices"] = active_devices_count

        tmp_active_devices = copy.deepcopy(self._active_devices)
        try:
            tmp_active_devices[LAST_UPDATE_KEY] = str(tmp_active_devices[LAST_UPDATE_KEY])
        except KeyError:
            logging.error('"'+LAST_UPDATE_KEY+'" data structure is not available!')
        # x = json.dumps(tmp_active_devices, indent=2, sort_keys=True)
        tmp_rc[ACTIVE_DEVICES_KEY] = tmp_active_devices

        return tmp_rc

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
            time_diff = (current_time - self._active_devices[LAST_UPDATE_KEY]).total_seconds()
            if time_diff < self._active_devices[UPDATE_INTERVAL_KEY]:
                self._active_devices[ACTUAL_COUNTER_KEY] += 1
            else:
                self._active_devices[COUNTER_KEY] = self._active_devices[ACTUAL_COUNTER_KEY]
                self._active_devices[ACTUAL_COUNTER_KEY] = 1
                self._active_devices[LAST_UPDATE_KEY] = current_time
        except KeyError as ke:
            logging.error("Trying to update active_devices structure... But a field is missing!")
            logging.error(repr(ke))

    def delete_device(self, device_id: str, remove_only_from_catalog: bool = False) -> (bool, bool):
        if device_id not in self._resource_catalog:
            logging.error("There is no device: " + device_id)
            return False, True

        deleted = False

        if not remove_only_from_catalog:
            device_catalog = self._resource_catalog[device_id]
            for datastream, ds_id in device_catalog.items():
                ds_removed = self._ogc_config.delete_datastream(ds_id)
                if ds_removed:
                    logging.debug('From device "' + device_id + '" DATASTREAM "' + datastream + '" removed')
                else:
                    logging.error('Impossible to remove DATASTREAM "'+datastream+'" from device "'+device_id+'"')

        logging.info('From SCRAL resource_catalog removing element: "'+str(device_id)+'"\n'
                     'Content: "'+str(self._resource_catalog[device_id])+'"')
        del(self._resource_catalog[device_id])
        deleted = True

        if not remove_only_from_catalog:
            self.update_file_catalog()

        return deleted, False

    def mqtt_publish(self, topic: str, payload, qos: int = DEFAULT_MQTT_QOS, to_print: bool = True) -> bool:
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

    @abstractmethod
    def runtime(self):
        """ This is an abstract method that has to be overwritten.
            It manages the runtime operation of the module.
        """
        raise NotImplementedError("Implement runtime method in subclasses")

# def ogc_datastream_registration(self, ogc_devices_server_url: str, certificate_path: Optional[str] = None):
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
