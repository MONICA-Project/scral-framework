class OGCLocation:
    """ This class represents the LOCATION entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#locations_post
    """

    def __init__(self, name: str, description: str, x: float, y: float,
                 location_type: str = "Point", encoding_type: str = "application/vnd.geo+json"):
        self._id = None  # the id is assigned by the OGC Server
        self._name = name
        self._description = description
        self._encodingType = encoding_type
        self._location = {
            "coordinates": [x, y],
            "type": location_type
        }

    def set_id(self, location_id: int):
        self._id = location_id

    def get_id(self):
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_rest_payload(self) -> dict:
        return {
            "name": self._name,
            "description": self._description,
            "encodingType": self._encodingType,
            "location": self._location
        }

    def __str__(self):
        to_return = self.get_rest_payload()
        if self._id:
            to_return["@iot.id"] = self._id

        return str(to_return)