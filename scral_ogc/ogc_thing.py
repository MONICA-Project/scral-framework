import json
from typing import Optional


class OGCThing:
    """ This class represents the THING entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#things_post
    """

    def __init__(self, name: str, description: str, properties: json, ogc_location_id: Optional[int] = None):
        self._id = None
        self._name = name
        self._description = description
        self._properties = properties
        if ogc_location_id is not None:
            self._ogc_location_id = ogc_location_id

    # setter ###
    def set_id(self, thing_id: int):
        self._id = thing_id

    def set_location_id(self, location_id: int):
        self._ogc_location_id = location_id

    # getter ###
    def get_id(self) -> int:
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_rest_payload(self) -> dict:
        to_return = {
            "name": self._name,
            "description": self._description,
            "properties": self._properties
        }

        if self._ogc_location_id:
            to_return["Locations"] = [{"@iot.id": self._ogc_location_id}]

        return to_return

    def __str__(self):
        to_return = self.get_rest_payload()
        if self._id:
            to_return["@iot.id"] = self._id

        return str(to_return)