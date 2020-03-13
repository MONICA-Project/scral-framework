#############################################################################
#      _____ __________  ___    __                                          #
#     / ___// ____/ __ \/   |  / /                                          #
#     \__ \/ /   / /_/ / /| | / /                                           #
#    ___/ / /___/ _, _/ ___ |/ /___                                         #
#   /____/\____/_/ |_/_/  |_/_____/   Smart City Resource Adaptation Layer  #
#                                                                           #
# LINKS Foundation, (c) 2017-2020                                           #
# developed by Jacopo Foglietti & Luca Mannella                             #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md     #
#                                                                           #
#############################################################################
import json
import arrow
import logging

from flask import make_response, jsonify

from scral_core.constants import SUCCESS_RETURN_STRING, OGC_OBSERVED_AREA_KEY, \
    ERROR_RETURN_STRING, WRONG_REQUEST, DUPLICATE_REQUEST
from microphone.constants import NAME_KEY
from phonometer.constants import DESCRIPTION_KEY, LAEQ_KEY, SPECTRA_KEY, VALUE_TYPE_KEY, RESPONSE_KEY
from phonometer_rest.constants import DATA_KEY, MEASURES_KEY, MEASURE_KEY, SAMPLES_KEY, WRONG_PHONOMETERS, \
     DEVICE_NAME_KEY ,SAMPLE_VALUE_KEY, SAMPLE_START_TIME_KEY, SAMPLE_END_TIME_KEY, SAMPLE_OK_PROCESSED, \
     WRONG_SAMPLES, WRONG_MEASURES

from microphone.microphone_module import SCRALMicrophone


class SCRALPhonometerREST(SCRALMicrophone):
    """ Resource manager for integration of Phonometers with a REST endpoint. """

    def ogc_datastream_registration(self, payload: json):
        """ """
        try:
            device_name = payload[NAME_KEY]
            device_description = payload[DESCRIPTION_KEY]
            observed_area = payload[OGC_OBSERVED_AREA_KEY]
            device_coordinates = (observed_area["coordinates"]["lng"], observed_area["coordinates"]["lat"])
        except KeyError as ke:
            logging.error("Missing key: "+str(ke))
            return make_response(jsonify({ERROR_RETURN_STRING: WRONG_REQUEST}), 400)

        # Check whether device has been already registered
        if device_name in self._resource_catalog:
            logging.debug("Device: " + device_name + " already registered with id: " + device_name)
            return make_response(jsonify({ERROR_RETURN_STRING: DUPLICATE_REQUEST}), 409)

        self._resource_catalog[device_name] = {}
        # Iterate over ObservedProperties
        for ogc_property in self._ogc_config.get_observed_properties():
            self._new_datastream(
                ogc_property, device_name, device_coordinates, device_description)

        self.update_file_catalog()
        return make_response(jsonify({SUCCESS_RETURN_STRING: "Ok"}), 201)

    def observation_registration(self, raw_payload: json):
        try:
            payload = raw_payload[DATA_KEY]
        except KeyError as ke:
            logging.error("Wrong format payload, missing key: "+str(ke))
            return make_response(jsonify({ERROR_RETURN_STRING: WRONG_REQUEST}), 400)

        successfully_processed = 0
        wrong_samples = 0
        wrong_measures = 0
        wrong_phonometers = 0
        for phono_object in payload:
            try:
                phono_name = phono_object[DEVICE_NAME_KEY]
                logging.info("Processing measures from device: "+phono_name)
                phono_measures = phono_object[MEASURES_KEY]

                for measure in phono_measures:
                    try:
                        measure_type = measure[MEASURE_KEY]
                        if (measure_type != LAEQ_KEY) and (measure_type != SPECTRA_KEY):
                            logging.error("Unrecognized measure: " + str(measure_type))
                            wrong_measures = wrong_measures + 1
                            break

                        datastream_id = self._resource_catalog[phono_name][measure_type]
                        samples = measure[SAMPLES_KEY]

                        for s in samples:
                            try:
                                sample_start_time = arrow.get(s[SAMPLE_START_TIME_KEY])
                                sample_end_time = arrow.get(s[SAMPLE_END_TIME_KEY])
                                sample_value = s[SAMPLE_VALUE_KEY]

                                # In this moment there are no difference in sample managements
                                # if measure_type is LAEQ_KEY:
                                #     pass
                                # elif measure_type is SPECTRA_KEY:
                                #     pass
                                # else:
                                #     logging.error("Unrecognized sample type: " + str(measure_type))
                                #     break

                                response = {"value": [{
                                    "values": [sample_value],
                                    "startTime": str(sample_start_time),
                                    "endTime": str(sample_end_time)
                                }]}
                                observation_result = {VALUE_TYPE_KEY: LAEQ_KEY, RESPONSE_KEY: response}

                                self.ogc_observation_registration(
                                    datastream_id, str(sample_start_time), observation_result)
                                successfully_processed = successfully_processed + 1
                            except KeyError as ke:
                                logging.error("Missing key: " + str(ke))
                                logging.error("Going to next sample (if available)...")
                                wrong_samples = wrong_samples + 1

                    except KeyError as ke:
                        logging.error("Missing key: " + str(ke))
                        logging.error("Going to next measure array (if available)...")
                        wrong_measures = wrong_measures + 1

            except KeyError as ke:
                logging.error("Missing key: " + str(ke))
                logging.error("Going to next phonometer object (if available)...")
                wrong_phonometers = wrong_phonometers + 1

        body = {
            SUCCESS_RETURN_STRING: "Ok",
            SAMPLE_OK_PROCESSED: successfully_processed,
            WRONG_SAMPLES: wrong_samples,
            WRONG_MEASURES: wrong_measures,
            WRONG_PHONOMETERS: wrong_phonometers
        }
        return make_response(jsonify(body), 201)
