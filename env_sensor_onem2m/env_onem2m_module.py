#############################################################################
#      _____ __________  ___    __                                          #
#     / ___// ____/ __ \/   |  / /                                          #
#     \__ \/ /   / /_/ / /| | / /                                           #
#    ___/ / /___/ _, _/ ___ |/ /___   Smart City Resource Adaptation Layer  #
#   /____/\____/_/ |_/_/  |_/_____/   v.2.0 - enhanced by Python 3          #
#                                                                           #
# LINKS Foundation, (c) 2019                                                #
# developed by Jacopo Foglietti & Luca Mannella                             #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md     #
#                                                                           #
#############################################################################
import json
import logging

import arrow
import cherrypy as cherrypy
from flask import Flask, request, jsonify

from env_sensor_onem2m.constants import *
from scral_module.scral_module import SCRALModule
import scral_module.util as util
from scral_ogc import OGCDatastream, OGCObservation

app = Flask(__name__)

_onem2m_module = None


class SCRALEnvOneM2M(SCRALModule):

    def __init__(self, connection_file, pub_topic_prefix, ogc_config):
        super().__init__(ogc_config, connection_file, pub_topic_prefix)

        connection_config_file = util.load_from_file(connection_file)
        self._listening_address = connection_config_file["REST"]["listening_address"]["address"]
        self._listening_port = int(connection_config_file["REST"]["listening_address"]["port"])

        self._ogc_config = ogc_config

        global _onem2m_module
        _onem2m_module = self

    # noinspection PyMethodOverriding
    def runtime(self):
        cherrypy.tree.graft(app, "/")
        cherrypy.config.update({"server.socket_host": self._listening_address,
                                "server.socket_port": self._listening_port,
                                "engine.autoreload.on": False,
                                })
        cherrypy.engine.start()
        cherrypy.engine.block()


@app.route(URI_ENV_NODE, methods=["POST"])
def new_onem2m_request():
    logging.debug(new_onem2m_request.__name__ + " method called")

    container_path = str(request.json["m2m:sgn"]["sur"])
    substrings = container_path.split("/")
    env_node_id = None
    for i in range(len(substrings)):
        if substrings[i].startswith("env-node"):
            env_node_id = substrings[i]
            break
    if env_node_id is None:
        return jsonify({"Error": "Environmental Node ID not found!"}), 400

    content = json.loads(request.json["m2m:sgn"]["nev"]["rep"]["m2m:cin"]["con"])
    haw_sensor_id = content["sensorId"]

    if _onem2m_module is None:
        return jsonify({"Error": "Internal server error"}), 500

    rc = _onem2m_module.get_resource_catalog()
    if env_node_id not in rc:
        logging.info("Node: " + str(env_node_id) + " registration.")
        ogc_datastream_registration(env_node_id)

    ogc_observation_registration(env_node_id, content, request.json["m2m:sgn"])

    return jsonify({"result": "Ok"}), 201


def ogc_datastream_registration(env_node_id):
    if _onem2m_module is None:
        return jsonify({"Error": "Internal server error"}), 500

    ogc_config = _onem2m_module.get_ogc_config()
    if ogc_config is None:
        return jsonify({"Error": "Internal server error"}), 500

    # Collect OGC information needed to build DATASTREAMs payload
    thing = ogc_config.get_thing()
    thing_id = thing.get_id()
    thing_name = thing.get_name()

    sensor = ogc_config.get_sensors()[0]  # Assumption: only Environmental Node is defined for this adapter
    sensor_id = sensor.get_id()
    sensor_name = sensor.get_name()

    rc = _onem2m_module.get_resource_catalog()
    rc[env_node_id] = {}
    for op in ogc_config.get_observed_properties():
        property_id = op.get_id()
        property_name = op.get_name()
        property_description = op.get_description()

        datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + env_node_id
        if property_name.lower() == "wind-speed":
            uom = {
                "name": property_name,
                "symbol": "m/s",
                "definition": "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#MeterPerSecond"
            }
        # elif
        else:
            uom = {"name": property_name}

        datastream = OGCDatastream(name=datastream_name, description="Datastream for " + property_description,
                                   ogc_property_id=property_id, ogc_sensor_id=sensor_id, ogc_thing_id=thing_id,
                                   x=0.0, y=0.0, unit_of_measurement=uom)
        datastream_id = ogc_config.entity_discovery(
            datastream, ogc_config.URL_DATASTREAMS, ogc_config.FILTER_NAME)

        datastream.set_id(datastream_id)
        ogc_config.add_datastream(datastream)

        rc[env_node_id][property_name] = datastream_id  # Store Hamburg to MONICA coupled information


def ogc_observation_registration(env_node_id, content, onem2m_payload):
    observation_result = content["result"]  # Load the measure
    phenomenon_time = content["resultTime"]  # Time of the phenomenon
    observation_time = str(arrow.utcnow())
    obs_property = onem2m_payload["nev"]["rep"]["m2m:cin"]["lbl"][0]  # label
    logging.debug("Node: '"+env_node_id+"', Property: '"+obs_property+"', Observation: '"+observation_result+"'.")

    topic_prefix = _onem2m_module.get_topic_prefix()
    datastream_id = _onem2m_module.get_resource_catalog()[env_node_id][obs_property]
    topic = topic_prefix + "Datastreams(" + str(datastream_id) + ")/Observations"

    # Create OGC Observation and publish
    ogc_observation = OGCObservation(datastream_id, phenomenon_time, observation_result, observation_time)
    observation_payload = json.dumps(dict(ogc_observation.get_rest_payload()))

    _onem2m_module.mqtt_publish(topic, observation_payload)


@app.route("/")
def test():
    """ Checking if Flask is working. """
    logging.debug(test.__name__ + " method called")

    return "<h1>Flask is running!</h1>"


@app.route(URI_DEFAULT)
def test_module():
    """ Checking if SCRAL is running. """
    logging.debug(test_module.__name__ + " method called")

    to_ret = "<h1>SCRAL module is running!</h1>\n"
    to_ret += "<h2> ToDo: Insert list of API here! </h2>"
    return to_ret
