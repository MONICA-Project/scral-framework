# to be launched from parent folder

FROM python:3.6-alpine

WORKDIR /monica-scral

EXPOSE 8000

ADD scral_startup.py /monica-scral
ADD scral_ogc /monica-scral/scral_ogc
ADD scral_module /monica-scral/scral_module
ADD wristband /monica-scral/wristband

RUN pip3 install --no-cache-dir -r wristband/requirements.txt
RUN pip3 install -e wristband

### docker deploy - INTERNAL - Movida
# ENTRYPOINT python3 scral_startup.py -v -o wristband/config/ogc_config_wristband.conf -c wristband/config/movida/connection_config_internal.json -p MOVIDA
### docker deploy - INTERNAL - TIVOLI
# ENTRYPOINT python3 scral_startup.py -v -o wristband/config/ogc_config_wristband.conf -c wristband/config/tivoli/connection_config_internal.json -p TIVOLI
### docker deploy - INTERNAL - IoTWeek
ENTRYPOINT python3 scral_startup.py -v -o wristband/config/ogc_config_wristband.conf -c wristband/config/iotweek/connection_config_internal.json -p IOTWEEK

### docker deploy - INTERNAL - LST
# ENTRYPOINT python3 scral_startup.py -v -o wristband/config/ogc_config_wristband.conf -c wristband/config/lst/connection_config_internal.json -p LST
### docker deploy - EXTERNAL - LST
# ENTRYPOINT python3 scral_startup.py -v -o wristband/config/ogc_config_wristband.conf -c wristband/config/lst/connection_config_external.json -p LST

### local testing:
# ENTRYPOINT python3 scral_startup.py -v -o wristband/config/ogc_config_wristband.conf -c wristband/config/connection_config_local.json -p local