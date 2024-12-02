from flask import Flask, request, jsonify
from google.cloud import firestore, pubsub_v1, storage
import os
import uuid

# Initialize Flask app
app = Flask(__name__)

# Initialize Google Cloud clients
firestore_client = firestore.Client()
publisher = pubsub_v1.PublisherClient()
storage_client = storage.Client()

# Environment variables
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'dcsc-final-project')
VIDEO_BUCKET = os.getenv('VIDEO_BUCKET', 'dcsc-final-project-bucket-mava6837')
PUBSUB_TOPIC = os.getenv('PUBSUB_TOPIC', 'video-tasks')

# Firestore collection name
FIRESTORE_COLLECTION = 'video_tasks'

# Routes
@app.route('/upload', methods=['POST'])
def upload_video():
    """
    Upload video URL and pass it to the master node via Pub/Sub.
    """
    data = request.json
    if not data or 'video_url' not in data:
        return jsonify({'error': 'video_url is required'}), 400

    video_url = data['video_url']
    task_id = str(uuid.uuid4())  # Generate a unique task ID

    # Save metadata to Firestore
    firestore_client.collection(FIRESTORE_COLLECTION).document(task_id).set({
        'video_url': video_url,
        'status': 'PENDING'
    })

    # Publish task to Pub/Sub
    message_data = {'task_id': task_id, 'video_url': video_url}
    publisher.publish(f'projects/{PROJECT_ID}/topics/{PUBSUB_TOPIC}', data=str(message_data).encode('utf-8'))

    return jsonify({'message': 'Task created', 'task_id': task_id}), 200

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    """
    Check the processing status of a video task.
    """
    doc = firestore_client.collection(FIRESTORE_COLLECTION).document(task_id).get()
    if not doc.exists:
        return jsonify({'error': 'Task not found'}), 404

    data = doc.to_dict()
    return jsonify({'task_id': task_id, 'status': data.get('status'), 'details': data}), 200

@app.route('/summary/<task_id>', methods=['GET'])
def retrieve_summary(task_id):
    """
    Retrieve the processed summary of the video task.
    """
    doc = firestore_client.collection(FIRESTORE_COLLECTION).document(task_id).get()
    if not doc.exists:
        return jsonify({'error': 'Task not found'}), 404

    data = doc.to_dict()
    if data.get('status') != 'COMPLETED':
        return jsonify({'error': 'Task not completed yet'}), 400

    summary_url = data.get('summary_url')
    if not summary_url:
        return jsonify({'error': 'Summary URL not available'}), 404

    return jsonify({'task_id': task_id, 'summary_url': summary_url}), 200

# Main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
