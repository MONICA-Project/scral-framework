class OGCThing:
    """ This class represents the THING entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#things_post
    """

    def __init__(self, name, description, properties, ogc_location_id=None):
        self.id = None
        self.name = name
        self.description = description
        self.properties = properties
        if ogc_location_id is not None:
            self.ogc_location_id = ogc_location_id

    def set_id(self, thing_id):
        self.id = thing_id

    def get_id(self):
        return self.id

    def get_rest_payload(self):
        to_return = {"name": self.name, "description": self.description, "properties": self.properties}

        if self.ogc_location_id:
            to_return["Locations"] = [{"@iot.id": self.ogc_location_id}]

        return to_return
