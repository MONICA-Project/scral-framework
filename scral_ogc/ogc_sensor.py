class OGCSensor:
    """ This class represents the SENSOR entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#sensors_post
    """

    def __init__(self, name, description, metadata, encoding="application/pdf"):
        self.id = None  # the id is assigned by the OGC Server
        self.name = name
        self.description = description
        self.encoding = encoding
        self.metadata = metadata

    def set_id(self, sensor_id):
        self.id = sensor_id

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_rest_payload(self):
        return {"name": self.name, "description": self.description,
                "encodingType": self.encoding, "metadata": self.metadata}
