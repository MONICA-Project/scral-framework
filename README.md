# SCRAL - Smart City Resource Adaptation Layer

[![License](https://img.shields.io/badge/license-Apache%202-green)](https://opensource.org/licenses/BSD-2-Clause)
![Language: Python3](https://img.shields.io/badge/language-python3-blue.svg)

![Logo](images/SCRAL-Logo-V1.1.png)

<!-- Short description of the project -->

The Smart City Resource Adaptation Layer (*SCRAL*) is a framework used in MONICA european project to manage several
different kinds of IoT devices.


## Getting Started
<!-- Instruction to make the project up and running. -->

SCRAL could be started as a Python 3 application but we suggest you to start using it downloading one of the *quickstart*
Docker containers that you can find on this [Docker Hub repository](https://hub.docker.com/r/monicaproject/scral).
SCRAL was tested mainly with Python 3.6 so it is suggested to install at least that version.

### How to use SCRAL
```
        _____ __________  ___    __                                     
       / ___// ____/ __ \/   |  / /                                     
       \__ \/ /   / /_/ / /| | / /                                      
      ___/ / /___/ _, _/ ___ |/ /___                                    
     /____/\____/_/ |_/_/  |_/_____/   Smart City Resource Adaptation Layer

     (c) 2017-2020, LINKS Foundation
     developed by Jacopo Foglietti & Luca Mannella


usage: SCRAL [-h] -p PILOT

arguments:
  -h, --help
        show this help message and exit
  -p PILOT, --pilot PILOT
        the name of the configuration folder

example: start_module.py -p MOVIDA  
```

Have a look to config folder to find more details about SCRAL configuration parameter.

### Examples
ex 1
```
./scral.py -h
```

## Deployment
<!-- Deployment/Installation instructions. If this is software library, change this section to "Usage" and give usage examples -->

To deploy a new SCRAL image, modify to your needs one of the dockerfile already contained in each module folder.

### Docker
To start using SCRAL is strongly suggest to take a Docker image *"as is"* and to configure properly the environmental variables. <br>
An update list of the configurable variable is available in the [Docker hub repository](https://hub.docker.com/r/monicaproject/scral).

## Development

### Prerequisite
SCRAL requires:
 - Python 3 (Python 3.6 or above suggested)
 - Frameworks:
    - [Flask](http://flask.palletsprojects.com)
    - [CherryPy](https://cherrypy.org/)
 - Python packages:
    - [Eclipse Paho](https://pypi.org/project/paho-mqtt/1.5) 1.5
    - [Flask](https://pypi.org/project/Flask/1.0.2) 1.1.1
    - [CherryPy](https://pypi.org/project/CherryPy/18.1.0) 18.5.0
    - [arrow](https://pypi.org/project/arrow/0.14.2) 0.14.2
    - [requests](https://pypi.org/project/requests/2.22) 2.22.0
    - [configparser](https://pypi.org/project/configparser/3.7.1) 3.7.1
 - Docker (to be containerized or to be used "as is")

#### Python packages
To install the required python3 packages:
```
pip3 install -r requirements.txt
```

### Test
SCRAL does not have at the moment a test suite.<br>
Feel free to contribute if you want! :)

### Build
SCRAL is mainly written in Python 3 (that is an interpreted language) and so it could just be started without building anything.

## Contributing
Contributions are welcome. 

Please fork, make your changes, and submit a pull request. For major changes, please open an issue first and discuss it with the other authors.

## Licensing
**Copyright © 2017-2020 [Jacopo Foglietti](http://ismb.it/jacopo.foglietti/)
and [Luca Mannella](http://ismb.it/luca.mannella) for [LINKS Foundation](http://linksfoundation.com/).**

*SCRAL* is licensed under the Apache 2 License (click [here](https://opensource.org/licenses/Apache-2.0) for details).

## Affiliation
![MONICA](https://github.com/MONICA-Project/template/raw/master/monica.png)  
This work is supported by the European Commission through the [MONICA H2020 PROJECT](https://www.monica-project.eu) under grant agreement No 732350.
