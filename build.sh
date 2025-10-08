#!/bin/bash
# Install system packages needed by WeasyPrint
apt-get update
apt-get install -y libffi-dev libjpeg-dev zlib1g-dev libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0
# Upgrade pip & setuptools
pip install --upgrade pip setuptools wheel
# Install Python packages
pip install -r requirements.txt
