class OGCObservedProperty:
    """ This class represents the OBSERVEDPROPERTY entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#observedProperties_post
    """

    def __init__(self, name, description, definition):
        self._id = None  # the id is assigned by the OGC Server
        self._name = name
        self._description = description
        self._definition = definition

    def set_id(self, property_id):
        self._id = property_id

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description

    def get_definition(self):
        return self._definition

    def get_rest_payload(self):
        return {"name": self._name, "description": self._description, "definition": self._definition}
