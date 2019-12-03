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
COPY noise_app /monica_scral/noise_app

RUN mkdir /monica_scral/catalogs
VOLUME /monica_scral/catalogs
ENV OGC_FILE "ogc_config_noise_app.conf"

RUN pip3 install --no-cache-dir -r noise_app/requirements.txt

# Enabling bash and utilities
RUN apk add --no-cache bash
RUN apk add nano
RUN apk add jq

### docker deploy local testing
# ENTRYPOINT python3 scral_startup.py -p local

# New docker-compose
ENTRYPOINT python3 scral_startup.py

### docker-compose deployment
# ENTRYPOINT python3 scral_startup.py -p deploy

### docker deploy - INTERNAL Configurations
## FdL
# ENTRYPOINT python3 scral_startup.py -p fdl
