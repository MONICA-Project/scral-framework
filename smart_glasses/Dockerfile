# to be launched from parent folder

FROM python:3.6-alpine
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica-scral
EXPOSE 8000

COPY scral_startup.py /monica-scral
COPY scral_ogc /monica-scral/scral_ogc
COPY scral_module /monica-scral/scral_module
COPY smart_glasses /monica-scral/smart_glasses

RUN mkdir /monica-scral/catalogs
VOLUME /monica-scral/catalogs

RUN pip3 install --no-cache-dir -r smart_glasses/requirements.txt
RUN pip3 install -e smart_glasses

### docker deploy - INTERNAL - LOCAL - new
ENTRYPOINT python3 scral_startup.py -p local

### docker deploy - INTERNAL - LST
# ENTRYPOINT python3 scral_startup.py -v -o smart_glasses/config/ogc_config_glasses.conf -c smart_glasses/config/lst/connection_config_internal.json -p LST
### docker deploy - EXTERNAL - LST
# ENTRYPOINT python3 scral_startup.py -v -o smart_glasses/config/ogc_config_glasses.conf -c smart_glasses/config/lst/connection_config_external.json -p LST

### docker deploy - INTERNAL - Leeds
# ENTRYPOINT python3 scral_startup.py -v -o smart_glasses/config/ogc_config_glasses.conf -c smart_glasses/config/leeds/connection_config_internal.json -p LEEDS
### docker deploy - INTERNAL - Tivoli
# ENTRYPOINT python3 scral_startup.py -v -o smart_glasses/config/ogc_config_glasses.conf -c smart_glasses/config/tivoli/connection_config_internal.json -p TIVOLI
### local testing:
# ENTRYPOINT python3 scral_startup.py -v -o smart_glasses/config/ogc_config_glasses.conf -c smart_glasses/config/connection_config_local.json -p local
