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
from typing import Union

import arrow

from scral_ogc import OGCObservation
from scral_ogc.ogc_datastream import OGCDatastream

from scral_core import util
from scral_core.constants import CATALOG_FILENAME
from scral_core.ogc_configuration import OGCConfiguration
from scral_core.rest_module import SCRALRestModule

from template_rest.constants import DEVICE_ID_KEY


class SCRALTemplate(SCRALRestModule):

    def __init__(self, ogc_config: OGCConfiguration, config_filename: str, catalog_name: str = CATALOG_FILENAME):
        super().__init__(ogc_config, config_filename, catalog_name)

    def ogc_datastream_registration(self, device_id: str) -> bool:
        if self._ogc_config is None:
            return False

        # Collect OGC information needed to build DATASTREAMs payload
        thing = self._ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        # Assumption: only 1 sensor considered in this basic implementation
        sensor = self._ogc_config.get_sensors()[0]  # the first (and only) sensor
        sensor_id = sensor.get_id()
        sensor_name = sensor.get_name()

        rc = self._resource_catalog

        rc[device_id] = {}
        for op in self._ogc_config.get_observed_properties():
            property_id = op.get_id()
            property_name = op.get_name()
            property_description = op.get_description()

            datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + device_id
            uom = util.build_ogc_unit_of_measure(property_name.lower())

            datastream = OGCDatastream(name=datastream_name, description="Datastream for " + property_description,
                                       ogc_property_id=property_id, ogc_sensor_id=sensor_id, ogc_thing_id=thing_id,
                                       x=0.0, y=0.0, unit_of_measurement=uom)
            datastream_id = self._ogc_config.entity_discovery(
                datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)

            if not datastream_id:
                return False

            datastream.set_id(datastream_id)
            self._ogc_config.add_datastream(datastream)
            rc[device_id][property_name] = datastream_id

        self.update_file_catalog()
        return True

    def ogc_observation_registration(self, obs_property: str, payload: dict) -> Union[None, bool]:
        device_id = payload[DEVICE_ID_KEY]
        if device_id not in self._resource_catalog:
            return None

        phenomenon_time = payload.pop("timestamp")  # Retrieving and removing the phenomenon time
        observation_time = str(arrow.utcnow())
        observation_result = payload

        logging.debug(
            "Device: '"+device_id+"', Property: '"+obs_property+"', Observation:\n"+json.dumps(observation_result)+".")

        datastream_id = self._resource_catalog[device_id][obs_property]
        topic = self._topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # Create OGC Observation and publish
        ogc_observation = OGCObservation(datastream_id, phenomenon_time, observation_result, observation_time)
        observation_payload = json.dumps(ogc_observation.get_rest_payload())

        mqtt_response = self.mqtt_publish(topic, observation_payload)
        self._update_active_devices_counter()
        return mqtt_response
