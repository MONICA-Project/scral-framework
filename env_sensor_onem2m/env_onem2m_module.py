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
from flask import jsonify, make_response

from scral_module.rest_module import SCRALRestModule
import scral_module.util as util
from scral_ogc import OGCDatastream, OGCObservation


class SCRALEnvOneM2M(SCRALRestModule):
    """ Resource manager for integration of the Environmental Nodes (through OneM2M platform). """

    def ogc_datastream_registration(self, env_node_id):
        """ Given a Environmental Node ID, this method registers a new DATASTREAM in the OGC model.

        :param env_node_id: The Environmental node ID.
        :return: An HTTP response to be returned to the client.
        """
        ogc_config = self.get_ogc_config()
        if ogc_config is None:
            return make_response(jsonify({"Error": "Internal server error"}), 500)

        # Collect OGC information needed to build DATASTREAMs payload
        thing = ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor = ogc_config.get_sensors()[0]  # Assumption: only Environmental Node is defined for this adapter
        sensor_id = sensor.get_id()
        sensor_name = sensor.get_name()

        rc = self._resource_catalog
        rc[env_node_id] = {}
        for op in ogc_config.get_observed_properties():
            property_id = op.get_id()
            property_name = op.get_name()
            property_description = op.get_description()

            datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + env_node_id
            uom = util.build_ogc_unit_of_measure(property_name.lower())

            datastream = OGCDatastream(name=datastream_name, description="Datastream for " + property_description,
                                       ogc_property_id=property_id, ogc_sensor_id=sensor_id, ogc_thing_id=thing_id,
                                       x=0.0, y=0.0, unit_of_measurement=uom)
            datastream_id = ogc_config.entity_discovery(
                datastream, ogc_config.URL_DATASTREAMS, ogc_config.FILTER_NAME)

            datastream.set_id(datastream_id)
            ogc_config.add_datastream(datastream)

            rc[env_node_id][property_name] = datastream_id  # Store Hamburg to MONICA coupled information

        return make_response(jsonify({"Result": "ok"}), 200)

    def ogc_observation_registration(self, env_node_id, content, onem2m_payload):
        """ Given a Environmental Node ID, this method registers an OBSERVATION in the OGC model.

        :param env_node_id: The Environmental node ID.
        :param content: A content from which will be extracted the observation result and the phenomenon time.
        :param onem2m_payload: A payload from which will be extracted the OBSERVATION id.
        :return: An HTTP response to be returned to the client.
        """
        observation_result = content["result"]  # Load the measure
        phenomenon_time = content["resultTime"]  # Time of the phenomenon
        observation_time = str(arrow.utcnow())
        obs_property = onem2m_payload["nev"]["rep"]["m2m:cin"]["lbl"][0]  # label
        logging.debug(
            "Node: '" + env_node_id + "', Property: '" + obs_property + "', Observation: '" + observation_result + "'.")

        topic_prefix = self._topic_prefix
        datastream_id = self._resource_catalog[env_node_id][obs_property]
        topic = topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # Create OGC Observation and publish
        ogc_observation = OGCObservation(datastream_id, phenomenon_time, observation_result, observation_time)
        observation_payload = json.dumps(dict(ogc_observation.get_rest_payload()))

        published = self.mqtt_publish(topic, observation_payload)
        if published:
            return make_response(jsonify({"result": "Ok"}), 201)
        else:
            return make_response(jsonify({"Error": "Internal server error"}), 500)
