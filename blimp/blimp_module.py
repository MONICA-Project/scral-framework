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

from scral_module.constants import ERROR_RETURN_STRING, INTERNAL_SERVER_ERROR, WRONG_PAYLOAD_REQUEST, \
                                   DUPLICATE_REQUEST, INVALID_DATASTREAM, SUCCESS_RETURN_STRING
from blimp.constants import BLIMP_ID_KEY


class SCRALBlimp(SCRALRestModule):
    """ Resource manager for integration of Blimps. """

    def ogc_datastream_registration(self, payload):
        """ This method allow to register the DATASTREAMs related to a blimp in the GOST database. """
        ogc_config = self.get_ogc_config()
        if ogc_config is None:
            return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)

        try:
            blimp_id = payload[BLIMP_ID_KEY]
        except KeyError:
            logging.error("Wrong payload received:")
            logging.error(json.dumps(payload))
            return make_response(jsonify({ERROR_RETURN_STRING: WRONG_PAYLOAD_REQUEST}), 422)

        if blimp_id in self._resource_catalog:
            logging.error("Blimp: '" + str(blimp_id) + "' already registered!")
            return make_response(jsonify({ERROR_RETURN_STRING: DUPLICATE_REQUEST}), 422)

        logging.info("Blimp: '" + str(blimp_id) + "' registration.")

        # Collect OGC information needed to build DATASTREAMs payload
        thing = ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor = ogc_config.get_sensors()[0]  # Assumption: only "Blimp sensor" is defined for this adapter
        sensor_id = sensor.get_id()
        sensor_name = sensor.get_name()

        self._resource_catalog[blimp_id] = {}
        blimp_datastreams = {}
        for op in ogc_config.get_observed_properties():
            property_id = op.get_id()
            property_name = op.get_name()
            property_description = op.get_description()

            datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + blimp_id
            uom = util.build_ogc_unit_of_measure(property_name.lower())

            datastream = OGCDatastream(name=datastream_name, description="Datastream for " + property_description,
                                       ogc_property_id=property_id, ogc_sensor_id=sensor_id, ogc_thing_id=thing_id,
                                       unit_of_measurement=uom)
            datastream_id = ogc_config.entity_discovery(
                datastream, ogc_config.URL_DATASTREAMS, ogc_config.FILTER_NAME)

            if not datastream_id:
                logging.error("No datastream ID for Blimp: " + blimp_id + ", property: " + property_name)
                return make_response(jsonify({ERROR_RETURN_STRING: INVALID_DATASTREAM}), 500)
            else:
                datastream.set_id(datastream_id)
                ogc_config.add_datastream(datastream)

                blimp_datastreams[property_name] = datastream_id
                self._resource_catalog[blimp_id][property_name] = datastream_id

        self.update_file_catalog()
        response_payload = jsonify(blimp_datastreams)
        return make_response(response_payload, 200)

    def ogc_observation_registration(self, datastream_id, payload):
        """ This method stores an OGC OBSERVATION inside the GOST database.

        :param datastream_id: The ID of the DATASTREAM related to the OBSERVATION.
        :param payload: The payload to be inserted inside OGC "result" field.
        :return: An HTTP 201 response if it's possible to publish the OBSERVATION through MQTT, an error code otherwise.
        """
        if not datastream_id:
            return make_response(jsonify({ERROR_RETURN_STRING: "Missing DATASTREAM id!"}), 400)
        if not payload:
            return make_response(jsonify({ERROR_RETURN_STRING: WRONG_PAYLOAD_REQUEST}), 400)

        blimp_id = str(payload[BLIMP_ID_KEY])
        logging.debug("New OBSERVATION from Blimp: '" + str(blimp_id) + "'.")

        observation_result = payload["result"]  # Load the measure
        phenomenon_time = payload["phenomenonTime"]  # Time of the phenomenon
        observation_time = str(arrow.utcnow())
        logging.info(
            "Blimp: '"+blimp_id+"', Datastream: '"+datastream_id+"', Observation: '"+str(observation_result)+"'.")

        topic_prefix = self._topic_prefix
        topic = topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # Create OGC Observation and publish
        ogc_observation = OGCObservation(datastream_id, phenomenon_time, observation_result, observation_time)
        observation_payload = json.dumps(dict(ogc_observation.get_rest_payload()))

        published = self.mqtt_publish(topic, observation_payload, to_print=True)
        self._update_active_devices_counter()
        if published:
            return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)
        else:
            return make_response(jsonify({ERROR_RETURN_STRING: INTERNAL_SERVER_ERROR}), 500)
