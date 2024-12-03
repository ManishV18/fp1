#!/bin/bash

# Update package list and install dependencies
apt-get update
apt-get install -y python3-pip git

# Upgrade pip
pip3 install --upgrade pip

# Install project-specific dependencies for the master node
pip3 install google-cloud-storage google-cloud-pubsub flask whisper transformers

# Define repository details
GITHUB_USERNAME="ManishV18"
REPO_NAME="fp1"
TOKEN="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"  # Replace with your actual token
PROJECT_REPO="https://${TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
PROJECT_DIR="/home/ubuntu/${REPO_NAME}"

# Clone the project repository
if [ ! -d "$PROJECT_DIR" ]; then
  git clone "$PROJECT_REPO" "$PROJECT_DIR"
else
  echo "Repository already exists at $PROJECT_DIR."
fi

# Navigate to the master directory and install Python dependencies
cd "$PROJECT_DIR/master" || exit 1
if [ -f "requirements.txt" ]; then
  pip3 install -r requirements.txt
else
  echo "No requirements.txt found in $PROJECT_DIR/master."
fi

# Run the master script
if [ -f "master.py" ]; then
  python3 master.py
else
  echo "No master.py script found in $PROJECT_DIR/master."
fi
