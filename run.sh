#!/bin/bash

# startup
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

# create venv if does not exist
function setup_venv {
    env_name="env"

    # make sure we're not in another venv
    if [ "$VIRTUAL_ENV" != "" ] && [ "$VIRTUAL_ENV" != "$DIR/$env_name" ]; then
        echo 'Unexpected venv set...'
        exit 1
    fi

    # create venv if not exists
    if [ ! -d "$env_name" ]; then
        echo "Creating venv..."
        pip_version=$(cat requirements.txt | grep "^pip==")
        python -m venv $env_name && source env/bin/activate && pip install $pip_version
        if [ $? -ne 0 ]; then
            echo 'Error during venv create...'
            if [ "$VIRTUAL_ENV" != "" ]; then
                deactivate
            fi
            exit 1
        fi
    fi

    # activate venv
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source env/bin/activate
    fi
}

# verify requirements are installed
function package_diff {
    diff <(cat requirements.txt | grep -v "^pip==") <(pip list --not-required --disable-pip-version-check --format freeze | grep -v "^pip==" | grep -v "^setuptools")
}

# setup proper requirements strictly
function setup_packages {
    echo 'Setting up packages...'
    pdiff=$(package_diff)
    if [ "$pdiff" != "" ]; then
        echo 'Installing packages...'
        pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo 'Error during package install...'
            exit 1
        else
            pdiff=$(package_diff)
            if [ "$pdiff" != "" ]; then
                echo 'Package mis-match after install...'
                echo $pdiff
                exit 1
            fi
        fi
    fi
}

# main execution loop
function main {

    TEAM=$1
    REFRESH=$2

    # make sure team is set
    if [ -z "$TEAM" ]; then
        echo 'Team must be set as $1'
        exit 1
    fi

    # flush terminal
    clear

    # create and/or activate venv
    setup_venv

    # install and verify requirements
    setup_packages

    # flush terminal
    clear

    # run script (optionally watch)
    if [ -z "$REFRESH" ]; then
        python run.py query --team $TEAM
    else
        watch -d -n $REFRESH python run.py query --team $TEAM
    fi
}
main "$@"

# cleanup
if [[ "$VIRTUAL_ENV" != "" ]]; then
    deactivate
fi
cd - > /dev/null
