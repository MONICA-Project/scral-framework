# Deploy and develop a  SCRAL Module
You can find an updated version of this tutorial also on the
[official MONICA tutorial website](http://monica-project.github.io). <br>
<img src="https://github.com/MONICA-Project/monica-project.github.io/raw/master/assets/img/SCRAL-Logo-V1.1.png" alt="SCRAL logo" width="350"/> <br>
This tutorial will help you to understand how to deploy and develop a SCRAL module.

## Table of Contents
1. [Prerequisites](#Prerequisites)
1. [SCRAL quickstart with docker-compose](#SCRAL-quickstart-with-docker-compose)
1. [Run SCRAL Python code](#Run-SCRAL-Python-code)
1. [Implement a new SCRAL module](#Implement-a-new-SCRAL-module)


## Prerequisites

### Download or Fork SCRAL repository.
The SCRAL source code is available in [MONICA project repository](https://github.com/MONICA-Project/scral-framework).
It is possible to fork (or simply download) the repository and start working directly on the source code.

### Docker
To start working with SCRAL it is necessary to have Docker installed on your machine.
To install the proper version for your operating system, have a look to the [Docker documentation page](https://docs.docker.com/).

### GOST
SCRAL depends on the GOST server, a [Go](https://golang.org/) implementation of the Sensing OGC [SensorThings API](http://developers.sensorup.com/docs).
To learn more about OGC and GOST visit the [GOST GitHub page](https://github.com/gost/server) or the MONICA tutorial about 
[OGC Historical Data Retrieval & Visualizations](https://monica-project.github.io/sections/gost_retrieval.html).

To start GOST, you need the docker-compose file that you can download from [GOST repository](https://github.com/gost/docker-compose)
or the file "docker-compose-gost.yml" contained inside the "docker-compose" folder of SCRAL repository.
Once you have the file, from the directory in which the file is stored, you can execute the following command:
```bash
$ docker-compose -f docker-compose-gost.yml up -d
```

## SCRAL quickstart with docker-compose
SCRAL is an IoT adaptation framework that contains different adapters, called also resource managers. In the SCRAL source code repository, you can find a [docker-compose template]( https://github.com/MONICA-Project/scral-framework/blob/master/docker-compose/docker-compose.yml) to start working with SCRAL and GOST. You just need to modify only the name of the adapter (corresponding to the name of the SCRAL image).

This docker-compose file integrate the GOST environment and all the possible SCRAL enviromental variables. Note that the variables that are not commented are mandatory.

### Quickstart introduction
A user can initiate a "quickstart" docker-compose file going inside "docker-compose" folder published inside SCRAL repository and running the command:
```bash
$ docker-compose -f <file_name> up -d
```

### Before Starting
For running a SCRAL docker-compose, it is necessary to set few environmental variables:

•	To enable the usage of the other environmental variables it is necessary to have the variable "CONFIG" set to value "custom".

•	To start a SCRAL module it is necessary to specify the name of the docker image to load (e.g.: monicaproject/scral:glasses)

```docker-compose
scral:
    image: monicaproject/scral:${SCRAL_MODULE}
    container_name: "SCRAL-${SCRAL_MODULE}"
    environment:
        CONFIG: custom
```

*Note 1*: you can run only a quickstart image present inside the [SCRAL archive of MONICA docker-hub](https://hub.docker.com/r/monicaproject/scral/tags).

*Note 2*: for certain modules it is necessary to specify additional environmental variables, for more details have a look to the [MONICA SCRAL dockerhub](https://hub.docker.com/r/monicaproject/scral).


### Testing SCRAL capabilities
When the SCRAL is up and running, the adapter is able to manage data flow mainly through either REST or MQTT messages.
You can interact with SCRAL using the APIs available [here](https://app.swaggerhub.com/apis-docs/scral/SCRAL/1.0.0).

Each SCRAL module exposes also a landing web-page useful for both testing the reachability of the endpoint 
and having a quick overview of the available SCRAL APIs
(e.g.: for gps_tracker_rest the URL is http://localhost:8000/scral/v1.0/gps-tracker-gw).


## Run SCRAL Python code
The SCRAL source code is available in [MONICA project repository](https://github.com/MONICA-Project/scral-framework).
It is possible to fork (or simply download) the repository and start working directly on the source code.
As already mentioned, it is necessary to have already started a GOST docker instance to make SCRAL properly working.
To do that, it is possible to download a docker-compose file from [GOST repository](https://github.com/gost/docker-compose)
or to start the file "docker-compose-gost.yml" contained inside the "docker-compose" folder of SCRAL repository through the command:
```bash
$ docker-compose -f docker-compose-gost.yml up -d
```

### Python Packages
To work properly with the SCRAL, it is required the following Python packages (with the recommended versions):
 - [Eclipse Paho](https://pypi.org/project/paho-mqtt/1.5) 1.5
 - [Flask](https://pypi.org/project/Flask/1.0.2) 1.0.2
 - [CherryPy](https://pypi.org/project/CherryPy/18.1.0) 18.1.0
 - [arrow](https://pypi.org/project/arrow/0.14.2) 0.14.2 (arrow 0.15 not supported)
 - [requests](https://pypi.org/project/requests/2.22.0) 2.22.0
 - [configparser](https://pypi.org/project/configparser/3.7.1) 3.7.1

### Running a SCRAL module from the source code
To give to developers the possibility to quickly switch between different configurations, SCRAL can work also using configuration files.
The configuration files must be called “preference.json”.
If nothing is specified, in each module folder, the default configuration file must be stored inside "config/local".

When you start working with SCRAL, you can decide if you prefer to modify the content of the default file, or if you want to create a new folder inside the already existing "config" folder (e.g.: "config/my_config_folder").

To start an execution just go in the SCRAL main folder and run the following command:
```bash
python <module_name>/<start_module.py> -p <my_config_folder>
```
For example, if you want to start the SCRAL tha integrates the smart glasses module and you want to store your preferences inside: "smart_glasses/config/test/preferences.json", you can run the following command:
```bash
python smart_glasses/start_smart_glasses.py -p test
```
Note: if the environmental variable CONFIG exists and it is set to "custom" then the configuration file is not read.

Once that the SCRAL module is up and running, you can have access to its APIs surfing the "entry endpoint" of the module (e.g.: for gps_tracker_rest the URL is http://localhost:8000/scral/v1.0/gps-tracker-gw).
A complete list of API is avaiable on [SwaggerHub](https://app.swaggerhub.com/apis-docs/scral/SCRAL/).

## Implement a new SCRAL module
The following picture shows the high-level architecture of the SCRAL framework.<br>
<img src="https://github.com/MONICA-Project/monica-project.github.io/raw/master/assets/img/SCRAL_architecture.png" alt="SCRAL high level architecture" width="350"/> <br>

To create a new SCRAL module, you can start from the "template_rest" folder and modify it according to your needs.
This folder contains a generic "ready-to-use" SCRAL module that exposes a REST-based <em>resource manager</em> and it is configured to contact the GOST server through REST and MQTT <em>connectors</em> (look at the previous picture).

### Step 1: Prepare the OGC Configuration
As already mentioned, SCRAL is strongly connected to the OGC Sensor Things model. To get familiar with this model, it is strongly suggested having a look at the [official documentation](http://developers.sensorup.com/docs/#sensorthingsAPISensing).
Inside ./template_rest/config you will find the file "ogc_config_template.conf", go there and modify the entities if you need it.

#### OGC MONICA Thing
In our paradigm, an OGC Thing represents an IoT platform/system (e.g. a gateway, a hub) and should be unique for each SCRAL module.
Close to this parameter you have to specify the number of the other entities (every field is mandatory, but it could be set to 0).

#### OGC MONICA Sensor
In our paradigm, an OGC Sensor represent a class of device --- i.e. not a specific device like the wristband 579 but the generic wristband device. If necessary, you could define many different devices for each module (in our example we will use just one).

#### OGC (Observed) Property
An Observed Property represent a measure that could be observed. E.g.: a location, a temperature, a pressure, etc...
If necessary, you could define many different Observed Property for each sensor, but you will have to assign every property to the right device class (again, in our example we will use just one).

#### OGC Datastream (not part of the ogc_config.conf)
The datastream is the entity that will manage the dataflow. The datastreams should not be modelled in this file because they are generated at runtime.

#### Virtual Entities (Sensor, Property and Datastream)
The Virtual Entities are not part of the OGC Sensor Things API - Sensing. They were introduced to create a distinction between class of Sensor that are used only for sensing and class of Sensor that are used only for send a command (actuate).
When you want to define an Observed Property that will be written (instead of being read), you have to define a Virtual Sensor, a Virtual Property and a Virtual Datastream.

### Step 2: Modify the preferences
As already explained in section "Running a SCRAL module from the source code", if you need different settings, you can go inside folder "./config/local" and modify the content of "preferences.json" or create a new folder with a "preferences.json" file inside.

### Step 3: Checking or adding new REST endpoints
Inside file "start_template_module.py" you can see all the exposed endpoint through Flask.
When you run the "template rest module", a list of the available endpoints could also be reached at the following URL: http://localhost:8000/scral/v1.0/your_module (you can change all the URL going inside file "constants.py" of the template module).

By default, the template module exposes 5 endpoints:
1. <em>documentation</em> (GET): useful to test if the module is correctly running and to have info about other endpoints;
1. <em>registering devices</em> (POST): to add new devices in the MONICA IoT platform;
1. <em>deleting devices</em> (DELETE): to remove a device from the MONICA IoT platform;
1. <em>sending observations</em> (PUT): to send observation related to an already registered device;
1. <em>active devices</em> (GET): to have a list of the already registered devices;

Note: the PUT endpoint must be coded to recognize the same Observed Property defined inside the "ogc_config_template.conf" file.

### Step 4: Adding your logic and functionalities
The SCRAL core already provides some basic functionalities that you can use in your own module (like the OGC registration and the interactions with the MQTT broker).

Two functionality that must be coded in each new SCRAL module are:
- the method for registering new datastreams (usually called "ogc_datastream_registration")
- the method for managing new received observations (usually called "ogc_observation_registration")

You can start from the code in "template_rest_module.py" to understand how to code these functionalities.


### Step 5: Execute and debug your module
To give to developers the possibility to quickly switch between different configuration, the SCRAL can work using a configuration file or through environmental variables.
The configuration files must be called “preference.json”.
If nothing is specified, in each module folder, the default configuration file must be stored inside "config/local".

When you start working with SCRAL, you can decide if you prefer to modify the content of the default file, or if you want to create a new folder inside the existing "config" folder (e.g.: "config/my_config_folder").

To start the execution just go inside the SCRAL main folder and run the following command:
```bash
python <module_name>/<start_module.py> -p <my_config_folder>
```
So, if you want to start the template_rest module and you want to store your preferences inside: "template_rest/config/test/preferences.json", you can run the following command from the main SCRAL folder:
```bash
python template_rest/start_template_module.py -p test
```

Note: if the environmental variable CONFIG exists and it is set to "custom", then the configuration file is not read.


### Step 6: Dockerize
Once tested your module, you can decide to dockerize it.
To do that, you can take advantage of the "Dockerfile" already available in the "template_rest" folder.
If you need also to upload the image on dockerhub, you can use the "deploy.sh" script included in the main folder of the SCRAL repository.
To launch that script it is necessary to specify the name of the resulting image, the name of the dockerfile and the repository on which you want to push the image (it is necessary to run "docker login" before running the script).
```bash
./deploy.sh <module_name> <dockerfile_name> <repository_name>
```
