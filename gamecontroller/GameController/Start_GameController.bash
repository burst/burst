#!/bin/bash

set -eu

read -p 'Enter team number for blue: ' readBlue
read -p 'Enter team number for red: ' readRed

declare -i blue=readBlue
declare -i red=readRed
declare broadcast=""


echo "Starting GameController, team ${blue} plays in blue and team ${red} plays in red"
if [ -n "${1:-""}" ]; then
  broadcast="-broadcast ${1}"
  echo "Broadcasting into network ${1}"
fi

java -jar GameController.jar -numplayers 3 ${broadcast} ${blue} ${red} 
