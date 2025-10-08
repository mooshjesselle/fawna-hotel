#!/bin/bash
sudo apt-get update
sudo apt-get install -y libjpeg-dev zlib1g-dev libcairo2 libcairo2-dev
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
