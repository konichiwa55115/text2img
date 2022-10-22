#!/bin/bash

currentDir=$(pwd)
scriptDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"

cd "$scriptDir/.." || exit 1

if [ ! -d "data" ]
then
    mkdir data
fi

if [ ! -d "data/logs" ]
then
    mkdir data/logs
fi

if [ ! -d "data/media" ]
then
    mkdir data/media
fi

if [ ! -f "data/telegram_last_update_id.txt" ]
then
    touch data/telegram_last_update_id.txt
fi

if [ ! -d "config" ]
then
    cp -r install/config config
fi

chmod 775 -R data
chmod 775 -R config

if [ ! -d "env" ]
then
    rm -rf env
fi

virtualenv env

source env/bin/activate

pip3 install --upgrade pip
pip3 install -r requirements.txt

deactivate

cd "$currentDir" || exit 1
