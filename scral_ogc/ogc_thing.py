class OGCThing:

    def __init__(self, name, description, property_type, ogc_location):
        self.id = None
        self.name = name
        self.description = description
        self.properties = {"type": property_type, "Locations": [{"@iot.id": ogc_location.get_location_id()}]}

    def set_id(self, thing_id):
        self.id = thing_id

    def get_id(self):
        return self.id

    def get_rest_payload(self):
        return {"name": self.name, "description": self.description, "properties": self.properties}
