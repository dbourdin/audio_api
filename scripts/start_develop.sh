#!/bin/bash

# Starts the stack defined in docker/docker-compose.yml and creates a docker
# network if needed

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

function wait_for_db {
    echo "Waiting db startup..."
    until docker-compose -f "$SCRIPT_DIR"/../docker/docker-compose.yml exec db pg_isready ; do sleep 1 ; done
    echo "DB is ready!"
}

docker-compose -f "$SCRIPT_DIR"/../docker/docker-compose.yml up -d
wait_for_db
echo "Creating 'uuid-ossp' extension"
docker-compose -f "$SCRIPT_DIR"/../docker/docker-compose.yml exec db psql --user postgres -d audio_api -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'

 echo "Applying migrations"
 docker-compose -f "$SCRIPT_DIR"/../docker/docker-compose.yml exec audio-api poetry run manage migrate
