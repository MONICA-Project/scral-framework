# to be launched from parent folder

FROM python:3.6-alpine
ARG BUILD_DATE
LABEL build-date=$BUILD_DATE
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica_scral
EXPOSE 8000

COPY scral_startup.py /monica_scral
COPY scral_ogc /monica_scral/scral_ogc
COPY scral_module /monica_scral/scral_module
COPY gps_tracker /monica_scral/gps_tracker
COPY gps_tracker_rest /monica_scral/gps_tracker_rest

RUN mkdir /monica_scral/catalogs
VOLUME /monica_scral/catalogs

RUN pip3 install --no-cache-dir -r gps_tracker_rest/requirements.txt
RUN pip3 install -e gps_tracker_rest

# Enabling bash
RUN apk add --update bash

### local testing:
# ENTRYPOINT python3 scral_startup.py -p local

### docker-compose deployment
ENTRYPOINT python3 scral_startup.py -p deploy

### docker deploy - INTERNAL Configurations
## PM
# ENTRYPOINT python3 scral_startup.py -p PM
## RIF
# ENTRYPOINT python3 scral_startup.py -p RIF
## Nuits Sonores
# ENTRYPOINT python3 scral_startup.py -p NS