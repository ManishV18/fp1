from flask import Flask, request, jsonify
from google.cloud import pubsub_v1, firestore
import re
import os

# Initialize Flask app
app = Flask(__name__)

# Initialize Google Cloud Clients
project_id = "dcsc-final-project-443518"
topic_id = "video-processing-tasks"
firestore_client = firestore.Client()

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# Validate YouTube URL
def is_valid_youtube_url(url):
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=|embed/|v/)?[A-Za-z0-9_-]{11}'
    return re.match(youtube_regex, url)

@app.route('/submit', methods=['POST'])
def submit_video():
    """
    Endpoint to submit a YouTube URL for processing.
    """
    data = request.get_json()
    youtube_url = data.get('youtube_url')

    if not youtube_url or not is_valid_youtube_url(youtube_url):
        return jsonify({"error": "Invalid YouTube URL"}), 400

    # Publish the task to Pub/Sub
    message = {"youtube_url": youtube_url}
    publisher.publish(topic_path, data=str(message).encode("utf-8"))
    
    # Save initial task status in Firestore
    doc_ref = firestore_client.collection("video-tasks").document()
    doc_ref.set({
        "url": youtube_url,
        "status": "submitted"
    })
    return jsonify({"message": "Task submitted successfully", "task_id": doc_ref.id}), 200

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    """
    Endpoint to check the processing status of a task.
    """
    doc_ref = firestore_client.collection("video-tasks").document(task_id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"task_id": task_id, "status": doc.to_dict().get("status")}), 200

@app.route('/summary/<task_id>', methods=['GET'])
def get_summary(task_id):
    """
    Endpoint to retrieve the summary of a processed video.
    """
    doc_ref = firestore_client.collection("video-tasks").document(task_id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"error": "Task not found"}), 404

    task_data = doc.to_dict()
    if task_data.get("status") != "completed":
        return jsonify({"error": "Task not yet completed"}), 400

    summary = task_data.get("summary", "Summary not available.")
    return jsonify({"task_id": task_id, "summary": summary}), 200

if __name__ == '__main__':
    # Run the Flask app locally
    app.run(host='0.0.0.0', port=8080)
