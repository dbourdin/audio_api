#!/bin/bash

poetry run pytest --cov="audio_api" --cov-report="term-missing"
