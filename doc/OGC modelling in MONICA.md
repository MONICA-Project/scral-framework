# Understanding OGC modelling in MONICA platform

## OGC Model 

### Introduction
- OGC specification is the semantic model adopted to describe MONICA's resources, properties and relationships.
- MONICA OGC entities are uniquely identified using a naming scheme that avoids entities duplication
and mixed payloads (as long as possible).
- The OGC modeling in MONICA enables both Sensing and Control/Actuation scenarios using the
same modeling scheme

### Requirements
[GOST](https://github.com/gost/server) is the OGC server specification used by MONICA platform.
Reference start-up can be found at this page: https://github.com/gost/docs/blob/master/gost_installation.md


## OGC Entities in MONICA

### THING
- Name is defined at GATEWAY (or CLOUD) level.
    - This allows Gateway to be addressed when needed (e.g. actuation message for wristbands or smartglasses);

### LOCATION
- Location is assigned to the THING;

### SENSOR
- A specific Sensor class is unique in the system;
- Resources can be aggregated using the Sensor type (e.g. get all the Datastreams of type "UWB");

### (OBSERVED) PROPERTY
- A specific Property class is unique in the system;
- Resources can be aggregated using the ObservedProperty type (e.g. get all the Sensor measuring "Localization" property);

### DATASTREAM
- Name is built as: *THING-Name / SENSOR-Name / PROPERTY-Name / deviceId*
- This naming scheme guarantees uniqueness among deployed resources;
- Metadata and Position Coordinates may be stored in Datastreams' corresponding properties (e.g., UnitOfMeasurement, ObservedArea, etc.)
- Advantage:  
    - Sensing and Actuation scenarios can be merged together in the same model;
    - The same OGC model can be used for modeling either device/edge or service layer modules;
- Warning: 
    - Physical devices are now represented through Datastreams rather than Things!

### Example in MONICA domain
The followin table shows some examples of OGC mapping made for MONICA resources.

| THING	| LOCATION | SENSOR | PROPERTY | DATASTREAM	| NOTES |
| ----- | -------- | ------ | -------- | ---------- | ----- |
| a     | b        | c      | d        | e          | n     |ù

MOVIDA	DEXELS	Wristband-GW	Wristband-GW Location	TBD1	TBD2	MOVIDA/Wristband-GW/TBD1/TBD2	This assignment let the GW be reachable as OGC entity. For example, it can be useful to enable actuation scenarios.

	
	
	
	868	Localization	MOVIDA/Wristband-GW/Wristband-868/Localization/wristbandId	

	
	
	
	
	Button	MOVIDA/Wristband-GW/Wristband-868/Button/wristbandId	

	
	
	
	
	Notification	MOVIDA/Wristband-GW/Wristband-868/Notification/wristbandId	

	
	
	
	UWB	Localization	MOVIDA/Wristband-GW/Wristband-UWB/Localization/wristbandId	

	
	
	
	
	Button	MOVIDA/Wristband-GW/Wristband-UWB/Button/wristbandId	

	
	
	
	
	Notification 	MOVIDA/Wristband-GW/Wristband-UWB/Notification/wristbandId	

	KU/VCA	SFN	SFN Location	TBD3	TBD4	MOVIDA/SFN/TBD3/TBD4	This assignment let the SFN be reachable as OGC entity. For example, it can be useful to enable actuation scenarios.

	
	
	
	Camera	CDL-Estimation	MOVIDA/SFN/Camera/CDL-Estimation/cameraId	Camera position coordinates will be stored in the “ObservedArea” field of the Datastream.

	
	
	
	
	FA-Estimation	MOVIDA/SFN/Camera/FA-Estimation/cameraId	Flow Analysis estimation can't be currently produced from more than one camera. Camera position coordinates will be stored in the “ObservedArea” field of the Datastream.

	
	
	
	
	FD-Estimation	MOVIDA/SFN/Fight-Detection/FD-Estimation/cameraId	

	
	
	
	
	OD-Estimation	MOVIDA/SFN/Object-Detetction/OD-Estimation/cameraId	

	
	
	
	
	GC-Estimation	MOVIDA/SFN/Gate-Counting/GC-Estimation/cameraId	

	
	
	
	Crowd-Density-Global	CDG-Estimation	MOVIDA/SFN/Crowd-Density-Global/CDG-Estimation/moduleId	

	
	
	
	Action-Recognition	AC-Estimation	SFN/Action-Recognition/AC-Estimation/moduleId	

This has to be changed into Wristband-GW Property

	B&K	SLM-GW	SLM-GW Location	none	none	none	No requirements for reaching B&K cloud.

	
	
	
	SLM	LAeq	MOVIDA/SLM-GW/SLM/LAeq/deviceId	SLM position coordinates will be stored in the “ObservedArea” field of the Datastream.

	
	
	
	
	LCeq	MOVIDA/SLM-GW/SLM/LCeq/deviceId	SLM position coordinates will be stored in the “ObservedArea” field of the Datastream.

	
	
	
	
	CPBLZeq	MOVIDA/SLM-GW/SLM/CPBLZeq/deviceId	SLM position coordinates will be stored in the “ObservedArea” field of the Datastream.

	SMARTDATANET	SDN-GW	SDN-GW Location	none	none	none	No requirements for reaching SDN platform

	
	
	
	PHONO	LAeq	MOVIDA/SDN-GW/PHONO/LAeq/deviceId	

	
	
	
	
	CPBLZeq	MOVIDA/SDN-GW/PHONO/CPBLZeq/deviceId	

	HAW	RIOT-GW	RIOT-GW Location	none	none	none	No requirements for reaching RIOT GW.

	
	
	
	Environ-Sensor	Temperature	MOVIDA/GW-RIOT/Environ-Sensor/Temperature/deviceId	

	
	
	
	
	Pressure	MOVIDA/GW-RIOT/Environ-Sensor/Pressure/deviceId	

	
	
	
	
	Humidity	MOVIDA/GW-RIOT/Environ-Sensor/Humidity/deviceId	

	
	
	
	
	Sound	MOVIDA/GW-RIOT/Environ-Sensor/Sound/deviceId	

	OPTINVENT	MONICORA-GW	MONICORA-GW Location	Incident	Incident-Notification	MOVIDA/MONICORA-GW/Incident/Incident-Notification	

"Incident" is a Virtual Sensor used to enable incident notifications sent as actuation messages.

"Incident-Notification" is a Virtual Property for notification of incident events.

Resulting Datastream is a Virtual Datastream collecting Observations sent by the DSS to the MONICORA-GW.

No glassesId is required in this case.

	
	
	
	Smart-Glasses	Localization-Smart-Glasses	MOVIDA/MONICORA-GW/Smart-Glasses/Localization-Smart-Glasses/glassesId	

	
	
	
	
	Incident-Reporting	MOVIDA/MONICORA-GW/Smart-Glasses/Incident-Reporting/glassesId	

	
	
	
	
	
	
	




