#!/bin/bash
DIR="./venv"
if [ ! -d "$DIR" ]; then
  # Create env if it does not exist
  echo "Installing new virtual env at ${DIR}..."
  python3.10 -m venv ./venv

  # Install requirements
  source ./venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi