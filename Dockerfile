FROM python:3.6-alpine

#RUN \ apk add --update bash

WORKDIR /monica-scral

ADD  gps-tracker-poll/ /monica-scral/gps-tracker-poll

ADD scral_ogc/ /monica-scral/scral_ogc

ADD setup.py /monica-scral/

ADD requirements.txt /monica-scral/

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install -e .

ENTRYPOINT python3 gps-tracker-poll/start_gps_poll.py -v -o gps-tracker-poll/config/ogc_config_gps.conf -c gps-tracker-poll/config/hamburg/connection_config_internal.json -p DOM 
