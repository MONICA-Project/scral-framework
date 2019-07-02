# to be launched from parent folder

FROM python:3.6-alpine
LABEL authors="Jacopo Foglietti, Luca Mannella"

WORKDIR /monica-scral
EXPOSE 8000

COPY scral_startup.py /monica-scral
COPY scral_ogc /monica-scral/scral_ogc
COPY scral_module /monica-scral/scral_module
COPY microphone /monica-scral/microphone
COPY phonometer /monica-scral/phonometer

RUN mkdir /monica-scral/catalogs
VOLUME /monica-scral/catalogs

RUN pip3 install --no-cache-dir -r phonometer/requirements.txt
RUN pip3 install -e phonometer

### docker deploy - INTERNAL - LOCAL - new
# ENTRYPOINT python3 scral_startup.py -p local

### docker deploy - INTERNAL - MOVIDA - new
ENTRYPOINT python3 scral_startup.py -p MOVIDA
