#!/bin/bash

currentDir=$(pwd)
scriptDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"

cd "$scriptDir/.." || exit 1

sudo docker build -t iamsashko/text2img .

sudo docker login

sudo docker push iamsashko/text2img:latest

cd "$currentDir" || exit 1

exit 0
