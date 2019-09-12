# to be launched from parent folder

FROM python:3.6-alpine
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica_scral
EXPOSE 8000

COPY scral_startup.py /monica_scral
COPY scral_ogc /monica_scral/scral_ogc
COPY scral_module /monica_scral/scral_module
COPY security_fusion_node /monica_scral/security_fusion_node

RUN mkdir /monica_scral/catalogs
VOLUME /monica_scral/catalogs

RUN pip3 install --no-cache-dir -r security_fusion_node/requirements.txt
RUN pip3 install -e security_fusion_node

# Enabling bash
# RUN apk add --no-cache bash
RUN apk add --update bash

### local testing:
# ENTRYPOINT python3 scral_startup.py -p local

### docker deploy - INTERNAL Configurations
## PM
# ENTRYPOINT python3 scral_startup.py -p PM
## KFF
# ENTRYPOINT python3 scral_startup.py -p KFF
## MOVIDA
# ENTRYPOINT python3 scral_startup.py -p MOVIDA
## RIF
# ENTRYPOINT python3 scral_startup.py -p RIF
## TIVOLI
# ENTRYPOINT python3 scral_startup.py -p TIVOLI
## DOM
# ENTRYPOINT python3 scral_startup.py -p DOM
## LEEDS
ENTRYPOINT python3 scral_startup.py -p LEEDS
