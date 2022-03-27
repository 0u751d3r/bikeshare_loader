#!/bin/bash

python3 -m venv ./bs_venv
source ./bs_venv/bin/activate
pip3 install -r src/requirements.txt

echo "Running unit tests..."
pytest src/tests