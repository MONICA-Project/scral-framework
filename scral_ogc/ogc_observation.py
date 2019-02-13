class OGCObservation:
    """ This class represents the OBSERVATION entity of the OCG Sensor Things model.
        For more info: http://developers.sensorup.com/docs/#observations_post
    """

    def __init__(self, ogc_datastream_id, phenomenon_time, result, result_time):
        self._id = None  # the id is assigned by the OGC Server
        self._ogc_datastream_id = ogc_datastream_id
        self._phenomenon_time = phenomenon_time
        self._result_time = result_time
        self._result = result

    def set_id(self, observation_id):
        self._id = observation_id

    def get_id(self):
        return self._id

    def get_rest_payload(self):
        return {
            "phenomenonTime": self._phenomenon_time,
            "resultTime": self._result_time,
            "result": self._result,
            "Datastream": {
                "@iot.id": self._ogc_datastream_id
            }
        }
