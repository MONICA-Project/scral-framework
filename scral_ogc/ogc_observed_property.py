class OGCObservedProperty:
    """ This class represents the OBSERVEDPROPERTY entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#observedProperties_post
    """

    def __init__(self, name: str, description: str, definition: str):
        self._id = None  # the id is assigned by the OGC Server
        self._name = name
        self._description = description
        self._definition = definition

    def set_id(self, property_id: int):
        self._id = property_id

    def get_id(self) -> int:
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return self._description

    def get_definition(self) -> str:
        return self._definition

    def get_rest_payload(self) -> dict:
        return {
            "name": self._name,
            "description": self._description,
            "definition": self._definition
        }

    def __eq__(self, other: "OGCObservedProperty") -> bool:
        if self.get_id() == other.get_id():
            if self.get_name() == other.get_name():
                if self.get_definition() == other.get_definition():
                    if self.get_description() == other.get_description():
                        return True

        return False

