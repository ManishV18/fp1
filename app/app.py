from flask import Flask, request, jsonify, render_template, redirect, url_for
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

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Home route to render the input form and handle submissions.
    """
    if request.method == 'POST':
        youtube_url = request.form.get('url')
        if not youtube_url or not is_valid_youtube_url(youtube_url):
            return render_template("index.html", error="Invalid YouTube URL")

        # Publish the task to Pub/Sub
        message = {"youtube_url": youtube_url}
        publisher.publish(topic_path, data=str(message).encode("utf-8"))
        
        # Save initial task status in Firestore
        doc_ref = firestore_client.collection("video-tasks").document()
        doc_ref.set({
            "url": youtube_url,
            "status": "submitted"
        })

        return redirect(url_for('check_status', task_id=doc_ref.id))
    
    return render_template("index.html")

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    """
    Endpoint to check the processing status of a task.
    """
    doc_ref = firestore_client.collection("video-tasks").document(task_id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"error": "Task not found"}), 404

    task_data = doc.to_dict()
    status = task_data.get("status", "unknown")
    return render_template("status.html", task_id=task_id, status=status)

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
        return render_template("status.html", task_id=task_id, status=task_data.get("status", "unknown"))

    summary = task_data.get("summary", "Summary not available.")
    return render_template("summary.html", task_id=task_id, summary=summary)

if __name__ == '__main__':
    # Run the Flask app locally on port 5000
    app.run(host='0.0.0.0', port=5000)
