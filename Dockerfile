FROM python:3.6-alpine

#RUN \ apk add --update bash

WORKDIR /monica-scral

ADD scral_ogc/ /monica-scral/scral_ogc
ADD scral_module/ /monica-scral/scral_module
ADD gps_tracker_poll/ /monica-scral/gps_tracker_poll
ADD requirements.txt /monica-scral/

RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT python3 gps_tracker_poll/start_gps_poll.py -v -o gps_tracker_poll/config/ogc_config_gps.conf  \
           -c gps_tracker_poll/config/hamburg/connection_config_internal.json -p DOM
