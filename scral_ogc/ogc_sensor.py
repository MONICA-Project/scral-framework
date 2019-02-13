class OGCSensor:
    """ This class represents the SENSOR entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#sensors_post
    """

    def __init__(self, name, description, metadata, encoding="application/pdf"):
        self._id = None  # the id is assigned by the OGC Server
        self._name = name
        self._description = description
        self._encoding = encoding
        self._metadata = metadata

    def set_id(self, sensor_id):
        self._id = sensor_id

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_rest_payload(self):
        return {"name": self._name, "description": self._description,
                "encodingType": self._encoding, "metadata": self._metadata}
