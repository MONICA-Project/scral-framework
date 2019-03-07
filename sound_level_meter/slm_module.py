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

import requests
import json
import logging
import scral_module.util as util

from flask import Flask
from scral_module.scral_module import SCRALModule
from sound_level_meter.constants import URL_SLM_LOGIN, CREDENTIALS
from scral_module.constants import REST_HEADERS
from sound_level_meter.constants import URL_SLM_CLOUD, TENANT_ID, SITE_ID
from scral_ogc import OGCDatastream

app = Flask(__name__)

_slm_module = None


class SCRALSoundLevelMeter(SCRALModule):
    """ Resource manager for integration of the SLM-GW (by usage of B&K's IoT Sound Level Meters). """

    def __init__(self, ogc_config, connection_file, pub_topic_prefix):
        """ Load OGC configuration model and initialize MQTT Broker for publishing Observations

        :param connection_file: A file containing connection information.
        :param pub_topic_prefix: The MQTT topic prefix on which information will be published.
        """
        super().__init__(ogc_config, connection_file, pub_topic_prefix)

        # Creating endpoint for listening to "sound event detection" REST requests
        connection_config_file = util.load_from_file(connection_file)
        self._listening_address = connection_config_file["REST"]["listening_address"]["address"]
        self._listening_port = int(connection_config_file["REST"]["listening_address"]["port"])

        # Get cloud access token by using available credentials
        self._cloud_token = self.get_credentials(URL_SLM_LOGIN, CREDENTIALS, REST_HEADERS)

        global _slm_module
        _slm_module = self

    # noinspection PyMethodOverriding
    def runtime(self):
        """
        This method discovers active SLMs from B&K cloud, registers them as OGC Datastreams into the MONICA
        server and finally retrieves sound measurements for each device by using parallel querying threads.

        Furthermore, this method deploys an REST endpoint as Flask application based on CherryPy WSGI web server.
        The endpoint will listen for incoming REST requests of the type "sound event detection",
        and will generate corresponding Observations.
        """
        # ### Start SLM discovery from B&K cloud
        self.ogc_datastream_registration(URL_SLM_CLOUD, TENANT_ID, SITE_ID)

    def ogc_datastream_registration(self, url, tenant_id, site_id):
        """
        This method discovers active SLMs for a given site_id and registers a new OGC Datastream for
        each couple SLM-ObservedProperty.
        :param url: B&K server address
        :param tenant_id: B&K server tenant_id
        :param site_id: B&K server site_id (pilot specific)
        """

        url_locations = url + "/tenants/" + str(tenant_id) + "/sites/" + str(site_id) + "/locations"

        # Get the list of active locations registered to the site_id
        r = None
        try:
            r = requests.get(url_locations, headers=self._cloud_token)
        except Exception as ex:
            logging.error(ex)
        if r is None:
            raise ConnectionError(
                "Connection status: " + str(r.status_code) + "\nImpossible to establish a connection"
                + "with " + url)
        else:
            locations_list = r.json()['value']
            logging.debug("Active locations list: " + str(locations_list))
        locations_id_list = []

        # Get location ids from active locations
        for location in locations_list:
            locations_id_list.append(location["locationId"])

        # Discover active devices from active location ids (assumption: 1 SLM x 1 location_id)
        active_devices = {}
        for location_id in locations_id_list:
            logging.info("Start discovery for active SLMs in a given site (pilot)")
            url_location = url_locations + "/" + str(location_id)
            try:
                r = requests.get(url_location, headers=self._cloud_token)
            except Exception as ex:
                logging.error(ex)

            # Get device id, name, description and coordinates assigned to location item
            location_item = r.json()
            location_assigned_device_id = location_item["assignedDevices"][0]["deviceId"]
            location_assigned_device_name = location_item["assignedDevices"][0]["name"]
            location_assigned_device_description = location_item["assignedDevices"][0]["description"]
            location_coordinates = location_item["geoLocation"]
            logging.debug("SLM id: "+str(location_assigned_device_id)+" / SLM name: "+location_assigned_device_name)

            # Build active devices catalog
            active_devices[location_assigned_device_id] = {}
            active_devices[location_assigned_device_id]["coordinates"] = location_coordinates["coordinates"]
            active_devices[location_assigned_device_id]["name"] = location_assigned_device_name
            active_devices[location_assigned_device_id]["description"] = location_assigned_device_description

        logging.debug("ACTIVE SLMs catalog: " + str(active_devices))

        # Collect OGC information needed to build Datastreams payload
        thing = self._ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor = self._ogc_config.get_sensors()[0]  # Assumption: only "SLM" Sensor is defined for this adapter
        sensor_id = sensor.get_id()
        sensor_name = sensor.get_name()

        properties_list = self._ogc_config.get_observed_properties()  # There are more than one properties to parse

        # Start OGC Datastreams registration
        logging.debug("Start OGC DATASTREAMs registration")
        for device_id, values in active_devices.items():
            logging.debug("Device id: "+str(device_id))
            logging.debug("Device values: "+str(values))
            device_name = values["name"]
            device_coordinates = values["coordinates"]
            device_description = values["description"]

            # Check whether device has been already registered
            if device_name in self._resource_catalog:
                logging.debug("Device: "+device_id+" already registered with id: "+device_id+" and name: "+device_name)
            else:
                self._resource_catalog[device_name] = {}

                # Iterate over SLM assigned ObservedProperties
                for ogc_property in properties_list:
                    property_id = ogc_property.get_id()
                    property_name = ogc_property.get_name()
                    property_definition = {"definition": ogc_property.get_definition()}
                    logging.debug("Device property: " + str(property_name))
                    datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + device_name
                    description = device_description
                    datastream = OGCDatastream(name=datastream_name, description=description,
                                               ogc_property_id=property_id, ogc_sensor_id=sensor_id,
                                               ogc_thing_id=thing_id, x=device_coordinates[0], y=device_coordinates[1],
                                               unit_of_measurement=property_definition)
                    datastream_id = self._ogc_config.entity_discovery(
                                        datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)

                    datastream.set_id(datastream_id)
                    self._ogc_config.add_datastream(datastream)

                    # Store device/property information in local resource catalog
                    self._resource_catalog[device_name][property_name] = datastream_id

    @staticmethod
    def get_credentials(url, credentials, headers):
        """ This function get authorized token from SLM server
        :param: url: B&K server address
        :param: credentials: available access credentials
        ·param: headers: REST query headers
        :return: a dictionary with limited-time-available access credentials
        """

        auth = None
        try:
            auth = requests.post(url=url, data=json.dumps(credentials), headers=headers)
        except Exception as ex:
            logging.error(ex)

        if auth:
            # enable authorization
            cloud_token = dict()
            cloud_token["Accept"] = "application/json"
            access_token = auth.json()['accessToken']
            cloud_token['Authorization'] = "Bearer " + str(access_token)
        else:
            raise ValueError("Credentials " + credentials + " have been denied by the SLM server")

        logging.info("B&K access token successfully authorized!")
        return cloud_token
