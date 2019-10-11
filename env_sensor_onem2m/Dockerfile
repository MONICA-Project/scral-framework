# to be launched from parent folder

FROM python:3.6-alpine
ARG BUILD_DATE
LABEL build-date=$BUILD_DATE
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica_scral
EXPOSE 8000

COPY scral_startup.py /monica_scral
COPY scral_ogc /monica_scral/scral_ogc
COPY scral_core /monica_scral/scral_core
COPY env_sensor_onem2m /monica_scral/env_sensor_onem2m

RUN mkdir /monica_scral/catalogs
VOLUME /monica_scral/catalogs

RUN pip3 install --no-cache-dir -r env_sensor_onem2m/requirements.txt
RUN pip3 install -e env_sensor_onem2m

# Enabling bash
RUN apk add --no-cache bash

### docker deploy local testing
# ENTRYPOINT python3 scral_startup.py -p local

### docker-compose deployment
# ENTRYPOINT python3 scral_startup.py -p deploy

### docker deploy - INTERNAL Configurations
## PORT Anniversary
# ENTRYPOINT python3 scral_startup.py -p PORT
## Spring DOM
# ENTRYPOINT python3 scral_startup.py -p SDOM
## Winter DOM
ENTRYPOINT python3 scral_startup.py -p WDOM
