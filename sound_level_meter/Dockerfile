# to be launched from parent folder

FROM python:3.6-alpine

WORKDIR /monica-scral

EXPOSE 8000

ADD scral_startup.py /monica-scral
ADD scral_ogc /monica-scral/scral_ogc
ADD scral_module /monica-scral/scral_module
ADD sound_level_meter /monica-scral/sound_level_meter

RUN pip3 install --no-cache-dir -r sound_level_meter/requirements.txt
RUN pip3 install -e sound_level_meter

### docker deploy - INTERNAL - MOVIDA
# ENTRYPOINT python3 scral_startup.py -v -o sound_level_meter/config/ogc_config_slm.conf -c sound_level_meter/config/movida/connection_config_internal.json -p MOVIDA
### docker deploy - INTERNAL - TIVOLI
# ENTRYPOINT python3 scral_startup.py -v -o sound_level_meter/config/ogc_config_slm.conf -c sound_level_meter/config/tivoli/connection_config_internal.json -p TIVOLI
### docker deploy - INTERNAL - RIF
ENTRYPOINT python3 scral_startup.py -v -o sound_level_meter/config/ogc_config_slm.conf -c sound_level_meter/config/rif/connection_config_internal.json -p RIF
### local testing:
# ENTRYPOINT python3 scral_startup.py -v -o sound_level_meter/config/ogc_config_slm.conf -c sound_level_meter/config/connection_config_local.json -p local