class OGCObservedProperty:

    def __init__(self, name, description, definition):
        self.id = None
        self.name = name
        self.description = description
        self.definition = definition

    def set_id(self, property_id):
        self["id"] = property_id

    def get_id(self):
        return self["id"]

    def get_rest_payload(self):
        return {"name": self.name, "description": self.description, "definition": self.property_type}
