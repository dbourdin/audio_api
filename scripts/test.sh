#!/bin/bash

# Runs the test suite inside a container

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

function wait_for_db {
    echo "Waiting db startup..."
    until docker-compose -f "$SCRIPT_DIR"/../docker/docker-compose.yml exec db pg_isready ; do sleep 1 ; done
    echo "DB is ready!"
}

# Ensure all containers are down
docker-compose -f "$SCRIPT_DIR"/../docker/docker-compose.yml down

# Start environment and wait for DB
docker-compose -f "$SCRIPT_DIR"/../docker/docker-compose.yml up -d audio-api
wait_for_db

# Run tests
docker-compose -f "$SCRIPT_DIR"/../docker/docker-compose.yml exec audio-api pytest --cov="audio_api" $@

# Tear down environment
docker-compose -f "$SCRIPT_DIR"/../docker/docker-compose.yml down
