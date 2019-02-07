class OGCDatastream:
    """ This class represents the DATASTREAM entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#datastreams_post
    """

    def __init__(self, name, description, ogc_property_id, ogc_sensor_id, ogc_thing_id,
                 unit_of_measurement, x, y, observed_area_type="Point",
                 observation_type="http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"):
        # the id is assigned by the OGC Server
        self.id = None
        self.name = name
        self.description = description
        self.observation_type = observation_type
        self.observed_area = {"coordinates": [x, y], "type": observed_area_type}
        self.unit_of_measurement = unit_of_measurement
        self.ogc_thing_id = ogc_thing_id
        self.ogc_property_id = ogc_property_id
        self.ogc_sensor_id = ogc_sensor_id

    def set_id(self, datastream_id):
        self.id = datastream_id

    def get_id(self):
        return self.id

    def get_rest_payload(self):
        return {
            "name": self.name, "description": self.description, "observationType": self.observation_type,
            "observedArea": self.observed_area, "unitOfMeasurement": self.unit_of_measurement,
            "Thing": {"@iot.id": self.ogc_thing_id}, "ObservedProperty": {"@iot.id": self.ogc_property_id},
            "Sensor": {"@iot.id": self.ogc_sensor_id},
        }
