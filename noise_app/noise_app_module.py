#############################################################################
#      _____ __________  ___    __                                          #
#     / ___// ____/ __ \/   |  / /                                          #
#     \__ \/ /   / /_/ / /| | / /                                           #
#    ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Adaptation Layer  #
#   /____/\____/_/ |_/_/  |_/_____/   v.2.0 - enhanced by Python 3          #
#                                                                           #
# LINKS Foundation, (c) 2019                                                #
# developed by Jacopo Foglietti & Luca Mannella                             #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md     #
#                                                                           #
#############################################################################
import io
import logging
import os
import time
import zipfile
from json import JSONDecodeError
from threading import Thread

from jproperties import Properties
import arrow
import requests
from flask import Flask


from scral_core.constants import ENABLE_FLASK, CATALOG_FILENAME, D_CONFIG_KEY, D_CUSTOM_MODE, \
    ERROR_MISSING_ENV_VARIABLE, ERROR_MISSING_CONNECTION_FILE, ADDRESS_KEY, SEMICOLON, PHENOMENON_TIME_KEY
from scral_core.rest_module import SCRALRestModule
from scral_core import util, rest_util

from noise_app.constants import NOISE_PARTY_ID_KEY, GEO_SERVER_KEY, REST_NOISE_PREFIX_REQUEST, \
    REST_NOISE_PARTY, TIME_TO_SLEEP, DATA_KEY, METADATA_KEY, ID_KEY, REST_NOISE_DATE_FILTER


class SCRALNoiseApp(SCRALRestModule):

    def __init__(self, ogc_config: "OGCConfiguration", connection_file: str, pilot: str,
                 catalog_name: str = CATALOG_FILENAME):

        super().__init__(ogc_config, connection_file, pilot, catalog_name)

        self._run = True

        # 3a) Custom mode
        if D_CONFIG_KEY in os.environ.keys() and os.environ[D_CONFIG_KEY].lower() == D_CUSTOM_MODE:
            if NOISE_PARTY_ID_KEY.upper() not in os.environ.keys():
                logging.critical(NOISE_PARTY_ID_KEY.upper() + " is missing!")
                exit(ERROR_MISSING_ENV_VARIABLE)
            if GEO_SERVER_KEY.upper() not in os.environ.keys():
                logging.critical(GEO_SERVER_KEY.upper() + " is missing!")
                exit(ERROR_MISSING_ENV_VARIABLE)

            self._noise_party_id = os.environ[NOISE_PARTY_ID_KEY.upper()]
            self._geo_server_address = os.environ[GEO_SERVER_KEY.upper()]

        # 3b) No connection file
        elif not connection_file:  # has the connection_file been set?
            logging.critical("Connection file is missing!")
            exit(ERROR_MISSING_CONNECTION_FILE)
        # 3c) Connection file properly set
        else:
            # Storing the OGC server addresses
            connection_config_file = util.load_from_file(connection_file)
            self._noise_party_id = connection_config_file[GEO_SERVER_KEY][NOISE_PARTY_ID_KEY]
            self._geo_server_address = connection_config_file[GEO_SERVER_KEY][ADDRESS_KEY]

    def runtime(self, flask_instance: Flask, mode: int = ENABLE_FLASK):
        rest_util.test_connectivity(self._geo_server_address)
        th = Thread(target=self.noise_capture_manager)
        th.start()
        super().runtime(flask_instance, mode)
        th.join()  # code unreachable

    def noise_capture_manager(self):
        noise_party_url = self._geo_server_address + REST_NOISE_PREFIX_REQUEST \
                          + REST_NOISE_PARTY + str(self._noise_party_id) + SEMICOLON
        datafilter_url = noise_party_url + REST_NOISE_DATE_FILTER

        # ts = "2019-12-04T11:02:58"
        # most_recent_ts = arrow.get(ts)
        most_recent_ts = arrow.utcnow()
        while self._run:
            ts_without_timezone = str(most_recent_ts).split("+")[0]
            timestamp = str(ts_without_timezone).split(".")[0]
            url = datafilter_url + timestamp

            response = requests.get(url)
            if not response or not response.ok:
                logging.error("Wrong response: Wrong request or geoserver down. Request time: "+timestamp)
                time.sleep(TIME_TO_SLEEP)
                continue

            try:
                tracks = response.json()
            except JSONDecodeError:
                logging.warning("Wrong response: check your request. Request time: "+timestamp)
                time.sleep(TIME_TO_SLEEP)
                continue

            if len(tracks) < 1:
                logging.warning("Empty response: no new tracks available at: "+timestamp)

            for track_dict in tracks:
                current_ts = arrow.get(track_dict["record_utc"])
                if current_ts > most_recent_ts:
                    most_recent_ts = current_ts

                # retrieving metadata
                metadata = self.get_noise_capture_metadata(track_dict)
                if not metadata:
                    logging.error("No metadata retrieved for this track!")
                    continue

                # Registering the device (if necessary)
                uuid = metadata[ID_KEY]
                if uuid not in self._resource_catalog:
                    logging.info('Registration of device: "' + str(uuid) + '"')
                    ok = self.ogc_simple_datastream_registration(uuid)
                    if not ok:
                        logging.error("Impossible to create a DATASTREAM for device: " + uuid)
                        continue

                # Sending the OGC OBSERVATION through MQTT
                source_fields = {PHENOMENON_TIME_KEY: "record_utc"}
                result = self.ogc_observation_registration(uuid, metadata)
                if not result:
                    logging.error("Impossible to publish the observation on MQTT broker.")

            time.sleep(TIME_TO_SLEEP)

    @staticmethod
    def get_noise_capture_metadata(track_dict: dict) -> dict:
        geo_link = track_dict[DATA_KEY]
        geo_zip = requests.get(geo_link)
        z = zipfile.ZipFile(io.BytesIO(geo_zip.content))

        logging.info("Files contained in zip archive: " + str(z.namelist()))
        meta_bytes = z.read(METADATA_KEY)
        # geojson_bytes = z.read(TRACK_KEY)
        p = Properties()
        p.load(meta_bytes, "utf-8")

        metadata = {}
        for i in p:
            metadata[i] = p[i].data

        return metadata

    def ogc_observation_registration(self, device_id, payload: dict) -> bool:

        if "record_utc" in payload.keys():
            timestamp = int(payload.pop("record_utc", False))  # Retrieving and removing the phenomenon time
            a = arrow.get(timestamp/1000)
            phenomenon_time = str(a)
        else:
            phenomenon_time = str(arrow.utcnow())

        obs_property_name = self.get_ogc_config().get_observed_properties()[0].get_name()
        result = super()._ogc_observation_registration(device_id, obs_property_name, payload, phenomenon_time)
        return result
