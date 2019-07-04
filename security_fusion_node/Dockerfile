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

### docker deploy - INTERNAL - KFF - new
ENTRYPOINT python3 scral_startup.py -p KFF

### local testing:
# ENTRYPOINT python3 scral_startup.py -v -o security_fusion_node/config/ogc_config_sfn.conf -c security_fusion_node/config/connection_config_local.json -p local

### docker deploy - INTERNAL - KFF
# ENTRYPOINT python3 scral_startup.py -v -o security_fusion_node/config/ogc_config_sfn.conf -c security_fusion_node/config/kff/connection_config_internal.json -p KFF
### docker deploy - INTERNAL - MOVIDA
# ENTRYPOINT python3 scral_startup.py -v -o security_fusion_node/config/ogc_config_sfn.conf -c security_fusion_node/config/movida/connection_config_internal.json -p MOVIDA
### docker deploy - INTERNAL - RIF
# ENTRYPOINT python3 scral_startup.py -v -o security_fusion_node/config/ogc_config_sfn.conf -c security_fusion_node/config/rif/connection_config_internal.json -p RIF
### docker deploy - INTERNAL - TIVOLI
# ENTRYPOINT python3 scral_startup.py -v -o security_fusion_node/config/ogc_config_sfn.conf -c security_fusion_node/config/tivoli/connection_config_internal.json -p TIVOLI
### docker deploy - INTERNAL - DOM
# ENTRYPOINT python3 scral_startup.py -v -o security_fusion_node/config/ogc_config_sfn.conf -c security_fusion_node/config/dom/connection_config_internal.json -p DOM
### docker deploy - INTERNAL - LEEDS
# ENTRYPOINT python3 scral_startup.py -v -o security_fusion_node/config/ogc_config_sfn.conf -c security_fusion_node/config/leeds/connection_config_internal.json -p LEEDS
