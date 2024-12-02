#!/bin/bash

# Set up environment variables
PROJECT_ID="dcsc-final-project"
ZONE="us-central1-a"
VM_NAME_PREFIX="worker-node-vm"
IMAGE_FAMILY="debian-10"
IMAGE_PROJECT="debian-cloud"
VM_MACHINE_TYPE="n1-standard-1"
WORKER_COUNT=3
STARTUP_SCRIPT="startup-worker.sh"

# Deploy multiple worker nodes
for i in $(seq 1 $WORKER_COUNT)
do
    VM_NAME="${VM_NAME_PREFIX}-$i"
    
    # Create Google Compute Engine instance (Worker Node)
    gcloud compute instances create $VM_NAME \
        --project=$PROJECT_ID \
        --zone=$ZONE \
        --image-family=$IMAGE_FAMILY \
        --image-project=$IMAGE_PROJECT \
        --machine-type=$VM_MACHINE_TYPE \
        --metadata=startup-script-url=gs://$PROJECT_ID/startup-scripts/$STARTUP_SCRIPT \
        --tags=http-server,https-server
    
    echo "Worker Node $i VM deployed successfully."

done

# Optionally SSH into one of the created instances for manual checks
gcloud compute ssh ${VM_NAME_PREFIX}-1 --zone=$ZONE
