##############################################################################
#      _____ __________  ___    __                                           #
#     / ___// ____/ __ \/   |  / /                                           #
#     \__ \/ /   / /_/ / /| | / /                                            #
#    ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Abstraction Layer  #
#   /____/\____/_/ |_/_/  |_/_____/   v.2.0 - enhanced by Python 3           #
#                                                                            #
# LINKS Foundation, (c) 2019                                                 #
# developed by Jacopo Foglietti & Luca Mannella                              #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md      #
#                                                                            #
##############################################################################
import configparser
import scral_ogc


class OGCConfiguration:

    def __init__(self, ogc_file_name, ogc_server_address):
        # OGC server urls according to the given address
        self.URL_RESOURCES = ogc_server_address                           # All resources
        self.URL_THINGS = ogc_server_address + "/Things"                  # All things
        self.URL_LOCATIONS = ogc_server_address + "/Locations"            # All Locations
        self.URL_SENSORS = ogc_server_address + "/Sensors"                # All Sensors
        self.URL_PROPERTIES = ogc_server_address + "/ObservedProperties"  # All Observed Properties
        self.URL_DATASTREAMS = ogc_server_address + "/DataStreams"        # All DataStreams
        self.FILTER_NAME = "?$filter=name eq "
        # Filter example: /ObservedProperties?$filter=name eq 'Area Temperature'

        parser = configparser.ConfigParser()
        parser.read(ogc_file_name)
        parser.sections()

        # LOCATION
        name = parser['LOCATION']['NAME']  # only one LOCATION for each configuration file
        description = parser['LOCATION']['DESCRIPTION']
        x = parser['LOCATION']['COORDINATES_X']
        y = parser['LOCATION']['COORDINATES_Y']
        self.ogc_location = scral_ogc.OGCLocation(name, description, float(x), float(y))

        # THING
        name = parser['THING']['NAME']  # only one THING for each configuration file
        description = parser['THING']['DESCRIPTION']
        props_type = {"type": parser['THING']['PROPERTY_TYPE']}
        self.ogc_thing = scral_ogc.OGCThing(name, description, props_type)

        # COUNTABLE
        self.num_sensors = int(parser['THING']['NUM_OF_SENSORS'])
        self.num_properties = int(parser['THING']['NUM_OF_PROPERTIES'])

        i = 0  # SENSORS
        self.sensors = []
        while i < self.num_sensors:
            section = "SENSOR_" + str(i)
            i += 1
            sensor_name = parser[section]['NAME']
            sensor_description = parser[section]['DESCRIPTION']
            sensor_encoding = parser[section]['ENCODING']
            sensor_metadata = parser[section]['METADATA']

            self.sensors.append(scral_ogc.OGCSensor(sensor_name, sensor_description, sensor_metadata, sensor_encoding))

        i = 0  # OBSERVED PROPERTIES
        self.observed_properties = []
        while i < self.num_properties:
            section = "PROPERTY_" + str(i)
            i += 1
            property_name = parser[section]['NAME']
            property_description = parser[section]['DESCRIPTION']
            property_definition = parser[section]['PROPERTY_TYPE']

            self.observed_properties.append(
                scral_ogc.OGCObservedProperty(property_name, property_description, property_definition))

    def get_thing(self):
        return self.ogc_thing

    def get_location(self):
        return self.ogc_location

    def get_sensors(self):
        return self.sensors

    def get_observed_properties(self):
        return self.observed_properties

    def get_sensors_number(self):
        return self.num_sensors

    def get_properties_number(self):
        return self.num_properties
