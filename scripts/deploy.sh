#!/bin/bash

cd ..
rm -rf $(pwd)

git clone https://github.com/the-sashko/text2img.git
git fetch --all --tags
tag=$(git describe --tags `git rev-list --tags --max-count=1`)
git checkout -f $tag
git pull origin $tag

docker-compose build --no-cache
docker-compose up --detach

exit 0
