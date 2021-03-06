# ChangeLog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

    Legenda:
    - "Added" for new features.
    - "Changed" for changes in existing functionality.
    - "Deprecated" for soon-to-be removed features.
    - "Removed" for now removed features.
    - "Fixed" for any bug fixes.
    - "Security" in case of vulnerabilities.

## [Unreleased]
This part will contain project for future releases.

- Create a SCRAL endpoint for patching fields of registered devices.

## [3.1] - 2020-02-14
The MQTT wristband module was reintroduced.

### Added
- MQTT wristband module

### Changed
- The previous "wristband" module was split to improve modularity. You should consider it now as a general module.
The previous functionality are now offered by "wristband_rest" module.

## [3.0] - 2020-01-28
This is the first open source SCRAL version.
In this version we removed some modules not particular meaningful and we slightly changed the way in which SCRAL retrives configuration variables.

### Added
- Active Devices endpoints enabled also in phonometer module.
- all classes contained inside "scral_ogc" package have now a __str__ method.
- together with "entity_discovery" a method "entity_override" was introduced in scral_ogc package.
- A template of a REST SCRAL Module

### Changed
- in "/active-devices" REST endpoint: "registered_devices" is no more a stand alone field, is now a field of "active_devices" data structure.
- "result" field of payload sent from "phonometer" module is now the same of "SLM" module.
- "cli_file.json" is now "preference.json"
- Now is it possible to set the MQTT GOST prefix in the preference.json file (instead of pilot name)

### Removed
- Some modules are removed before of the open source release due to useless complexity: blimp, env_sensor_onem2m, noise_app, wb mqtt, wb dumb and wb nginx.
- All the references to pilots configurations are removed.
- Removed the Docker-compose file contained in every module.
- It is no more necessary to a have a "connection_file", all the configuration variables are stored in "preference.json"

## [2.5] - 2019-12-03
This update introduces a new integration module: the noise-application manager.
This module is considered as an external platform, so it should be deployed on ports 88xx.

### Added
- noise_app manager module


## [2.4] - 2019-11-29
This update introduces the possibility to configure a SCRAL module through Environmental Variable (and so through docker-compose file also).
Now, SCRAL has an official logo!

### Added
- First official version of SCRAL logo;
- Support to environmental variables;
- .gitignore and Changelog file are now part of the repository;
- Added the entry "/resource-catalog" for SLM to have a direct access to registered devices;
- "deploy.sh" now can:
    - address different DockerHub repository as third parameter;
    - print the time elapsed to build and push the docker image;
    
### Changed
- Subscribing MQTT broker of "gps_tracker_poll" module is no more hard-coded, it is now settable through "connection_file".
- docker-compose.yml and docker-compose-scral.yml use now the last GOST version. The original docker-compose.yml is moved in "testing" folder and renamed "docker-compose-0.5.yml". 

### Fixed
- Fixed an issue of name shadowing of "active_devices" in SLM module; 


## [2.3] - 2019-10-08
This update introduce full support to type-hinting in SCRAL source code.

### Added
- Full support to type-hinting.

## [2.2] - 2019-09-30
Several utility functions are provided in this update.
In particular from the end point for retrieving the registered devices, is now also available an "active_devices" JSON Object containing information about number of observation sent. SCRAL expose also a new REST DELETE functionality and new MQTT special-purpose MQTT WB simulator and subscriber are provided. 

### Added
- It is possible to specify a name for the resource catalog file;
- Together with the list of active devices are returned:
    - the explicit number of registered devices ("registered_devices": int);
    - an "active_devices" JSON Object that stores the number of messages that a SCRAL module receives in a fixed amount of time. 
- An archive folder to store zipped logs;
- A folder to store reports;
- A utility test provided by Antonio Defina to test SCRAL WB module;
- A more useful MQTT subscriber was added (in particular for testing wb module);
- The MQTT client used by SCRAL is now identified by an ID;
- 3 new version of WB module was introduces:
    - a dumb version (for testing purposes);
    - a version using nginx + uWSGI as backend to improve performance;
    - a WB module with MQTT resource manager (suggested for Large Scale Pilots).
- A deploy folder was added to every module with the purpose of creating a set of quickstart module for task 7.6 (Toolbox);
- Delete functionality is introduced (in almost SCRAL REST modules).
  It gives the possibility to remove all the datastreams associated to a particular device;

### Changed
- When MQTT publish fails, 502 HTTP error code is retrieved instead of 500.
- When an Observation is received, SCRAL prints in its log more debug information:
     - the timestamp in which the message is forwarded through MQTT Paho;
     - the time elapsed since PhenomenonTime;
     - the time elapsed since ResultTime.
- MQTT testing publisher support now command line parameter to specify:
    - how many observation you want to publish;
    - how many seconds you want to wait between burst.
     
### Fixed
- When resource catalog is written on file, is dived in chunks to reduce amount of memory used and to improve performance.
- Package Arrow is set to version 0.14.2 due to abuse of warning messages (to be investigated in the future).


## [2.1] - 2019-06-25
SCRAL does not retrieve all the parameter from command line, it is necessary to specify only the pilot name. Other parameters are retrieved from 2 files: "cli_file.json" and "connection_config.json".
Pilot name is necessary to specify the right GOST-MQTT topic prefix and to address the right configuration folder.

### Changed
- Only pilot name could be used on command line. Other parameters are retrieved by files.


## [2.0] - 2019-06-13
This was a major refactoring of what it was done by Jacopo in the previous year. This was the first SCRAL version to use Python 3.x.
The tool was continuously developed in the first months of 2019.

### Added
- SCRAL startup ASCII banner;
- Object Oriented paradigm;
- Command line parameter are now supported;
- Introduced a testing MQTT Publisher and Subscriber;
- Endpoints and basic documentation is now exposed on a REST endpoint;
- An Endpoint with the list of the currently registered devices is now exposed for every REST module;
- A UML architectural diagram was added;
- A deployment strategy written in "deployment - suggested ports.md" file;
- A script (deploy.sh) to easy deploy images on DockerHub is introduced;

### Changed
- SCRAL requires now Python 3 to work properly;
- Resource Catalog is now stored in a file;
- When SCRAL is dockerized, the Resource Catalog will be stored in a Docker Data Volume;
- Logging is executed in a more precise way using also Python "logging" library;
- Flask is no more the only possible backend (also CherryPy and WSGI are supported).

### Removed
- Python 2 is no more supported.


## [1.0] - 2018
This was the first proof-of-concept of SCRAL developed by Jacopo Foglietti in 2018.
It was based on Python 2.7.