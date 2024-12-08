#!/bin/bash

# Set up environment variables
PROJECT_ID="dcsc-final-project-443518"
ZONE="us-central1-a"
VM_NAME="master-node-vm"
IMAGE_FAMILY="debian-11"
IMAGE_PROJECT="debian-cloud"
VM_MACHINE_TYPE="n1-standard-1"
STARTUP_SCRIPT="startup-master.sh"

# Create Google Compute Engine instance (Master Node)
gcloud compute instances create $VM_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --machine-type=$VM_MACHINE_TYPE \
    --metadata=startup-script-url=gs://$PROJECT_ID/startup-scripts/$STARTUP_SCRIPT \
    --tags=http-server,https-server

# SSH into the created instance for manual configurations or checks
#gcloud compute ssh $VM_NAME --zone=$ZONE

echo "Master Node VM deployed successfully."
