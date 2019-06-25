# to be launched from parent folder

FROM python:3.6-alpine
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica-scral
EXPOSE 8000

COPY scral_startup.py /monica-scral
COPY scral_ogc /monica-scral/scral_ogc
COPY scral_module /monica-scral/scral_module
COPY gps_tracker /monica-scral/gps_tracker
COPY gps_tracker_rest /monica-scral/gps_tracker_rest

RUN mkdir /monica-scral/catalogs
VOLUME /monica-scral/catalogs

RUN pip3 install --no-cache-dir -r gps_tracker_rest/requirements.txt
RUN pip3 install -e gps_tracker_rest

### docker deploy - INTERNAL - LOCAL - new
ENTRYPOINT python3 scral_startup.py -p local

### docker deploy - INTERNAL - RIF
# ENTRYPOINT python3 scral_startup.py -v -o gps_tracker_rest/config/ogc_config_gps.conf -c gps_tracker_rest/config/rif/connection_config_internal.json -p RIF
### docker deploy - INTERNAL - Nuits Sonores
# ENTRYPOINT python3 scral_startup.py -v -o gps_tracker_rest/config/ogc_config_gps.conf -c gps_tracker_rest/config/ns/connection_config_internal.json -p NS