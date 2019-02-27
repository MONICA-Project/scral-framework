# to be launched from parent folder

FROM python:3.6-alpine

WORKDIR /monica-scral

ADD scral_startup.py /monica-scral
ADD scral_ogc /monica-scral/scral_ogc
ADD scral_module /monica-scral/scral_module
ADD gps_tracker_poll /monica-scral/gps_tracker_poll

RUN pip3 install --no-cache-dir -r gps_tracker_poll/requirements.txt
RUN pip3 install -e gps_tracker_poll

# docker deploy
ENTRYPOINT python3 scral_startup.py -v -o gps_tracker_poll/config/ogc_config_gps.conf -c gps_tracker_poll/config/hamburg/connection_config_internal.json -p DOM
# local testing:
# ENTRYPOINT python3 scral_startup.py -v -o gps_tracker_poll/config/ogc_config_gps.conf -c gps_tracker_poll/config/connection_config_local.json -p local