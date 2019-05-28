#!/bin/bash

if [[ $# -ne 2 ]]; then
	echo "Error! Usage: $0 <module_name> <docker_file>"
	exit 1
fi

MODULE_NAME=$1
DOCKER_FILE=$2

echo " ----- STEP 1: Building docker image ----- "
docker build -t ${MODULE_NAME} -f ${DOCKER_FILE} .
echo
echo
echo " ----- STEP 2: Tagging image ----- "
REPOSITORY_NAME="scral/$MODULE_NAME"
echo "Target repository: $REPOSITORY_NAME"
docker tag ${MODULE_NAME} ${REPOSITORY_NAME}
echo
echo
echo " ----- STEP 3: Pushing image on repository ----- "
docker push ${REPOSITORY_NAME}
echo
echo
read -n 1 -s -r -p "Process completed, press any key to continue."
