FROM python:3.6-slim
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica_scral

COPY scral_ogc /monica_scral/scral_ogc
COPY scral_core /monica_scral/scral_core
COPY wristband /monica_scral/wristband
RUN mkdir /monica_scral/catalogs
VOLUME /monica_scral/catalogs

RUN apt-get clean \
   && apt-get -y update

RUN apt-get -y install \
	nginx python3-dev build-essential supervisor

RUN pip3 install --no-cache-dir -r wristband/requirements.txt
RUN pip3 install -e wristband

RUN rm /etc/nginx/sites-enabled/default
RUN rm -r /root/.cache

COPY wristband/nginx.conf /etc/nginx
COPY wristband/wristband_nginx.conf /etc/nginx/conf.d/
COPY wristband/uwsgi.ini /etc/uwsgi/
#RUN  ln -s /etc/nginx/sites-available/wristband /etc/nginx/sites-enabled/
COPY wristband/supervisord.conf /etc/

RUN ls -la /monica_scral/*
RUN ls -la /monica_scral/*/*

CMD ["/usr/bin/supervisord"]
