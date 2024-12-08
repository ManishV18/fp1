Here’s the updated `README.md` file reflecting the changes and including the necessary commands to upload and set up the startup scripts:

```markdown
# Video Processing with Google Cloud Platform

This project implements a distributed video processing pipeline using Google Cloud Platform (GCP) services, including Pub/Sub, Firestore, and Cloud Storage. It features a Flask-based web interface, master-worker architecture for task orchestration, and automated resource setup.

---

## Project Structure

```
├── app
│   ├── app.py               # Flask application for user interaction
│   ├── requirements.txt     # Python dependencies for the app
│   ├── static
│   │   └── style.css        # CSS for the web interface
│   └── templates
│       └── index.html       # HTML template for the app
├── cloud_setup
│   ├── deploy_master.sh     # Deployment script for the master node
│   ├── deploy_worker.sh     # Deployment script for worker nodes
│   ├── setup_resources.py   # Python script to set up GCP resources
│   ├── startup-master.sh    # Startup script for the master node
│   └── startup-worker.sh    # Startup script for worker nodes
├── master
│   ├── master.py            # Main orchestrator script for video processing
│   ├── requirements.txt     # Python dependencies for the master node
│   └── utils.py             # Helper functions for the master node
└── worker
    ├── requirements.txt     # Python dependencies for the worker nodes
    ├── utils.py             # Helper functions for the worker nodes
    └── worker.py            # Worker script for processing video chunks
```

---

## Prerequisites

1. **Python**: Ensure Python 3.x is installed.
2. **Google Cloud SDK**: Install and authenticate using:
   ```bash
   gcloud auth login
   gcloud config set project <PROJECT_ID>
   ```
3. **Service Account Key**: Set up authentication:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   ```
4. **Install Required Python Libraries**:
   Each folder (`app`, `master`, `worker`) contains a `requirements.txt` file. Install dependencies as required.

---

## How to Run

### 1. Set Up Google Cloud Resources
Run the `setup_resources.py` script to create Cloud Storage buckets, Pub/Sub topics, and Firestore collections:
```bash
cd cloud_setup
python3 setup_resources.py
```

### 2. Upload Startup Scripts to Cloud Storage
Upload the `startup-master.sh` and `startup-worker.sh` scripts to your GCP bucket:

```bash
PROJECT_ID="your-project-id"
BUCKET_NAME="your-bucket-name"

# Upload startup scripts
gsutil cp startup-master.sh gs://$BUCKET_NAME/startup-scripts/
gsutil cp startup-worker.sh gs://$BUCKET_NAME/startup-scripts/
```

Ensure both scripts are stored in the Cloud Storage bucket under the `startup-scripts/` directory.

### 3. Deploy Master and Worker Nodes
Use the deployment scripts to set up the master and worker nodes. These scripts include references to the startup scripts uploaded to Cloud Storage:

```bash
cd cloud_setup

# Deploy Master Node
./deploy_master.sh

# Deploy Worker Node
./deploy_worker.sh
```

The deployment scripts pass the following metadata to GCP instances to automatically execute the startup scripts:
```bash
--metadata=startup-script-url=gs://$PROJECT_ID/startup-scripts/$STARTUP_SCRIPT
```

### 4. Run the Flask Application
Start the Flask app for user interaction:
```bash
cd app
pip install -r requirements.txt
python3 app.py
```
Access the app at `http://127.0.0.1:5000`.

---

## Key Features

- **Distributed Video Processing**: Splits large videos into chunks, processes them in parallel, and generates summaries.
- **Google Cloud Integration**: Utilizes Cloud Storage, Pub/Sub, and Firestore for scalable resource management.
- **Web Interface**: Simple and intuitive Flask-based web application for user interaction.
- **Automated Deployment**: Scripts for setting up and deploying GCP resources and services.

---

## Additional Notes

- **Configurations**: Update project-specific configurations in the scripts:
  - `project_id`
  - `bucket_name`
  - `topic_id`
  - `subscription_id`
- **Logs**: Check for logs to debug issues. Logs are printed to the console during execution.
- **Scalability**: Add more worker nodes as needed by deploying additional instances with `deploy_worker.sh`.

---
