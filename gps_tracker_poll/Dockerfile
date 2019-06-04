# to be launched from parent folder

FROM python:3.6-alpine
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica-scral
EXPOSE 8000

COPY scral_startup.py /monica-scral
COPY scral_ogc /monica-scral/scral_ogc
COPY scral_module /monica-scral/scral_module
COPY gps_tracker_poll /monica-scral/gps_tracker_poll

RUN mkdir /monica-scral/catalogs
VOLUME /monica-scral/catalogs

RUN pip3 install --no-cache-dir -r gps_tracker_poll/requirements.txt
RUN pip3 install -e gps_tracker_poll

# docker deploy - INTERNAL - DOM
ENTRYPOINT python3 scral_startup.py -v -o gps_tracker_poll/config/ogc_config_gps.conf -c gps_tracker_poll/config/hamburg/connection_config_internal.json -p DOM
# local testing:
# ENTRYPOINT python3 scral_startup.py -v -o gps_tracker_poll/config/ogc_config_gps.conf -c gps_tracker_poll/config/connection_config_local.json -p local