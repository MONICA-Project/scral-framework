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
COPY microphone /monica_scral/microphone
COPY sound_level_meter /monica_scral/sound_level_meter

RUN mkdir /monica_scral/catalogs
VOLUME /monica_scral/catalogs
ENV OGC_FILE "ogc_config_slm.conf"

RUN pip3 install --no-cache-dir -r sound_level_meter/requirements.txt
RUN pip3 install -e sound_level_meter

# Enabling bash and utilities
RUN apk add --update bash
RUN apk add nano
RUN apk add jq

### local testing:
# ENTRYPOINT python3 scral_startup.py -p local

# New docker-compose
ENTRYPOINT python3 scral_startup.py

### docker-compose deployment
# ENTRYPOINT python3 scral_startup.py -p deploy

### docker deploy - INTERNAL Configurations
## WT
# ENTRYPOINT python3 scral_startup.py -p WT
## KFF
# ENTRYPOINT python3 scral_startup.py -p KFF
## MOVIDA
# ENTRYPOINT python3 scral_startup.py -p MOVIDA
## TIVOLI
# ENTRYPOINT python3 scral_startup.py -p TIVOLI
## RIF
# ENTRYPOINT python3 scral_startup.py -p RIF
## Nuits Sonores
# ENTRYPOINT python3 scral_startup.py -p NS
## ROSKILDE
# ENTRYPOINT python3 scral_startup.py -p ROSKILDE
## FDL
# ENTRYPOINT python3 scral_startup.py -p FDL
