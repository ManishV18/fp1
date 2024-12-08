#!/bin/bash

# Update package list and install dependencies
apt-get update
apt-get install -y python3-pip git

# Upgrade pip
pip3 install --upgrade pip

# Install project-specific dependencies for the master node
pip3 install google-cloud-storage google-cloud-pubsub flask whisper transformers

# Clone the project repository
PROJECT_REPO="https://github.com/ManishV18/dcsc_final_project.git"
PROJECT_DIR="/home/ubuntu/fp1"
git clone "$PROJECT_REPO" "$PROJECT_DIR"

# Navigate to the master directory and install Python dependencies
cd "$PROJECT_DIR/master"
pip3 install -r requirements.txt

# Run the master script
python3 master.py
