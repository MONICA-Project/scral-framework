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
from scral_module.rest_module import SCRALRestModule
from gps_tracker.gps_module import SCRALGPS

from gps_tracker_rest.constants import TAG_ID_KEY, TYPE_KEY, TIMESTAMP_KEY


class SCRALGPSRest(SCRALRestModule, SCRALGPS):

    def new_datastream(self, payload):
        device_id = payload[TAG_ID_KEY]
        description = payload[TYPE_KEY]
        datastream = self.ogc_datastream_registration(device_id, description, "position")
        self.update_file_catalog()
        return datastream

    def ogc_observation_registration(self, observed_property, payload):
        gps_tag_id = payload[TAG_ID_KEY]
        if gps_tag_id not in self._resource_catalog:
            return None

        observation_time = str(arrow.utcnow())
        try:
            phenomenon_time = payload[TIMESTAMP_KEY]
        except KeyError:
            phenomenon_time = str(arrow.utcnow())

        logging.info("GPS: '"+gps_tag_id+"', Observation:\n"+json.dumps(payload)+".")

        datastream_id = self._resource_catalog[gps_tag_id][observed_property]
        topic_prefix = self._topic_prefix
        topic = topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # Create OGC Observation and publish
        ogc_observation = OGCObservation(datastream_id, phenomenon_time, payload, observation_time)
        observation_payload = json.dumps(ogc_observation.get_rest_payload())

        mqtt_response = self.mqtt_publish(topic, observation_payload)
        self._update_active_devices_counter()
        return mqtt_response
