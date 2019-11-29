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
from threading import Thread

import Properties as Properties
import arrow
import requests
import rest_util
from flask import Flask


from ogc_configuration import OGCConfiguration

from scral_core.constants import ENABLE_FLASK, CATALOG_FILENAME, D_CONFIG_KEY, D_CUSTOM_MODE, \
    ERROR_MISSING_ENV_VARIABLE, ERROR_MISSING_CONNECTION_FILE, ADDRESS_KEY, SEMICOLON
from scral_core.rest_module import SCRALRestModule
from scral_core import util

from noise_app.constants import NOISE_PARTY_ID_KEY, GEO_SERVER_KEY, REST_NOISE_PREFIX_REQUEST, \
    REST_NOISE_PARTY, TIME_TO_SLEEP, DATA_KEY, METADATA_KEY, ID_KEY


class SCRALNoiseApp(SCRALRestModule):

    def __init__(self, ogc_config: OGCConfiguration, connection_file: str, pilot: str,
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

        while self._run:
            timestamp = str(arrow.utcnow()).split(".")[0]
            url = noise_party_url + timestamp

            response = requests.get(url)
            tracks = response.json()

            for track_dict in tracks:
                # retrieving metadata
                metadata = self.get_noise_capture_metadata(track_dict)
                if not metadata:
                    logging.error("No metadata retrieved for this track!")
                    continue

                # Registering the device (if necessary)
                uuid = metadata[ID_KEY]
                if uuid not in self._resource_catalog:
                    logging.info("Registration of device: '" + str(uuid))
                    ok = self.ogc_datastream_registration(uuid, metadata)
                    if not ok:
                        logging.error("Impossible to create a DATASTREAM for device: " + uuid)
                        continue

                # Sending the OGC OBSERVATION through MQTT
                result = self.ogc_observation_registration(metadata)
                if not result:
                    logging.error("Impossible to publish on MQTT broker.")

            time.sleep(TIME_TO_SLEEP)

    @staticmethod
    def get_noise_capture_metadata(track_dict: dict) -> dict:
        geo_link = track_dict[DATA_KEY]
        geo_zip = requests.get(geo_link)
        z = zipfile.ZipFile(io.BytesIO(geo_zip.content))

        logging.info("Files contained in zip archive: " + z.namelist())
        meta_bytes = z.read(METADATA_KEY)
        # geojson_bytes = z.read(TRACK_KEY)
        p = Properties()
        p.load(meta_bytes, "utf-8")

        metadata = {}
        for i in p:
            metadata[i] = p[i].data

        return metadata

    def ogc_datastream_registration(self, wristband_id: str, payload: dict) -> bool:
        pass

    def ogc_observation_registration(self, obs_property: str, payload: dict) -> bool:
        pass