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

# docker deploy - INTERNAL
ENTRYPOINT python3 scral_startup.py -v -o wristband/config/ogc_config_wearable.conf -c wristband/config/tivoli/connection_config_internal.json -p TIVOLI
# local testing:
# ENTRYPOINT python3 scral_startup.py -v -o wristband/config/ogc_config_wearable.conf -c wristband/config/connection_config_local.json -p local