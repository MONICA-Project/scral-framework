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
COPY blimp /monica_scral/blimp

RUN mkdir /monica_scral/catalogs
VOLUME /monica_scral/catalogs

RUN pip3 install --no-cache-dir -r blimp/requirements.txt
RUN pip3 install -e blimp

# Enabling bash
RUN apk add --no-cache bash

### docker deploy local testing
# ENTRYPOINT python3 scral_startup.py -p local

### docker-compose deployment
ENTRYPOINT python3 scral_startup.py -p deploy

### docker deploy - INTERNAL Configurations
## WT
# ENTRYPOINT python3 scral_startup.py -p WT
## KFF
# ENTRYPOINT python3 scral_startup.py -p KFF