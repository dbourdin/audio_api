#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

poetry run pytest "$SCRIPT_DIR"/../tests/ --cov="audio_api" --cov-report="term-missing"
