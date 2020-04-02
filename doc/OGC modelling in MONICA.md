# Understanding OGC modelling in MONICA platform

SCRAL is strongly connected to the OGC Sensor Things model.
To get familiar with this model, it is strongly suggested having a look at the
[official documentation](http://developers.sensorup.com/docs/#sensorthingsAPISensing).
Inside [root_folder]/[SCRAL-Module]/config you will find the file "ogc_config_*.conf",
go there and modify the entities if you need it.

## Introduction
OGC specification is the semantic model adopted to describe MONICA's resources, properties and relationships. <br>
MONICA OGC entities are uniquely identified using a naming scheme that avoids entities duplication and mixed payloads
(as long as possible). <br> Even if, this is not allowed in *OGC Sensor Things - Sensing model*,
the OGC modeling in MONICA enables both Sensing and Control/Actuation scenarios using the same modeling scheme.

## Requirements
[GOST](https://github.com/gost/server) is the OGC server specification used by MONICA platform. <br>
Inside [ROOT_FOLDER]/docker-compose folder, you can find a ready-to-use docker-compose.yml file that
you can use to start a GOST environment.

## OGC Entities

### OGC MONICA Thing
In our paradigm, an OGC Thing represents an IoT platform/system (e.g. a gateway, a hub) and should be unique for each
SCRAL module. Close to this parameter you have to specify the number of the other entities (every field is mandatory,
but it could be set to 0).

### OGC MONICA Sensor
In our paradigm, an OGC Sensor represent a class of device --- i.e. not a specific device like the wristband 579 but the
generic wristband device. If necessary, you could define many different devices for each module
(in our example we will use just one).

### OGC (Observed) Property
An Observed Property represent a measure that could be observed. E.g.: a location, a temperature, a pressure, etc...
If necessary, you could define many different Observed Property for each sensor, but you will have to assign every
property to the right device class (again, in our example we will use just one).

### OGC Datastream (not part of the "ogc_config_*.conf")
The datastream is the entity that will manage the dataflow. <br>
The datastreams should not be modelled in the file "ogc_config_*.conf" because they are generated at runtime. <br>
To guarantees uniqueness among deployed resources, a datastream name should be modelled according to this "schema":
*THING-Name / SENSOR-Name / PROPERTY-Name / deviceId*.<br>
Furthermore, metadata and Position Coordinates could be stored in Datastreams' corresponding properties
(e.g., UnitOfMeasurement, ObservedArea, etc.).
- Advantage:  
    - Sensing and Actuation scenarios can be merged together in the same model;
    - The same OGC model can be used for modeling either device/edge or service layer modules;
- Warning: 
    - Physical devices are now represented through Datastreams rather than Things!

## Virtual Entities (Sensor, Property and Datastream)
The Virtual Entities are not part of the OGC Sensor Things API - Sensing. They were introduced to create a distinction
between class of Sensor that are used only for sensing and class of Sensor that are used only for send a command
(actuate). When you want to define an Observed Property that will be written (instead of being read), you have to define
a Virtual Sensor, a Virtual Property and a Virtual Datastream.



## Example in MONICA domain
The followin table shows some examples of OGC mapping made for MONICA resources.

| THING	| LOCATION | SENSOR | PROPERTY | DATASTREAM	| NOTES |
| ----- | -------- | ------ | -------- | ---------- | ----- |
| Wristband-GW | Wristband-GW Location | Wristband | Localization | Wristband-GW/Wristband/Localization/wristbandId | * |
| | | Wristaband-868 | Localization |	Wristband-GW/Wristband-868/Localization/wristbandId	| * |
| | | | Button | Wristband-GW/Wristband-868/Button/wristbandId | * | 	
| | | | Notification | Wristband-GW/Wristband-868/Notification/wristbandId | * |	
| | | Wristband-UWB	| Localization | Wristband-GW/Wristband-UWB/Localization/wristbandId | Ultra Wide-Band (UWB) |	
| | | | Button | Wristband-GW/Wristband-UWB/Button/wristbandId | * |	
| Security Fusion Node | SFN-Location |	Camera | CDL-Estimation | MOVIDA/SFN/Camera/CDL-Estimation/cameraId | Crowd Density Local (CDL) |
| | | |	FA-Estimation | SFN/Camera/FA-Estimation/cameraId | Flow Analysis (FA) |
| | | | FD-Estimation | SFN/Camera/FD-Estimation/cameraId | Fight Detection (FD) |	
| | | | OD-Estimation | SFN/Camera/OD-Estimation/cameraId | Object Detection (OD) |	
| | | | GC-Estimation | SFN/Camera/GC-Estimation/cameraId | Gate Counting (GC) |	
| | | Crowd-Density-Global | CDG-Estimation	| SFN/Crowd-Density-Global/CDG-Estimation/moduleId |	
| SLM-GW | SLM-GW Location | SLM | LAeq	| SLM-GW/SLM/LAeq/deviceId | Sound Level Meter (SLM) | 
| | | | LCeq | SLM-GW/SLM/LCeq/deviceId	| SLM position coordinates will be stored in the “ObservedArea” field of the Datastream |
| | | | CPBLZeq	| SLM-GW/SLM/CPBLZeq/deviceId | Spectra value |
| SDN-GW | SDN-GW | PHONO | LAeq | MOVIDA/SDN-GW/PHONO/LAeq/deviceId | Smart DataNet (SDN) |	
| | | | CPBLZeq	| MOVIDA/SDN-GW/PHONO/CPBLZeq/deviceId | Spectra value |
| RIOT-GW |	RIOT-GW Location | Environ-Sensor | Temperature	| RIOT-GW/Environ-Sensor/Temperature/deviceId | * |	
| | | | Pressure | RIOT-GW/Environ-Sensor/Pressure/deviceId | * | 
| | | | Humidity | RIOT-GW/Environ-Sensor/Humidity/deviceId | * |
| MONICORA-GW | MONICORA-GW Location | Smart-Glasses | Localization | MONICORA-GW/Smart-Glasses/Localization/glassesId | * |
| | | | Incident-Reporting | MONICORA-GW/Smart-Glasses/Incident-Reporting/glassesId | * | 
| | | Incident	| Incident-Notification	| MONICORA-GW/Incident/Incident-Notification | "Incident" is a Virtual Sensor used to enable incident notifications sent as actuation messages. Resulting Datastream is a Virtual Datastream collecting Observations sent by the DSS to the MONICORA-GW. |