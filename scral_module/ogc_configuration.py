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

import requests

import scral_ogc
from scral_module import util
from scral_module.constants import REST_HEADERS, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, OGC_ID_KEY


class OGCConfiguration:
    """ This class is a representation of an OGC SensorThings model. """

    def __init__(self, ogc_file_name, ogc_server_address):
        """ This function reads an OGC Model file and creates a Python object representation of it.
            Furthermore, it prepares all the appropriate REST URL to contact the OGC server.

        :param ogc_file_name: The path of the file containing the OGC Sensor Things model.
        :param ogc_server_address: The address of the OGC server to contact during discovery and integration phase.
        """
        # OGC server urls according to the given ogc server address
        self.URL_RESOURCES = ogc_server_address                           # All resources
        self.URL_THINGS = ogc_server_address + "/Things"                  # All things
        self.URL_LOCATIONS = ogc_server_address + "/Locations"            # All Locations
        self.URL_SENSORS = ogc_server_address + "/Sensors"                # All Sensors
        self.URL_PROPERTIES = ogc_server_address + "/ObservedProperties"  # All Observed Properties
        self.URL_DATASTREAMS = ogc_server_address + "/Datastreams"        # All DataStreams
        # Filter example: /ObservedProperties?$filter=name eq 'Area Temperature'
        self.FILTER_NAME = "?$filter=name eq "

        self._ogc_file_name = ogc_file_name
        parser = util.init_parser(self._ogc_file_name)

        # LOCATION
        name = parser['LOCATION']['NAME']  # only one LOCATION for each configuration file
        description = parser['LOCATION']['DESCRIPTION']
        x = parser['LOCATION']['COORDINATES_X']
        y = parser['LOCATION']['COORDINATES_Y']
        self._ogc_location = scral_ogc.OGCLocation(name, description, float(x), float(y))

        # THING
        name = parser['THING']['NAME']  # only one THING for each configuration file
        description = parser['THING']['DESCRIPTION']
        props_type = {"type": parser['THING']['PROPERTY_TYPE']}
        self._ogc_thing = scral_ogc.OGCThing(name, description, props_type)

        # COUNTABLE
        num_sensors = int(parser['THING']['NUM_OF_SENSORS'])
        num_properties = int(parser['THING']['NUM_OF_PROPERTIES'])
        num_v_sensors = int(parser['THING']['NUM_OF_V_SENSORS'])
        num_v_properties = int(parser['THING']['NUM_OF_V_PROPERTIES'])
        self._num_v_datastreams = int(parser['THING']['NUM_OF_V_DATASTREAMS'])

        i = 0  # SENSORS
        self._sensors = []
        while i < num_sensors:
            section = "SENSOR_" + str(i)
            i += 1
            sensor_name = parser[section]['NAME']
            sensor_description = parser[section]['DESCRIPTION']
            sensor_encoding = parser[section]['ENCODING']
            sensor_metadata = parser[section]['METADATA']

            self._sensors.append(scral_ogc.OGCSensor(sensor_name, sensor_description, sensor_metadata, sensor_encoding))

        i = 0  # OBSERVED PROPERTIES
        self._observed_properties = []
        while i < num_properties:
            section = "PROPERTY_" + str(i)
            i += 1
            property_name = parser[section]['NAME']
            property_description = parser[section]['DESCRIPTION']
            property_definition = parser[section]['PROPERTY_TYPE']

            self._observed_properties.append(
                scral_ogc.OGCObservedProperty(property_name, property_description, property_definition))

        self._virtual_sensors = []    # Virtual SENSORS
        if num_v_sensors > 0:
            i = 0
            while i < num_v_sensors:
                section = "V_SENSOR_" + str(i)
                i += 1
                sensor_name = parser[section]['NAME']
                sensor_description = parser[section]['DESCRIPTION']
                sensor_encoding = parser[section]['ENCODING']
                sensor_metadata = parser[section]['METADATA']

                self._virtual_sensors.append(
                    scral_ogc.OGCSensor(sensor_name, sensor_description, sensor_metadata, sensor_encoding))

        self._virtual_properties = []  # Virtual SENSORS
        if num_v_properties > 0:
            i = 0  # Virtual PROPERTIES
            while i < num_v_properties:
                section = "V_PROPERTY_" + str(i)
                i += 1
                property_name = parser[section]['NAME']
                property_description = parser[section]['DESCRIPTION']
                property_definition = parser[section]['PROPERTY_TYPE']

                self._virtual_properties.append(
                    scral_ogc.OGCObservedProperty(property_name, property_description, property_definition))

        self._datastreams = {}
        self._virtual_datastream = {}

    def discovery(self, verbose=False):
        """ This method uploads the OGC model on the OGC Server and retrieves the @iot.id assigned by the server.
            If entities were already registered, they are not overwritten (or registered twice)
            and only their @iot.id are retrieved.

        :return: It can throw an exception if something wrong.
        """
        logging.info("\n\n--- Starting OGC discovery ---\n")
        # LOCATION discovery
        location = self._ogc_location
        location_id = self.entity_discovery(location, self.URL_LOCATIONS, self.FILTER_NAME, verbose)
        logging.info('LOCATION: "' + location.get_name() + '" with id: ' + str(location_id))
        location.set_id(location_id)  # temporary useless

        # THING discovery
        thing = self._ogc_thing
        thing.set_location_id(location_id)
        thing_id = self.entity_discovery(thing, self.URL_THINGS, self.FILTER_NAME, verbose)
        logging.info('THING: "' + thing.get_name() + '" with id: ' + str(thing_id))
        thing.set_id(thing_id)

        # SENSORS discovery
        for s in self._sensors:
            sensor_id = self.entity_discovery(s, self.URL_SENSORS, self.FILTER_NAME, verbose)
            s.set_id(sensor_id)
            logging.info('SENSOR: "' + s.get_name() + '" with id: ' + str(sensor_id))

        # OBSERVED PROPERTIES discovery
        for op in self._observed_properties:
            op_id = self.entity_discovery(op, self.URL_PROPERTIES, self.FILTER_NAME, verbose)
            op.set_id(op_id)
            logging.info('OBSERVED PROPERTY: "' + op.get_name() + '" with id: ' + str(op_id))

        # Virtual SENSORS discovery
        for s in self._virtual_sensors:
            sensor_id = self.entity_discovery(s, self.URL_SENSORS, self.FILTER_NAME, verbose)
            s.set_id(sensor_id)
            logging.info('Virtual SENSOR: "' + s.get_name() + '" with id: ' + str(sensor_id))

        # Virtual PROPERTIES discovery
        for op in self._virtual_properties:
            op_id = self.entity_discovery(op, self.URL_PROPERTIES, self.FILTER_NAME, verbose)
            op.set_id(op_id)
            logging.info('Virtual PROPERTY: "' + op.get_name() + '" with id: ' + str(op_id))

        # VIRTUAL_DATASTREAM discovery
        if self._num_v_datastreams > 0:
            parser = util.init_parser(self._ogc_file_name)
            i = 0
            while i < self._num_v_datastreams:
                section = "V_DATASTREAM_" + str(i)
                i += 1

                sensor_name = parser[section]['SENSOR']
                property_name = parser[section]['PROPERTY']

                datastream_name = parser[section]['THING'] + "/" + sensor_name + "/" + property_name
                datastream_description = parser[section]['DESCRIPTION']
                ds_coord_x = float(parser[section]['COORDINATES_X'])
                ds_coord_y = float(parser[section]['COORDINATES_Y'])

                ds_unit_of_measure = util.build_ogc_unit_of_measure(parser[section]['UNIT_MEASURE'])

                ogc_sensor_id = None
                for s in self._sensors:
                    if s.get_name() == sensor_name:
                        ogc_sensor_id = s.get_id()
                        break

                ogc_property_id = None
                for op in self._observed_properties:
                    if op.get_name() == property_name:
                        ogc_property_id = op.get_id()

                virtual_datastream = scral_ogc.OGCDatastream(datastream_name, datastream_description,
                                                             ogc_property_id, ogc_sensor_id, thing_id,
                                                             ds_unit_of_measure, ds_coord_x, ds_coord_y)
                vds_id = self.entity_discovery(virtual_datastream, self.URL_DATASTREAMS, self.FILTER_NAME, verbose)
                logging.info('Virtual DATASTREAM: "' + datastream_name + '" with id: ' + str(vds_id))
                self._virtual_datastream[vds_id] = virtual_datastream

        logging.info("--- End of OGC discovery---\n")

    @staticmethod
    def entity_discovery(ogc_entity, url_entity, url_filter, verbose=False):
        """ This method uploads an OGC entity on the OGC Server and retrieves its @iot.id assigned by the server.
            If the entity is already registered, it is not overwritten (or registered twice)
            and only its @iot.id is retrieved.

        :param ogc_entity: An object containing the data of the entity.
        :param url_entity: The URL of the request.
        :param url_filter: The filter to apply.
        :param verbose: Set it to true to have more logging prints.
        :return: Returns the @iot.id of the entity if it is correctly registered,
                 if something goes wrong during registration, an exception can be generated.
        """
        # Build URL for LOCATION discovery based on Location name
        ogc_entity_name = ogc_entity.get_name()
        url_discovery = url_entity + url_filter + "'" + ogc_entity_name + "'"

        r = requests.get(url=url_discovery, headers=REST_HEADERS, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
        discovery_result = r.json()['value']

        if not discovery_result or len(discovery_result) == 0:  # if response is empty
            logging.info(ogc_entity_name + " not yet registered, registration is starting now!")
            payload = ogc_entity.get_rest_payload()
            r = requests.post(url=url_entity, data=json.dumps(payload),
                              headers=REST_HEADERS, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
            json_string = r.json()
            if OGC_ID_KEY not in json_string:
                raise ValueError("The Entity ID is not defined for: '" + ogc_entity_name + "'\n" +
                                 "Please check the REST request!")

            return json_string[OGC_ID_KEY]

        else:
            if len(discovery_result) > 1:
                logging.critical("Verify OGC-naming! Duplicate found for entity: <"+ogc_entity_name+">.")
                logging.debug("Current Filter: '" + url_filter + "'")
                if verbose:
                    for res in discovery_result:
                        logging.debug(str(res))
                raise ValueError("Multiple results for same Entity name: " + ogc_entity_name + "!")

            else:
                return discovery_result[0][OGC_ID_KEY]

    def get_thing(self):
        return self._ogc_thing

    def get_location(self):
        return self._ogc_location

    def get_sensors(self):
        return self._sensors

    def get_observed_properties(self):
        return self._observed_properties

    def get_sensors_number(self):
        return len(self._sensors)

    def get_properties_number(self):
        return len(self._observed_properties)

    def get_datastreams(self):
        return self._datastreams

    def get_datastream(self, datastream_id):
        return self._datastreams[datastream_id]

    def add_datastream(self, datastream):
        datastream_id = datastream.get_id()
        if datastream_id is None:
            raise ValueError("The DATASTREAM does not have an ID")
        else:
            self._datastreams[datastream_id] = datastream
