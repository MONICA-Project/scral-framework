# to be launched from parent folder

FROM python:3.6-alpine
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica_scral
EXPOSE 8000

COPY scral_startup.py /monica_scral
COPY scral_ogc /monica_scral/scral_ogc
COPY scral_module /monica_scral/scral_module
COPY smart_glasses /monica_scral/smart_glasses

RUN mkdir /monica_scral/catalogs
VOLUME /monica_scral/catalogs

RUN pip3 install --no-cache-dir -r smart_glasses/requirements.txt
RUN pip3 install -e smart_glasses

# Enabling bash
# RUN apk add --no-cache bash
RUN apk add --update bash

### local testing:
# ENTRYPOINT python3 scral_startup.py -p local

### docker deploy - INTERNAL Configurations
## LST
# ENTRYPOINT python3 scral_startup.py -p LST
## LEEDS
ENTRYPOINT python3 scral_startup.py -p LEEDS
## TIVOLI
# ENTRYPOINT python3 scral_startup.py -p TIVOLI
