# to be launched from parent folder

FROM python:3.6-alpine
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica-scral
EXPOSE 8000

COPY scral_startup.py /monica-scral
COPY scral_ogc /monica-scral/scral_ogc
COPY scral_module /monica-scral/scral_module
COPY wristband /monica-scral/wristband
COPY wristband_mqtt /monica-scral/wristband_mqtt

RUN mkdir /monica-scral/catalogs
VOLUME /monica-scral/catalogs

RUN pip3 install --no-cache-dir -r wristband_mqtt/requirements.txt
RUN pip3 install -e wristband_mqtt

# Enabling bash
RUN apk add --update bash

### docker deploy local testing
# ENTRYPOINT python3 scral_startup.py -p local

### docker deploy - INTERNAL - LST
# ENTRYPOINT python3 scral_startup.py -p LST

### docker deploy - INTERNAL - WT
ENTRYPOINT python3 scral_startup.py -p WT
### docker deploy - INTERNAL - Movida
# ENTRYPOINT python3 scral_startup.py -p MOVIDA
### docker deploy - INTERNAL - TIVOLI
# ENTRYPOINT python3 scral_startup.py -p TIVOLI
### docker deploy - INTERNAL - IoTWeek
# ENTRYPOINT python3 scral_startup.py -p IOTWEEK