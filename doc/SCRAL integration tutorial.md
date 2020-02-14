---
layout: default
title: SCRAL integration tutorial <!--- This is required for the page to come in the side pane --->
---
<span style="font-size:2em;">SCRAL integration tutorial</span>
<!-- Using Span is a hack to avoid the title to come again in TOC.-->

<img src="https://github.com/MONICA-Project/monica-project.github.io/raw/master/assets/img/SCRAL-Logo-V1.1.png" alt="SCRAL logo" width="350"/> <br>
This tutorial will help you to understand how to start using SCRAL and how to develop your own SCRAL module.

<!--
## Table of Contents
1. [Prerequisites](#Prerequisites)
2. [SCRAL quickstart with docker-compose](#SCRAL-quickstart-with-docker-compose)
3. [Run SCRAL Python code](#Run-SCRAL-Python-code)
4. [Implement a new SCRAL module](#Implement-a-new-SCRAL-module)
-->

* TOC (Do not remove. This is required to show Table of contents)
 {:toc}


## Prerequisites

### Docker
To start working with SCRAL is necessary to have Docker installed on your machine.
To install the proper version for your operating system, have a look to the [Docker documentation page](https://docs.docker.com/).

### GOST
SCRAL depends on GOST, a [Go](https://golang.org/) implementation of the Sensing OGC [SensorThings API](http://developers.sensorup.com/docs).
To learn more about OGC and GOST visit the [GOST GitHub page](https://github.com/gost/server) or the MONICA tutorial about 
[OGC Historical Data Retrieval & Visualizations](https://monica-project.github.io/sections/gost_retrieval.html).


## SCRAL quickstart with docker-compose
SCRAL is an adaptation framework that contains different integration modules.
Inside SCRAL repository is available a docker-compose folder to help you start working with SCRAL and GOST.

### Quickstart introduction
A user can start a "quickstart" docker-compose file going inside "docker-compose" folder published inside SCRAL repository and running the command:
```bash
$ docker-compose -f <file_name> up -d
```

To have a first start the complete environment (GOST+SCRAL), we suggest starting from "docker-compose.yml" file.

### Before Starting
For running a SCRAL docker-compose, it is necessary that few environmental variables are set.
•	To enable the usage of the other environmental variables is necessary to have variable "CONFIG" sets to value "custom".
•	To start a SCRAL module is necessary to specify the name of the docker image to load (e.g.: monicaproject/scral:glasses)

```docker-compose
scral:
    image: monicaproject/scral:${SCRAL_MODULE}
    container_name: "SCRAL-${SCRAL_MODULE}"
    environment:
        CONFIG: “custom”
```

*Note*: you can run only a quickstart image present inside the [SCRAL archive of MONICA docker-hub](https://hub.docker.com/r/monicaproject/scral/tags).
*Note2*: for certain modules is necessary to specify additional environmental variables, for more details have a look to the [MONICA SCRAL dockerhub](https://hub.docker.com/r/monicaproject/scral).

### Testing SCRAL capabilities
When SCRAL is up and running, it can manage data flow mainly through REST or MQTT messages.
You can interact with SCRAL using the APIs available [here](www.example.org).
<!-- generate and publish Swagger SCRAL API -->

Each SCRAL module with a REST endpoint exposes also a landing page useful both for testing reachability of the endpoint 
and for having a quick overview of the available SCRAL API
(e.g.: for gps_tracker_rest the URL is http://localhost:8000/scral/v1.0/gps-tracker-gw).


## Run SCRAL Python code
SCRAL open source code is available inside [MONICA project repository](https://github.com/MONICA-Project/scral-framework).
It is possible to fork (or simply download) the repository and start working directly on the source code.
As already mentioned, it is necessary to have already started a GOST instance to make SCRAL properly work.
To do that, it is possible to download a docker-compose file from [GOST repository](https://github.com/gost/docker-compose)
or to start the file "docker-compose-gost.yml" contained inside the "docker-compose" folder of SCRAL repository through the command:
```bash
$ docker-compose -f docker-compose-gost.yml up -d
```

### Running a SCRAL module from the source code
To give to developers the possibility to quickly switch between different configuration, SCRAL can work also using configuration files.
The configuration files must be called “preference.json”.
If nothing is specified, in each module folder, the default configuration file must be stored inside "config/local".

When you start working with SCRAL, you can decide if you prefer to modify the content of the default file, or if you want to create a new folder inside the already present "config" folder (e.g.: "config/my_config_folder").

To start the execution just go in the SCRAL main folder and run the following command:
```bash
python <module_name>/<start_module.py> -p <my_config_folder>
```
For example, if you want to start the smart glasses module and you want to store your preferences inside: "smart_glasses/config/test/preferences.json", you can run the following command:
```bash
python smart_glasses/start_smart_glasses.py -p test
```
Note: if the environmental variable CONFIG exists is set to "custom" the configuration file is not read.


## Implement a new SCRAL module
The following picture present the high level architecture of the SCRAL framework.
<img src="https://github.com/MONICA-Project/monica-project.github.io/raw/master/assets/img/SCRAL_architecture.png" alt="SCRAL high level architecture" width="350"/> <br>

To create a new SCRAL module, you can start from the "template_rest" folder and modify it according to your needs.
This folder contains a generic "ready-to-use" SCRAL module that expose a REST <em>resource manager</em> and an MQTT <em>connector</em>.

[... still work in progress ...]
