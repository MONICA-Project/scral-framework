#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#############################################################################
#      _____ __________  ___    __                                          #
#     / ___// ____/ __ \/   |  / /                                          #
#     \__ \/ /   / /_/ / /| | / /                                           #
#    ___/ / /___/ _, _/ ___ |/ /___                                         #
#   /____/\____/_/ |_/_/  |_/_____/   Smart City Resource Adaptation Layer  #
#                                                                           #
# LINKS Foundation, (c) 2017-2020                                           #
# developed by Jacopo Foglietti & Luca Mannella                             #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md     #
#                                                                           #
#############################################################################
import json
import logging
import time
from typing import List, Dict, Union

import requests

from scral_ogc import OGCThing, OGCLocation, OGCSensor, OGCObservedProperty, OGCDatastream
from scral_core import util
from scral_core.constants import REST_HEADERS, OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD, OGC_ID_KEY


class OGCConfiguration:
    """ This class is a representation of an OGC SensorThings model. """

    def __init__(self, ogc_file_name: str, ogc_server_address: str):
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
        self._ogc_location = OGCLocation(name, description, float(x), float(y))
        time.sleep(2)

        # THING
        name = parser['THING']['NAME']  # only one THING for each configuration file
        description = parser['THING']['DESCRIPTION']
        props_type = {"type": parser['THING']['PROPERTY_TYPE']}
        self._ogc_thing = OGCThing(name, description, props_type)

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

            self._sensors.append(OGCSensor(sensor_name, sensor_description, sensor_metadata, sensor_encoding))

        i = 0  # OBSERVED PROPERTIES
        self._observed_properties = []
        while i < num_properties:
            section = "PROPERTY_" + str(i)
            i += 1
            property_name = parser[section]['NAME']
            property_description = parser[section]['DESCRIPTION']
            property_definition = parser[section]['PROPERTY_TYPE']

            self._observed_properties.append(
                OGCObservedProperty(property_name, property_description, property_definition))

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
                    OGCSensor(sensor_name, sensor_description, sensor_metadata, sensor_encoding))

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
                    OGCObservedProperty(property_name, property_description, property_definition))

        self._datastreams = {}
        self._virtual_datastreams = {}

    def discovery(self, verbose: bool = False):
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

                virtual_sensor_name = parser[section]['SENSOR']
                virtual_property_name = parser[section]['PROPERTY']

                v_datastream_name = parser[section]['THING'] + "/" + virtual_sensor_name + "/" + virtual_property_name
                v_datastream_description = parser[section]['DESCRIPTION']
                v_ds_coord_x = float(parser[section]['COORDINATES_X'])
                v_ds_coord_y = float(parser[section]['COORDINATES_Y'])

                v_ds_unit_of_measure = util.build_ogc_unit_of_measure(parser[section]['UNIT_MEASURE'])

                virtual_sensor_id = None
                for s in self._virtual_sensors:
                    if s.get_name() == virtual_sensor_name:
                        virtual_sensor_id = s.get_id()
                        break
                if not virtual_sensor_id:
                    raise ValueError("Sensor ID not defined for VIRTUAL PROPERTY: " + virtual_property_name)

                virtual_property_id = None
                for op in self._virtual_properties:
                    if op.get_name() == virtual_property_name:
                        virtual_property_id = op.get_id()
                        break
                if not virtual_property_id:
                    raise ValueError("Property ID not defined for VIRTUAL PROPERTY: "+virtual_property_name)

                virtual_datastream = OGCDatastream(v_datastream_name, v_datastream_description,
                                                   virtual_property_id, virtual_sensor_id, thing_id,
                                                   v_ds_unit_of_measure, v_ds_coord_x, v_ds_coord_y)
                vds_id = self.entity_discovery(virtual_datastream, self.URL_DATASTREAMS, self.FILTER_NAME, verbose)
                logging.info('Virtual DATASTREAM: "' + v_datastream_name + '" with id: ' + str(vds_id))
                virtual_datastream.set_id(vds_id)
                self._virtual_datastreams[vds_id] = virtual_datastream

        logging.info("--- End of OGC discovery ---\n")

    @staticmethod
    def entity_registration(ogc_entity, url_entity: str):
        """ This method register an OGC entity on the OGC server.

        :param ogc_entity: An object from scral_ogc package containing the data of the OGC entity.
        :param url_entity: The URL of the request.
        :return: Returns the @iot.id of the entity if it is correctly registered,
                 if something goes wrong during registration, an exception will be thrown.
        """
        payload = ogc_entity.get_rest_payload()
        r = requests.post(url=url_entity, data=json.dumps(payload),
                          headers=REST_HEADERS, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
        json_string = r.json()
        if OGC_ID_KEY not in json_string:
            raise ValueError("The Entity ID is not defined for: '" + ogc_entity.get_name() + "'\n" +
                             "Please check the REST request!")
        else:
            return json_string[OGC_ID_KEY]

    @staticmethod
    def entity_discovery(ogc_entity, url_entity: str, url_filter: str, verbose: bool = False) -> int:
        """ This method retrieves the @iot.id associated to an OGC resource automatically assigned by the server.
            If the entity was not already registered, it will be uploaded on the OGC Server and the @iot.id is returned.

        :param ogc_entity: An object from scral_ogc package containing the data of the OGC entity.
        :param url_entity: The URL of the request.
        :param url_filter: The filter to apply.
        :param verbose: Set it to true to have more logging prints.
        :return: Returns the @iot.id of the entity if it is correctly registered,
                 if something goes wrong during registration, an exception will be thrown.
        """
        ogc_entity_name = ogc_entity.get_name()
        url_discovery = url_entity + url_filter + "'" + ogc_entity_name + "'"

        r = requests.get(url=url_discovery, headers=REST_HEADERS, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
        discovery_result = r.json()['value']

        if not discovery_result or len(discovery_result) == 0:  # if response is empty
            # This is a new OGC Entity.
            logging.info(ogc_entity_name + " not yet registered, registration is starting now!")
            ogc_id = OGCConfiguration.entity_registration(ogc_entity, url_entity)
            return ogc_id
        else:
            if len(discovery_result) > 1:
                # Something wrong in our model: no duplicate entity!
                logging.critical("Verify OGC-naming! Duplicate found for entity: <"+ogc_entity_name+">.")
                logging.debug("Current Filter: '" + url_filter + "'")
                if verbose:
                    for res in discovery_result:
                        logging.debug(str(res))
                raise ValueError("Multiple results for same Entity name: " + ogc_entity_name + "!")

            else:
                # OGC entity already exists, returning its OGC id.
                return discovery_result[0][OGC_ID_KEY]

    @staticmethod
    def entity_override(ogc_entity, url_entity: str, url_filter: str = "") -> int:
        """ This method register or overrides an OGC resource in the OGC server and returns its @iot.id.

        :param ogc_entity: An object from scral_ogc package containing the data of the OGC entity.
        :param url_entity: The URL of the request.
        :param url_filter: The filter to apply.
        :return: Returns the @iot.id of the entity if it is correctly registered,
                 if something goes wrong during registration, an exception will be thrown.
        """
        ogc_entity_name = ogc_entity.get_name()
        url_discovery = url_entity + url_filter + "'" + ogc_entity_name + "'"

        r = requests.get(url=url_discovery, headers=REST_HEADERS, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
        discovery_result = r.json()['value']

        if not discovery_result or len(discovery_result) == 0:  # if response is empty
            # This is a new OGC Entity.
            logging.info(ogc_entity_name + " not yet registered, registration is starting now!")
            ogc_id = OGCConfiguration.entity_registration(ogc_entity, url_entity)
            return ogc_id

        elif len(discovery_result) > 1:
            # Something wrong in our model: no duplicate entity!
            logging.critical("Verify OGC-naming! Duplicate found for entity: <" + ogc_entity_name + ">.")
            logging.debug("Current Filter: '" + url_filter + "'")

            for res in discovery_result:
                logging.debug(str(res))
            raise ValueError("Multiple results for same Entity name: " + ogc_entity_name + "!")

        else:
            # Patching the previous entity with new data.
            ogc_id = discovery_result[0][OGC_ID_KEY]
            ogc_entity.set_id(ogc_id)
            payload = ogc_entity.get_rest_payload()
            url_patch = url_entity + "(" + str(ogc_id) + ")"
            r = requests.patch(url=url_patch, data=json.dumps(payload),
                               headers=REST_HEADERS, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
            json_string = r.json()
            if OGC_ID_KEY not in json_string:
                raise ValueError("The Entity ID is not defined for: '" + ogc_entity.get_name() + "'\n" +
                                 "Please check the REST request!")
            elif json_string[OGC_ID_KEY] != ogc_id:
                raise ValueError('A new entity is created for: "' + ogc_entity.get_name() + '"')
            else:
                return json_string[OGC_ID_KEY]

    def delete_datastream(self, datastream_id: int) -> bool:
        url = self.URL_DATASTREAMS + "("+str(datastream_id)+")"

        r = requests.delete(url=url, headers=REST_HEADERS, auth=(OGC_SERVER_USERNAME, OGC_SERVER_PASSWORD))
        if r.ok:
            logging.info("DATASTREAM: " + str(datastream_id) + " correctly deleted!")
            return True
        else:
            logging.error("Impossible to delete DATASTREAM: " + str(datastream_id) + ". Maybe it did not exist!")
            return False

    def get_thing(self) -> OGCThing:
        return self._ogc_thing

    def get_location(self) -> OGCLocation:
        return self._ogc_location

    def get_sensors(self) -> List[OGCSensor]:
        return self._sensors

    def get_observed_properties(self) -> List[OGCObservedProperty]:
        return self._observed_properties

    def get_sensors_number(self) -> int:
        return len(self._sensors)

    def get_properties_number(self) -> int:
        return len(self._observed_properties)

    def get_virtual_datastream(self, name: str) -> Union[OGCDatastream, bool]:
        for vds_key, vds_value in self._virtual_datastreams.items():
            if vds_value.get_name() == name:
                return vds_value

        return False

    def get_datastreams(self) -> Dict[int, OGCDatastream]:
        return self._datastreams

    def get_datastream(self, datastream_id) -> OGCDatastream:
        return self._datastreams[datastream_id]

    def add_observed_property(self, ogc_obs_property):
        """ This method adds a new observed property inside the OGCConfiguration.
            If something wrong during the entity discovery of this new property a ValueError exception is raised.

        :param ogc_obs_property: The observed property that you want to add. It must have an ID.
        :return: The observed property with the GOST id.
        """
        obs_id = self.entity_discovery(ogc_obs_property, self.URL_PROPERTIES, self.FILTER_NAME)
        if not obs_id:
            raise ValueError("The OBSERVED PROPERTY does not have an ID")

        ogc_obs_property.set_id(obs_id)

        if ogc_obs_property not in self._observed_properties:
            self._observed_properties.append(ogc_obs_property)

        return ogc_obs_property

    def add_datastream(self, datastream):
        """ This method adds a new datastream inside the OGCConfiguration.
            If the datastream does not have an ID, a ValueError exception is raised.

        :param datastream: The datastream that you want to add. It must have an ID.
        """
        datastream_id = datastream.get_id()
        if not datastream_id:
            raise ValueError("The DATASTREAM does not have an ID")
        else:
            self._datastreams[datastream_id] = datastream
