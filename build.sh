#!/bin/bash
# build.sh
sudo apt-get update
sudo apt-get install -y libjpeg-dev zlib1g-dev libpangocairo-1.0-0 libpango1.0-dev libcairo2 libcairo2-dev
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
