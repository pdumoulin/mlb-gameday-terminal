#!/bin/bash

# startup and global vars
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ENV_NAME="env"
cd $DIR

# cleanup and exit script
function cleanup {
    if [ "$VIRTUAL_ENV" != "" ] && [ "$VIRTUAL_ENV" == "$DIR/$ENV_NAME" ]; then
        deactivate > /dev/null 2>&1
    fi
    cd - > /dev/null
    exit $1
}

# create venv if does not exist
function setup_venv {
    echo 'Setting up venv...'

    # make sure we're not in another venv
    if [ "$VIRTUAL_ENV" != "" ]; then
        echo 'Error venv already activated...'
        echo $VIRTUAL_ENV
        cleanup 1
    fi

    # create venv if not exists
    if [ ! -d "$ENV_NAME" ]; then
        echo "Creating venv..."
        pip_version=$(cat requirements.txt | grep "^pip==")
        python -m venv $ENV_NAME && source env/bin/activate && pip install $pip_version
        if [ $? -ne 0 ]; then
            echo 'Error during venv create...'
            cleanup 1
        fi
    fi

    # activate venv
    source env/bin/activate
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
            cleanup 1
        else
            pdiff=$(package_diff)
            if [ "$pdiff" != "" ]; then
                echo 'Package mis-match after install...'
                echo $pdiff
                echo 'Removing venv...'
                rm -R $ENV_NAME
                echo 'Try again'
                cleanup 1
            fi
        fi
    fi
}

function hard_clear {
    clear && printf '\e[3J'
}

# main execution loop
function main {

    TEAM=$1
    REFRESH=$2

    # make sure team is set
    if [ -z "$TEAM" ]; then
        echo 'Team must be set as $1'
        cleanup 1
    fi

    # flush terminal
    hard_clear

    # create and/or activate venv
    setup_venv

    # install and verify requirements
    setup_packages

    # flush terminal
    hard_clear

    # run script (optionally watch)
    if [ -z "$REFRESH" ]; then
        python run.py query --team $TEAM
    else
        watch -d -n $REFRESH python run.py query --team $TEAM
    fi
}
main "$@"
cleanup 0
