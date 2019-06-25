# to be launched from parent folder

FROM python:3.6-alpine
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica-scral
EXPOSE 8000

COPY scral_startup.py /monica-scral
COPY scral_ogc /monica-scral/scral_ogc
COPY scral_module /monica-scral/scral_module
COPY env_sensor_onem2m /monica-scral/env_sensor_onem2m

RUN mkdir /monica-scral/catalogs
VOLUME /monica-scral/catalogs

RUN pip3 install --no-cache-dir -r env_sensor_onem2m/requirements.txt
RUN pip3 install -e env_sensor_onem2m

### docker deploy - INTERNAL - LOCAL - new
ENTRYPOINT python3 scral_startup.py -p local

# docker deploy - INTERNAL - PORT
# ENTRYPOINT python3 scral_startup.py -v -o env_sensor_onem2m/config/ogc_config_onem2m.conf -c env_sensor_onem2m/config/port/connection_config_internal.json -p PORT
### docker deploy - INTERNAL - DOM
# ENTRYPOINT python3 scral_startup.py -v -o env_sensor_onem2m/config/ogc_config_onem2m.conf -c env_sensor_onem2m/config/dom/connection_config_internal.json -p DOM
### local testing:
# ENTRYPOINT python3 scral_startup.py -v -o env_sensor_onem2m/config/ogc_config_onem2m.conf -c env_sensor_onem2m/config/connection_config_local.json -p local