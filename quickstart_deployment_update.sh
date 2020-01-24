#!/bin/bash

${REPOSITORY_NAME} = "quickstart"

for d in */; do
  echo "------- Module: ${d} -------"
  echo
  if [ "${d}" = "catalogs/" ]; then
    print "Debug - Skipping folder: ${d}"
    continue
  elif [ "${d}" = "doc/" ]; then
    print "Debug - Skipping folder: ${d}"
    continue
  elif [ "${d}" = "gps_tracker/" ]; then
    print "Debug - Skipping folder: ${d}"
    continue
  elif [ "${d}" = "images/" ]; then
    print "Debug - Skipping folder: ${d}"
    continue
  elif [ "${d}" = "log/" ]; then
    print "Debug - Skipping folder: ${d}"
    continue
  elif [ "${d}" = "microphone/" ]; then
    print "Debug - Skipping folder: ${d}"
    continue
  elif [ "${d}" = "scral_module/" ]; then
    print "Debug - Skipping folder: ${d}"
    continue
  elif [ "${d}" = "scral_ogc/" ]; then
    print "Debug - Skipping folder: ${d}"
    continue
  elif [ "${d}" = "security_fusion_node/" ]; then
    print "Debug - Renaming folder: ${d} in sfn"
    ${MODULE_NAME} = "${REPOSITORY_NAME}:sfn"
  elif [ "${d}" = "smart_glasses/" ]; then
    print "Debug - Renaming folder: ${d} in glasses"
    ${MODULE_NAME} = "${REPOSITORY_NAME}:glasses"
  elif [ "${d}" = "sound_level_meter/" ]; then
    print "Debug - Renaming folder: ${d} in slm"
    ${MODULE_NAME} = "${REPOSITORY_NAME}:slm"
  elif [ "${d}" = "testing/" ]; then
    print "Debug - Skipping folder: ${d}"
    continue
  elif [ "${d}" = "wristband/" ]; then
    print "Debug - Skipping folder: ${d}"
    continue
  else
    print "Debug - Folder: ${d}"
    ${MODULE_NAME} = "${REPOSITORY_NAME}:${d}"
  fi
  ${DOCKER_FILE} = "${d}/Dockerfile"

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

  echo "------- Module ${d} successfully built! -------"
  echo
  echo
done
read -n 1 -s -r -p "Process completed, press any key to continue..."


