import json


class OGCDatastream:
    """ This class represents the DATASTREAM entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#datastreams_post
    """

    def __init__(self, name: str, description: str, ogc_property_id: int, ogc_sensor_id: int, ogc_thing_id: int,
                 unit_of_measurement: json, x: float = 0.0, y: float = 0.0,
                 observed_area_type="Point",
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

    def set_id(self, datastream_id: int):
        self._id = datastream_id

    def set_mqtt_topic(self, mqtt_topic: str):
        self._mqtt_topic = mqtt_topic

    def get_id(self) -> int:
        return self._id

    def get_mqtt_topic(self) -> str:
        return self._mqtt_topic

    def get_name(self) -> str:
        return self._name

    def get_rest_payload(self) -> dict:
        return {
            "name": self._name, "description": self._description, "observationType": self._observation_type,
            "observedArea": self._observed_area, "unitOfMeasurement": self._unit_of_measurement,
            "Thing": {"@iot.id": self._ogc_thing_id}, "ObservedProperty": {"@iot.id": self._ogc_property_id},
            "Sensor": {"@iot.id": self._ogc_sensor_id},
        }
