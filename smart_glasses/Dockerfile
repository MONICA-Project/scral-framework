# to be launched from parent folder

FROM python:3.6-alpine

WORKDIR /monica-scral

EXPOSE 8000

ADD scral_startup.py /monica-scral
ADD scral_ogc /monica-scral/scral_ogc
ADD scral_module /monica-scral/scral_module
ADD smart_glasses /monica-scral/smart_glasses

RUN pip3 install --no-cache-dir -r smart_glasses/requirements.txt
RUN pip3 install -e smart_glasses

# docker deploy - INTERNAL
ENTRYPOINT python3 scral_startup.py -v -o smart_glasses/config/ogc_config_glasses.conf -c smart_glasses/config/leeds/connection_config_internal.json -p LEEDS
# local testing:
# ENTRYPOINT python3 scral_startup.py -v -o gps_tracker_poll/config/ogc_config_gps.conf -c gps_tracker_poll/config/connection_config_local.json -p local