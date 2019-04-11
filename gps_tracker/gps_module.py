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
import logging
from abc import abstractmethod

from scral_ogc import OGCDatastream

from scral_module import util
from scral_module.scral_module import SCRALModule


class SCRALGPS(SCRALModule):
    """ Resource manager for integration of the GPS-TRACKER-GW (by usage of LoRa devices). """

    @abstractmethod
    def runtime(self):
        """ This is an abstract method that has to be overwritten.
            It manages the runtime operation of the module.
        """
        raise NotImplementedError("Implement runtime method in subclasses")

    def ogc_datastream_registration(self, device_id, description, unit_of_measure=None):
        """ This method registers new DATASTREAMs in the OGC model. """

        # Collect OGC information needed to build DATASTREAMs payload
        thing = self._ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor = self._ogc_config.get_sensors()[0]  # Assumption: only "GPS" Sensor is defined for this adapter
        sensor_id = sensor.get_id()
        sensor_name = sensor.get_name()

        # Assumption: only 1 observed property registered
        property_id = self._ogc_config.get_observed_properties()[0].get_id()
        property_name = self._ogc_config.get_observed_properties()[0].get_name()

        datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + device_id
        datastream = OGCDatastream(name=datastream_name, description=description, ogc_property_id=property_id,
                                   ogc_sensor_id=sensor_id, ogc_thing_id=thing_id, x=0.0, y=0.0,
                                   unit_of_measurement=util.build_ogc_unit_of_measure(unit_of_measure))
        datastream_id = self._ogc_config.entity_discovery(
                            datastream, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)
        if not datastream_id:
            logging.error("No datastream ID for device: " + device_id + ", property: " + property_name)
            return False
        else:
            datastream.set_id(datastream_id)
            self._ogc_config.add_datastream(datastream)
            return datastream
