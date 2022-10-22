#!/bin/bash

scriptDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"

cd "$scriptDir/.." || exit 1

currentDir=$(pwd)

cd ..

rm -rf currentDir

git clone https://github.com/the-sashko/text2img.git text2img

cd text2img

git fetch --all --tags
tag=$(git describe --tags `git rev-list --tags --max-count=1`)
git checkout -f "$tag"
git pull origin "$tag"

sudo docker-compose up -d

exit 0
