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
COPY blimp /monica_scral/blimp

RUN mkdir /monica_scral/catalogs
VOLUME /monica_scral/catalogs

RUN pip3 install --no-cache-dir -r blimp/requirements.txt
RUN pip3 install -e blimp

# Enabling bash
RUN apk add --no-cache bash

### docker deploy - INTERNAL - LOCAL - new
# ENTRYPOINT python3 scral_startup.py -p local

### docker deploy - INTERNAL - KFF - new
ENTRYPOINT python3 scral_startup.py -p KFF