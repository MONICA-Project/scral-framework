FROM python:3.6-alpine

WORKDIR /monica-scral

ADD setup.py /monica-scral/
ADD requirements.txt /monica-scral/
ADD scral_ogc/ /monica-scral/scral_ogc
ADD scral_module/ /monica-scral/scral_module
ADD gps_tracker_poll/ /monica-scral/gps_tracker_poll

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install -e .

# docker deploy
ENTRYPOINT python3 gps_tracker_poll/start_gps_poll.py -v -o gps_tracker_poll/config/ogc_config_gps.conf -c gps_tracker_poll/config/hamburg/connection_config_internal.json -p DOM
# local testing:
# ENTRYPOINT python3 gps_tracker_poll/start_gps_poll.py -v -o gps_tracker_poll/config/ogc_config_onem2m.conf -c gps_tracker_poll/config/connection_config_local.json -p local