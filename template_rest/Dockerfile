# Note: launch "docker build" from parent folder

FROM python:3.6-alpine
ARG BUILD_DATE
LABEL build-date=$BUILD_DATE
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica_scral
EXPOSE 8000

COPY scral_startup.py /monica_scral
COPY scral_ogc /monica_scral/scral_ogc
COPY scral_core /monica_scral/scral_core
COPY template_rest /monica_scral/template_rest

RUN mkdir /monica_scral/catalogs
VOLUME /monica_scral/catalogs
ENV OGC_FILE "ogc_config_template.conf"

RUN pip3 install --no-cache-dir -r template_rest/requirements.txt
RUN pip3 install -e template_rest

# Enabling bash and utilities
RUN apk add --update bash
RUN apk add nano
RUN apk add jq

### local testing:
ENTRYPOINT python3 scral_startup.py -p local

### For using Enviromental variable use just:
# ENTRYPOINT python3 scral_startup.py
