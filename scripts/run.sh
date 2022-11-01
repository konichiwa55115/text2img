#!/bin/bash

currentDir=$(pwd)
scriptDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"

cd "$scriptDir/.." || exit 1

source env/bin/activate

while :
do
    python3 src/run.py
done

deactivate

cd "$currentDir" || exit 1

exit 0
