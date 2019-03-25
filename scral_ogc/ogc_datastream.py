import json


class OGCDatastream:
    """ This class represents the DATASTREAM entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#datastreams_post
    """

    def __init__(self, name, description, ogc_property_id, ogc_sensor_id, ogc_thing_id,
                 unit_of_measurement: json, x=0.0, y=0.0, observed_area_type="Point",
                 observation_type="http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"):
        # the id is assigned by the OGC Server
        self._id = None
        self._name = name
        self._description = description
        self._observation_type = observation_type
        self._observed_area = {"coordinates": [x, y], "type": observed_area_type}
        self._unit_of_measurement = unit_of_measurement
        self._ogc_thing_id = ogc_thing_id
        self._ogc_property_id = ogc_property_id
        self._ogc_sensor_id = ogc_sensor_id
        self._mqtt_topic = None

    def set_id(self, datastream_id):
        self._id = datastream_id

    def set_mqtt_topic(self, mqtt_topic):
        self._mqtt_topic = mqtt_topic

    def get_id(self):
        return self._id

    def get_mqtt_topic(self):
        return self._mqtt_topic

    def get_name(self):
        return self._name

    def get_rest_payload(self):
        return {
            "name": self._name, "description": self._description, "observationType": self._observation_type,
            "observedArea": self._observed_area, "unitOfMeasurement": self._unit_of_measurement,
            "Thing": {"@iot.id": self._ogc_thing_id}, "ObservedProperty": {"@iot.id": self._ogc_property_id},
            "Sensor": {"@iot.id": self._ogc_sensor_id},
        }
