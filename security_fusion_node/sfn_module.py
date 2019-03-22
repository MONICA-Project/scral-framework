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

import arrow

from scral_ogc import OGCObservation
from scral_ogc.ogc_datastream import OGCDatastream
from scral_module import util
from scral_module.rest_module import SCRALRestModule


class SCRALSecurityFusionNode(SCRALRestModule):

    def ogc_datastream_registration(self, resource_id, sensor_type, payload):
        if self._ogc_config is None:
            return False

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

        rc = self._resource_catalog

        rc[resource_id] = {}
        for op in self._ogc_config.get_observed_properties():

            property_id = op.get_id()
            property_name = op.get_name()
            property_description = op.get_description()

            if sensor_type == 'Camera' and property_name != "CDG-Estimation":
                coordinates = payload['camera_position']
                datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + resource_id
                uom = util.build_ogc_unit_of_measure(property_name.lower())

                datastream = OGCDatastream(name=datastream_name, description="Datastream for " + property_description,
                                           ogc_property_id=property_id, ogc_sensor_id=sensor_id, ogc_thing_id=thing_id,
                                           x=coordinates[0], y=coordinates[1], unit_of_measurement=payload)
                datastream_id = self._ogc_config.entity_discovery(
                    datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)

                datastream.set_id(datastream_id)
                self._ogc_config.add_datastream(datastream)

                rc[resource_id][property_name] = datastream_id

            elif sensor_type == 'Crowd-Density-Global' and property_name == "CDG-Estimation":
                datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + resource_id
                uom = util.build_ogc_unit_of_measure(property_name.lower())

                datastream = OGCDatastream(name=datastream_name, description="Datastream for " + property_description,
                                           ogc_property_id=property_id, ogc_sensor_id=sensor_id, ogc_thing_id=thing_id,
                                           x=0.0, y=0.0, unit_of_measurement=payload)
                datastream_id = self._ogc_config.entity_discovery(
                    datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)

                datastream.set_id(datastream_id)
                self._ogc_config.add_datastream(datastream)

                rc[resource_id][property_name] = datastream_id
            # else:
            #     continue

        return True

    def ogc_observation_registration(self, obs_property, payload, resource_id):
        if resource_id not in self._resource_catalog:
            return None

        phenomenon_time = payload.pop("timestamp")  # Retrieving and removing the phenomenon time
        observation_time = str(arrow.utcnow())
        observation_result = payload

        logging.debug(
            "Device: '" + resource_id + "', Property: '" + obs_property + "', Observation:\n" + json.dumps(
                observation_result) + ".")

        topic_prefix = self._topic_prefix
        datastream_id = self._resource_catalog[resource_id][obs_property]
        topic = topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # Create OGC Observation and publish
        ogc_observation = OGCObservation(datastream_id, phenomenon_time, observation_result, observation_time)
        observation_payload = json.dumps(ogc_observation.get_rest_payload())

        return self.mqtt_publish(topic, observation_payload)
