#!/bin/bash

if [[ $# -ne 2 ]]; then
	echo "Error: wrong usage!"
	echo "Usage: $0 <module_name> <docker_file>"
	read -n 1 -s -r -p "Process completed, press any key to continue..."
	exit 255
fi

MODULE_NAME=$1
DOCKER_FILE=$2
SECONDS=0
echo
echo " ----- STEP 1: Building docker image ----- "
docker build --no-cache=true --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" -t "${MODULE_NAME}" -f "${DOCKER_FILE}" .
RESULT=$?
echo
echo
if [[ ${RESULT} -ne 0 ]]; then
    echo "Docker image not correctly built!"
    read -n 1 -s -r -p "Press any key to continue..."
    exit 1
fi
echo " ----- STEP 2: Tagging image ----- "
REPOSITORY_NAME="scral/$MODULE_NAME"
echo "Target repository: $REPOSITORY_NAME"
docker tag "${MODULE_NAME}" "${REPOSITORY_NAME}"
RESULT=$?
echo
echo
if [[ ${RESULT} -ne 0 ]]; then
    echo "Docker image not correctly tagged!"
    read -n 1 -s -r -p "Press any key to continue..."
    exit 2
fi
echo " ----- STEP 3: Pushing image on repository ----- "
docker push "${REPOSITORY_NAME}"
RESULT=$?
echo
echo
if [[ ${RESULT} -ne 0 ]]; then
    echo "Docker image not correctly pushed on docker hub!"
    read -n 1 -s -r -p "Press any key to continue..."
    exit 3
fi

duration=$SECONDS
echo "Process completed: $(date)"
echo "Docker image built and uploaded in $((${duration} / 60)) minutes and $((${duration} % 60)) seconds."
read -n 1 -s -r -p "Press any key to continue..."
