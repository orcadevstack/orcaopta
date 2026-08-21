#!/bin/bash
echo "Installing Orcaopta environment..."

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

mkdir -p models
mkdir -p data

echo "Environment setup complete."
