#!/bin/bash
# Update system packages
apt-get update

# Install dependencies for WeasyPrint and Pillow
apt-get install -y libffi-dev libjpeg-dev zlib1g-dev libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0

# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt
