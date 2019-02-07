class OGCObservation:

    def __init__(self, ogc_datastream_id, phenomenon_time, result_time, result, encoding_type="application/vnd.geo+json"):
        self.id = None
        self.ogc_datastream_id = ogc_datastream_id
        self.phenomenon_time = phenomenon_time
        self.result_time = result_time
        self.result = result
        self.encoding_type = encoding_type

    def set_id(self, property_id):
        self["id"] = property_id

    def get_id(self):
        return self["id"]

    def get_rest_payload(self):
        return {"phenomenonTime": self.phenomenon_time, "resultTime": self.result_time, "result": self.result,
                "encodingType": self.encoding_type, "Datastream": {"@iot.id": self.ogc_datastream_id}}
