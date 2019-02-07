class OGCLocation:

    def __init__(self, name, description, x, y, location_type="Point"):
        self.id = None
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
