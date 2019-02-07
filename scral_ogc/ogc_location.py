class OGCLocation:
    """ This class represents the LOCATION entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#locations_post
    """

    def __init__(self, name, description, x, y, location_type="Point"):
        self.id = None  # the id is assigned by the OGC Server
        self.name = name
        self.description = description
        self.encodingType = "application/vnd.geo+json"
        self.location = {"coordinates": [x, y], "type": location_type}

    def set_id(self, location_id):
        self["id"] = location_id

    def get_id(self):
        return self["id"]

    def get_rest_payload(self):
        return {"name": self.name, "description": self.description,
                "encodingType": self.encodingType, "location": self.location}
