#!/bin/bash

currentDir=$(pwd)
scriptDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"

cd "$scriptDir/.." || exit 1

git fetch --all --tags
tag=$(git describe --tags `git rev-list --tags --max-count=1`)

git checkout -f "$tag"
git pull origin "$tag"

sudo docker build -t iamsashko/text2img:"$tag" .

sudo docker login

sudo docker push iamsashko/text2img:"$tag"
sudo docker push iamsashko/text2img:latest

cd "$currentDir" || exit 1

exit 0
