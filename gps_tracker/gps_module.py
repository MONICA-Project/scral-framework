#############################################################################
#      _____ __________  ___    __                                          #
#     / ___// ____/ __ \/   |  / /                                          #
#     \__ \/ /   / /_/ / /| | / /                                           #
#    ___/ / /___/ _, _/ ___ |/ /___                                         #
#   /____/\____/_/ |_/_/  |_/_____/   Smart City Resource Adaptation Layer  #
#                                                                           #
# LINKS Foundation, (c) 2017-2020                                           #
# developed by Jacopo Foglietti & Luca Mannella                             #
# SCRAL is distributed under a BSD-style license -- See file LICENSE.md     #
#                                                                           #
#############################################################################
import logging
from abc import abstractmethod
from typing import Optional, List

from scral_ogc import OGCDatastream

from scral_core import util
from scral_core.scral_module import SCRALModule


class SCRALGPS(SCRALModule):
    """ Resource manager for integration of the GPS-TRACKER-GW (by usage of LoRa devices). """

    @abstractmethod
    def runtime(self):
        """ This is an abstract method that has to be overwritten.
            It manages the runtime operation of the module.
        """
        raise NotImplementedError("Implement runtime method in subclasses")

    def ogc_datastream_registration(self, device_id: str, description: str, unit_of_measure: Optional[str] = None,
                                    catalog_key: Optional[str] = None) -> List[OGCDatastream]:
        """ This method registers new DATASTREAMs in the OGC model. """

        if catalog_key is None:
            catalog_key = device_id
        self._resource_catalog[catalog_key] = {}

        # Collect OGC information needed to build DATASTREAMs payload
        thing = self._ogc_config.get_thing()
        thing_id = thing.get_id()
        thing_name = thing.get_name()

        sensor = self._ogc_config.get_sensors()[0]  # Assumption: only "GPS" Sensor is defined for this adapter
        sensor_id = sensor.get_id()
        sensor_name = sensor.get_name()

        datastream_list = []
        for observed_property in self._ogc_config.get_observed_properties():
            property_id = observed_property.get_id()
            property_name = observed_property.get_name()

            datastream_name = thing_name + "/" + sensor_name + "/" + property_name + "/" + device_id
            ds = OGCDatastream(name=datastream_name, description=description, ogc_property_id=property_id,
                               ogc_sensor_id=sensor_id, ogc_thing_id=thing_id, x=0.0, y=0.0,
                               unit_of_measurement=util.build_ogc_unit_of_measure(unit_of_measure))
            datastream_id = self._ogc_config.entity_discovery(
                                ds, self._ogc_config.URL_DATASTREAMS, self._ogc_config.FILTER_NAME)

            if not datastream_id:
                logging.error("No datastream ID for device: " + device_id + ", property: " + property_name)

            else:
                ds.set_id(datastream_id)
                datastream_list.append(ds)
                self._ogc_config.add_datastream(ds)
                self._resource_catalog[catalog_key][property_name] = ds.get_id()

        return datastream_list
