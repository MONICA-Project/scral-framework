# to be launched from parent folder

FROM python:3.6-alpine

WORKDIR /monica-scral

EXPOSE 8000

ADD scral_startup.py /monica-scral
ADD scral_ogc /monica-scral/scral_ogc
ADD scral_module /monica-scral/scral_module
ADD security_fusion_node /monica-scral/security_fusion_node

RUN pip3 install --no-cache-dir -r security_fusion_node/requirements.txt
RUN pip3 install -e security_fusion_node

# docker deploy - INTERNAL
ENTRYPOINT python3 scral_startup.py -v -o security_fusion_node/config/ogc_config_sfn.conf -c security_fusion_node/config/leeds/connection_config_internal.json -p LEEDS
# local testing:
# ENTRYPOINT python3 scral_startup.py -v -o security_fusion_node/config/ogc_config_sfn.conf -c security_fusion_node/config/connection_config_local.json -p local