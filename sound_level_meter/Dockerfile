# to be launched from parent folder

FROM python:3.6-alpine
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica-scral
EXPOSE 8000

COPY scral_startup.py /monica-scral
COPY scral_ogc /monica-scral/scral_ogc
COPY scral_module /monica-scral/scral_module
COPY microphone /monica-scral/microphone
COPY sound_level_meter /monica-scral/sound_level_meter

RUN mkdir /monica-scral/catalogs
VOLUME /monica-scral/catalogs

RUN pip3 install --no-cache-dir -r sound_level_meter/requirements.txt
RUN pip3 install -e sound_level_meter

### docker deploy - INTERNAL - MOVIDA
# ENTRYPOINT python3 scral_startup.py -v -o sound_level_meter/config/ogc_config_slm.conf -c sound_level_meter/config/movida/connection_config_internal.json -p MOVIDA
### docker deploy - INTERNAL - TIVOLI
# ENTRYPOINT python3 scral_startup.py -v -o sound_level_meter/config/ogc_config_slm.conf -c sound_level_meter/config/tivoli/connection_config_internal.json -p TIVOLI
### docker deploy - INTERNAL - RIF
# ENTRYPOINT python3 scral_startup.py -v -o sound_level_meter/config/ogc_config_slm.conf -c sound_level_meter/config/rif/connection_config_internal.json -p RIF
### docker deploy - INTERNAL - Nuits Sonores
ENTRYPOINT python3 scral_startup.py -v -o sound_level_meter/config/ogc_config_slm.conf -c sound_level_meter/config/ns/connection_config_internal.json -p NS
### local testing:
# ENTRYPOINT python3 scral_startup.py -v -o sound_level_meter/config/ogc_config_slm.conf -c sound_level_meter/config/connection_config_local.json -p local