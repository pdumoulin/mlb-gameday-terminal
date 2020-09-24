#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TEAM=$1
REFRESH=$2

# make sure team is set
if [ -z "$TEAM" ]; then
    echo 'Team must be set as $1'
    exit 1
fi

# flush terminal
clear

# go to project dir
cd $DIR

# create venv if does not exist
if [ ! -d "env" ]; then
    PIP_VERSION=$(cat requirements.txt | grep "^pip==")
    python -m venv env && source env/bin/activate && pip install $PIP_VERSION
    if [ $? -ne 0 ]; then
        if [[ "$VIRTUAL_ENV" != "" ]]; then
            deactivate
        fi
        exit 1
    fi
fi

# activate venv
if [[ "$VIRTUAL_ENV" == "" ]]; then
    source env/bin/activate
fi

# install packages if package mis-match
PACKAGE_DIFF=$(diff <(cat requirements.txt | grep -v "^pip==") <(pip list --not-required --disable-pip-version-check --format freeze | grep -v "^pip==" | grep -v "^setuptools"))
if [ "$PACKAGE_DIFF" != "" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo $PACKAGE_DIFF
        exit 1
    fi
fi

# flush terminal
clear

# run script (optionally watch)
if [ -z "$REFRESH" ]; then
    python run.py query --team $TEAM
else
    watch -d -n $REFRESH python run.py query --team $TEAM
fi

# deactivate venv
deactivate

# go back to origin dir
cd - > /dev/null
