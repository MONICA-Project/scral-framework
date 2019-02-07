class OGCDataStream:

    def __init__(self, name, description, property_type, metadata, ogc_property_id, ogc_sensor_id, ogc_thing_id,
                 unit_of_measurement, x, y, observed_area_type = "Point",
                 observation_type="http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"):
        self.id = None
        self.name = name
        self.description = description
        self.observation_type = observation_type
        self.ogc_property_id = ogc_property_id
        self.ogc_sensor_id = ogc_sensor_id
        self.ogc_thing_id = ogc_thing_id
        self.unit_of_measurement = unit_of_measurement
        self.observed_area = {"coordinates": [x, y], "type": observed_area_type}

    def set_id(self, sensor_id):
        self.id = sensor_id

    def get_id(self):
        return self.id

    def get_rest_payload(self):
        return {"name": self.name, "description": self.description, "observationType": self.observation_type,
                "ObservedProperty": {"@iot.id": self.ogc_property_id}, "Sensor": {"@iot.id": self.ogc_sensor_id},
                "Thing": {"@iot.id": self.ogc_thing_id}, "observedArea": self.observed_area}
