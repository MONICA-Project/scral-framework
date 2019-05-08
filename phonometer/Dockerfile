# to be launched from parent folder

FROM python:3.6-alpine

WORKDIR /monica-scral

EXPOSE 8000

ADD scral_startup.py /monica-scral
ADD scral_ogc /monica-scral/scral_ogc
ADD scral_module /monica-scral/scral_module
ADD phonometer /monica-scral/phonometer

RUN pip3 install --no-cache-dir -r phonometer/requirements.txt
RUN pip3 install -e phonometer

### docker deploy - INTERNAL - MOVIDA
ENTRYPOINT python3 scral_startup.py -v -o phonometer/config/ogc_config_slm.conf -c phonometer/config/movida/connection_config_internal.json -p MOVIDA
### local testing:
# ENTRYPOINT python3 scral_startup.py -v -o sound_level_meter/config/ogc_config_slm.conf -c sound_level_meter/config/connection_config_local.json -p local