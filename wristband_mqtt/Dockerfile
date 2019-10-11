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
COPY wristband /monica_scral/wristband
COPY wristband_mqtt /monica_scral/wristband_mqtt

RUN mkdir /monica_scral/catalogs
VOLUME /monica_scral/catalogs

RUN pip3 install --no-cache-dir -r wristband_mqtt/requirements.txt
RUN pip3 install -e wristband_mqtt

# Enabling bash
RUN apk add --update bash


### local testing:
# ENTRYPOINT python3 scral_startup.py -p local

### docker-compose deployment
ENTRYPOINT python3 scral_startup.py -p deploy

### docker deploy - INTERNAL Configurations
## LST
# ENTRYPOINT python3 scral_startup.py -p LST

## WT
# ENTRYPOINT python3 scral_startup.py -p WT
## Movida
# ENTRYPOINT python3 scral_startup.py -p MOVIDA
## TIVOLI
# ENTRYPOINT python3 scral_startup.py -p TIVOLI
## IoTWeek
# ENTRYPOINT python3 scral_startup.py -p IOTWEEK
