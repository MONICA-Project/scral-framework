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
from flask import make_response, jsonify, Response

from scral_ogc import OGCObservation, OGCObservedProperty, OGCDatastream

from scral_core.constants import TIMESTAMP_KEY, OPT_COORD, \
    SUCCESS_RETURN_STRING, ERROR_RETURN_STRING, INTERNAL_SERVER_ERROR
from scral_core import util
from scral_core.rest_module import SCRALRestModule

from security_fusion_node.constants import CAMERA_SENSOR_TYPE, CAMERA_POSITION_KEY, CDG_SENSOR_TYPE, CDG_PROPERTY


class SCRALSecurityFusionNode(SCRALRestModule):
    """ Resource manager for integration of the Security Fusion Node. """

    def ogc_datastream_registration(self, resource_id: str, sensor_type: str, payload: dict) -> Response:
        """ This function registers new datastream in the OGC model.

        :param resource_id:
        :param sensor_type:
        :param payload:
        :return: An HTTP response.
        """
        if self._ogc_config is None:
            return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)

        self._resource_catalog[resource_id] = {}
        for op in self._ogc_config.get_observed_properties():
            property_name = op.get_name()
            if sensor_type == CAMERA_SENSOR_TYPE and property_name != CDG_PROPERTY:
                coordinates = payload[CAMERA_POSITION_KEY]
                ok = self._ogc_datastream_registration(resource_id, sensor_type, op, payload, coordinates)
                if not ok:
                    return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)

            elif sensor_type == CDG_SENSOR_TYPE and property_name == CDG_PROPERTY:
                ok = self._ogc_datastream_registration(resource_id, sensor_type, op, payload)
                if not ok:
                    return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)

        self.update_file_catalog()
        return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)

    def ogc_datastream_patch(self, resource_id: str, sensor_type: str, payload: dict) -> Response:
        """ This function update DATASTREAMs values stored in the OGC model (e.g. unitOfMeasurement value).

            CURRENTLY UNSUPPORTED: Impossible to execute a "deep patch" on GOST db.
        """
        raise NotImplementedError

    def _ogc_datastream_registration(self, resource_id: str, sensor_type: str, observed_property: OGCObservedProperty,
                                     payload: dict, coordinates: OPT_COORD = (0.0, 0.0), override=False) \
            -> Union[bool, int]:
        # Collect OGC information needed to build DATASTREAMs payload
        thing = self._ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor_id = None
        for sensor in self._ogc_config.get_sensors():
            sensor_name = sensor.get_name()
            if sensor_name == sensor_type:
                sensor_id = sensor.get_id()
                break

        if not sensor_id:
            logging.error("Wrong sensor type: " + sensor_type)
            return False

        property_id = observed_property.get_id()
        property_name = observed_property.get_name()
        property_description = observed_property.get_description()

        datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + resource_id
        uom = util.build_ogc_unit_of_measure(property_name.lower())  # ToDo: is it right that this field is not used?

        datastream = OGCDatastream(name=datastream_name, description="Datastream for " + property_description,
                                   ogc_property_id=property_id, ogc_sensor_id=sensor_id, ogc_thing_id=thing_id,
                                   x=coordinates[0], y=coordinates[1], unit_of_measurement=payload)
        if override:  # datastream already exists, it will be updated.
            """ Right now the usage of this functionality is discouraged. GOST does not support deep patch. """
            datastream_id = self._ogc_config.entity_override(
                datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)
        else:
            # new datastream
            datastream_id = self._ogc_config.entity_discovery(
                datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)

        if not datastream_id:
            return False
        else:
            datastream.set_id(datastream_id)
            self._ogc_config.add_datastream(datastream)
            self._resource_catalog[resource_id][property_name] = datastream_id

        return datastream_id

    def ogc_observation_registration(self, resource_id: str, obs_property: str, payload: dict) -> Union[None, bool]:
        if resource_id not in self._resource_catalog:
            return None

        phenomenon_time = payload.pop(TIMESTAMP_KEY, False)  # Retrieving and removing the phenomenon time
        if not phenomenon_time:
            phenomenon_time = payload.pop("timestamp_1", False)
            if not phenomenon_time:
                phenomenon_time = str(arrow.utcnow())
        observation_time = str(arrow.utcnow())

        logging.debug("Device: '"+resource_id+"', Property: '"+obs_property+"', Observation:\n"+json.dumps(payload)+".")

        datastream_id = self._resource_catalog[resource_id][obs_property]
        topic = self._topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # Create OGC Observation and publish
        ogc_observation = OGCObservation(datastream_id, phenomenon_time, payload, observation_time)
        observation_payload = json.dumps(ogc_observation.get_rest_payload())

        mqtt_response = self.mqtt_publish(topic, observation_payload)
        self._update_active_devices_counter()
        return mqtt_response
