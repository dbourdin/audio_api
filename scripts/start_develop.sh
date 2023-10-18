#!/bin/bash

# Starts the stack defined in docker/docker-compose.yml and creates a docker
# network if needed

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

docker-compose -f "$SCRIPT_DIR"/../docker/docker-compose.yml up -d
