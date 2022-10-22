#!/bin/bash

currentDir=$(pwd)
scriptDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"

cd "$scriptDir/.." || exit 1

mkdir data
mkdir data/logs
mkdir data/media
touch data/telegram_last_update_id.txt

cp -r install/config config

chmod 775 -R data
chmod 775 -R config

virtualenv env

source env/bin/activate

pip3 install --upgrade pip
pip3 install -r requirements.txt

deactivate

cd "$currentDir" || exit 1

exit 0
