import os
import uuid
from google.cloud import firestore, pubsub_v1, storage
from utils import split_video, upload_to_bucket, publish_message

# Environment variables
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'dcsc-final-project')
VIDEO_BUCKET = os.getenv('VIDEO_BUCKET', 'dcsc-final-project-bucket-mava6837')
PUBSUB_TOPIC = os.getenv('WORKER_TOPIC', 'video-chunks-tasks')

# Firestore collection name
FIRESTORE_COLLECTION = 'video_tasks'

# Initialize Google Cloud clients
firestore_client = firestore.Client()
publisher = pubsub_v1.PublisherClient()
storage_client = storage.Client()

def process_task(task_id, video_url):
    """
    Process a video task:
    - Split video into chunks
    - Upload chunks to Cloud Storage
    - Publish tasks for workers
    - Track progress in Firestore
    """
    print(f"Processing task {task_id} for video: {video_url}")

    # Step 1: Split video into chunks
    chunks_dir = f'tmp/{task_id}/chunks'
    os.makedirs(chunks_dir, exist_ok=True)
    chunk_paths = split_video(video_url, chunks_dir)
    print(f"Video split into {len(chunk_paths)} chunks.")

    # Step 2: Upload chunks to Cloud Storage
    for i, chunk_path in enumerate(chunk_paths):
        chunk_name = f'{task_id}/chunk_{i}.mp4'
        upload_to_bucket(storage_client, VIDEO_BUCKET, chunk_path, chunk_name)
        print(f"Uploaded {chunk_name} to Cloud Storage.")

    # Step 3: Publish tasks for workers
    for i, chunk_path in enumerate(chunk_paths):
        chunk_name = f'{task_id}/chunk_{i}.mp4'
        message_data = {
            'task_id': task_id,
            'chunk_id': i,
            'chunk_name': chunk_name,
        }
        publish_message(publisher, PUBSUB_TOPIC, message_data)
        print(f"Published task for chunk {i}.")

    # Step 4: Update Firestore with task progress
    firestore_client.collection(FIRESTORE_COLLECTION).document(task_id).update({
        'status': 'IN_PROGRESS',
        'num_chunks': len(chunk_paths),
        'processed_chunks': 0
    })
    print(f"Task {task_id} marked as IN_PROGRESS.")

if __name__ == '__main__':
    print("Master node initialized.")
