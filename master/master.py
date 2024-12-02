import os
import tempfile
import time
import subprocess
from google.cloud import pubsub_v1, firestore, storage
from utils import download_video, split_video, upload_to_gcs

# Google Cloud Setup
project_id = "dcsc-final-project-443518"
topic_id = "video-processing-tasks"
bucket_name = "dcsc-final-project-bucket-mava6837"
firestore_client = firestore.Client()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)
storage_client = storage.Client()

# Orchestration of video processing
def process_video(youtube_url, task_id):
    """
    Orchestrates video processing: Download, Split, Upload, Publish.
    """
    try:
        # Step 1: Download the video
        video_path = download_video(youtube_url)
        print(f"Video downloaded to {video_path}")

        # Step 2: Split the video into chunks
        chunk_paths = split_video(video_path)
        print(f"Video split into {len(chunk_paths)} chunks")

        # Step 3: Upload chunks to Cloud Storage
        gcs_paths = []
        for chunk_path in chunk_paths:
            gcs_path = upload_to_gcs(chunk_path)
            gcs_paths.append(gcs_path)
            print(f"Chunk uploaded to GCS: {gcs_path}")

        # Step 4: Publish tasks to Pub/Sub for worker nodes to process each chunk
        for i, gcs_path in enumerate(gcs_paths):
            message = {"task_id": task_id, "gcs_path": gcs_path, "chunk_id": i}
            publisher.publish(topic_path, data=str(message).encode("utf-8"))
            print(f"Task for chunk {i} published to Pub/Sub.")

        # Step 5: Update task status in Firestore
        doc_ref = firestore_client.collection("video-tasks").document(task_id)
        doc_ref.update({
            "status": "processing",
            "chunks": len(chunk_paths)
        })
        print("Task status updated to 'processing' in Firestore.")
    
    except Exception as e:
        print(f"Error in processing video: {e}")
        # Step 6: Handle failure, update Firestore task status to failed
        doc_ref = firestore_client.collection("video-tasks").document(task_id)
        doc_ref.update({
            "status": "failed",
            "error": str(e)
        })
        print("Task status updated to 'failed' in Firestore.")

if __name__ == "__main__":
    # Example usage
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example YouTube URL
    task_id = "task-12345"  # Example task ID
    process_video(youtube_url, task_id)
