FROM python:3.6-alpine
RUN pip3 install --no-cache-dir paho-mqtt
RUN pip3 install --no-cache-dir arrow
RUN apk add --update bash

ARG BUILD_DATE
LABEL build-date=$BUILD_DATE
LABEL authors="Antonio Defina, Jacopo Foglietti and Luca Mannella"

WORKDIR /test_subscriber

COPY testing/test_subscriber/client_mqtt_test.py /test_subscriber
COPY testing/test_subscriber/dictionary_catalog.py /test_subscriber
COPY testing/test_subscriber/dictionary_catalog_movida.py /test_subscriber

RUN mkdir /test_subscriber/logs
# VOLUME /test_subscriber/logs

ENTRYPOINT python3 client_mqtt_test.py
# ENTRYPOINT python3 client_mqtt_test.py > /test_subscriber/logs/log.txt
# ENTRYPOINT python3 client_mqtt_test.py
