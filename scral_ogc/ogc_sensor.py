class OGCSensor:

    def __init__(self, name, description, property_type, metadata, encoding="application/pdf"):
        self.id = None
        self.name = name
        self.description = description
        self.encoding = encoding
        self.metadata = metadata

    def set_id(self, sensor_id):
        self.id = sensor_id

    def get_id(self):
        return self.id

    def get_rest_payload(self):
        return {"name": self.name, "description": self.description,
                "encodingType": self.encoding, "metadata": self.metadata}
