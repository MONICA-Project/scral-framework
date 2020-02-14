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

from scral_ogc import OGCObservation, OGCDatastream
from scral_core.rest_module import SCRALRestModule


class SCRALWristband(SCRALRestModule):

    def ogc_datastream_registration(self, wristband_id: str, payload: dict) -> bool:
        if self._ogc_config is None:
            return False

        # Collect OGC information needed to build DATASTREAMs payload
        thing = self._ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        wearable_type = payload["type"].upper()
        sensor_id = None
        for sensor in self._ogc_config.get_sensors():
            if sensor.get_name() == wearable_type:
                sensor_id = sensor.get_id()
                sensor_name = sensor.get_name()

        if not sensor_id:
            logging.error("Wearable type: <"+wearable_type+"> is not registered in OGC Model.")
            return False

        # with self._lock:
        self._resource_catalog[wristband_id] = {}
        for op in self._ogc_config.get_observed_properties():
            property_id = op.get_id()
            property_name = op.get_name()
            property_description = op.get_description()

            datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + wristband_id

            datastream = OGCDatastream(name=datastream_name, description="Datastream for " + property_description,
                                       ogc_property_id=property_id, ogc_sensor_id=sensor_id, ogc_thing_id=thing_id,
                                       x=0.0, y=0.0, unit_of_measurement={"metadata": payload})
            datastream_id = self._ogc_config.entity_discovery(
                datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)

            datastream.set_id(datastream_id)
            self._ogc_config.add_datastream(datastream)

            # with self._lock:
            self._resource_catalog[wristband_id][property_name] = datastream_id

            topic = self._topic_prefix + "Datastreams"
            mqtt_payload = {"wristband_id": wristband_id,
                            "observed_property": property_name,
                            "datastream_id": datastream_id}
            self.mqtt_publish(topic, json.dumps(mqtt_payload), to_print=False)
            # what should happens if an MQTT message is not properly sent?

        # with self._lock:
        self.update_file_catalog()

        return True

    def ogc_observation_registration(self, obs_property: str, payload: dict) -> Union[bool, None]:
        wristband_id = payload["tagId"]
        if wristband_id not in self._resource_catalog:
            logging.warning("Wristband '"+wristband_id+"' not yet registered, it will be automatically registered.")
            ok = self.ogc_datastream_registration(wristband_id, payload)
            if not ok:
                logging.error("Registration of wristband: '"+wristband_id+"' failed!")
                return None

        phenomenon_time = payload.pop("timestamp", False)  # Retrieving and removing the phenomenon time
        if not phenomenon_time:
            phenomenon_time = str(arrow.utcnow())
        observation_time = str(arrow.utcnow())

        logging.debug(
            "Wristband: '"+wristband_id+"', Property: '"+obs_property+"', Observation:\n"+json.dumps(payload)+".")

        datastream_id = self._resource_catalog[wristband_id][obs_property]
        topic = self._topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

        # Create OGC Observation and publish
        ogc_observation = OGCObservation(datastream_id, phenomenon_time, payload, observation_time)
        observation_payload = json.dumps(ogc_observation.get_rest_payload())

        mqtt_result = self.mqtt_publish(topic=topic, payload=observation_payload, to_print=False)
        self._update_active_devices_counter()
        return mqtt_result

    def ogc_service_observation_registration(self, datastream: OGCDatastream, payload: dict) -> bool:
        phenomenon_time = payload.pop("timestamp", False)  # Retrieving and removing the phenomenon time
        if not phenomenon_time:
            phenomenon_time = str(arrow.utcnow())
        observation_time = str(arrow.utcnow())

        logging.debug(
            "Service: '" + datastream.get_name() + "', Observation:\n" + json.dumps(payload) + ".")

        topic = self._topic_prefix + "Datastreams(" + str(datastream.get_id()) + ")/Observations"

        # Create OGC Observation and publish
        ogc_observation = OGCObservation(datastream.get_id(), phenomenon_time, payload, observation_time)
        observation_payload = json.dumps(ogc_observation.get_rest_payload())

        return self.mqtt_publish(topic=topic, payload=observation_payload)
