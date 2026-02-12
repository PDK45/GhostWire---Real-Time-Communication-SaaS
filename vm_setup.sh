#!/bin/bash
# GhostWire VM Setup Script

echo ">> INITIALIZING GHOSTWIRE PROTOCOL..."
echo ">> UPDATING SYSTEM..."
sudo apt update && sudo apt upgrade -y

echo ">> INSTALLING DEPENDENCIES..."
sudo apt install -y python3 python3-pip git

echo ">> CLONING REPOSITORY..."
if [ -d "GhostWire---Real-Time-Communication-SaaS" ]; then
    echo "Repo exists, pulling latest..."
    cd GhostWire---Real-Time-Communication-SaaS
    git pull
else
    git clone https://github.com/PDK45/GhostWire---Real-Time-Communication-SaaS.git
    cd GhostWire---Real-Time-Communication-SaaS
fi

echo ">> INSTALLING PYTHON LIBRARIES..."
pip3 install -r requirements.txt --break-system-packages
pip3 install pyngrok --break-system-packages

echo ">> SETUP COMPLETE."
echo ">> TO LAUNCH SATELLITE UPLINK: python3 deploy.py"
