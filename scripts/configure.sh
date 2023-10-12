#!/bin/bash

# Sets up development environment
#   - Install pre-commit hook
#   - Install local python dependencies

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

function running_in_virtualenv() {
    if [[ "$VIRTUAL_ENV" != "" ]]
    then
        return 0
    else
        return 1
    fi
}

function setup_hook() {
    pip install pre-commit
    pre-commit install
}

function install_deps() {
    pip install -r $SCRIPT_DIR/requirements.txt;
}

if running_in_virtualenv
then
    setup_hook;
    install_deps;
else
    echo "Script not running in a virtualenv, exiting...";
fi
