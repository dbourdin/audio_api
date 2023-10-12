#!/bin/bash

# Runs the pre-commit hook in the whole repo

function run_hook(){
    pre-commit run --all-files
}

echo "Running pre-commit"
run_hook
