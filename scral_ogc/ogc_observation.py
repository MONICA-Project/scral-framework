class OGCObservation:
    """ This class represents the OBSERVATION entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#observations_post
    """

    def __init__(self, ogc_datastream_id: int, phenomenon_time: str, result, result_time: str):
        self._id = None  # the id is assigned by the OGC Server
        self._ogc_datastream_id = ogc_datastream_id
        self._phenomenon_time = phenomenon_time
        self._result_time = result_time
        self._result = result

    def set_id(self, observation_id: int):
        self._id = observation_id

    def get_id(self) -> int:
        return self._id

    def get_rest_payload(self) -> dict:
        return {
            "phenomenonTime": self._phenomenon_time,
            "resultTime": self._result_time,
            "result": self._result,
            "Datastream": {
                "@iot.id": self._ogc_datastream_id
            }
        }

    def __str__(self):
        to_return = self.get_rest_payload()
        if self._id:
            to_return["@iot.id"] = self._id

        return str(to_return)