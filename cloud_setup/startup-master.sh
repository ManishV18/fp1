#!/bin/bash

# Update package list and install dependencies
apt-get update
apt-get install -y python3-pip git

# Upgrade pip
pip3 install --upgrade pip

# Clone the project repository
PROJECT_REPO="https://github.com/ManishV18/cu-csci-4253-datacenter-fall-2024 / finalproject-final-project-team-89.git"

git clone "$PROJECT_REPO"

# Navigate to the master directory and install Python dependencies
cd "master"
pip3 install -r requirements.txt

# Run the master script
python3 master.py
