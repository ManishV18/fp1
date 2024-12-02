import os
import json
from google.cloud import pubsub_v1, storage, firestore
from utils import download_from_bucket, transcribe_audio, summarize_text, upload_to_bucket

# Environment variables
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'dcsc-final-project')
VIDEO_BUCKET = os.getenv('VIDEO_BUCKET', 'dcsc-final-project-bucket-mava6837')
RESULTS_BUCKET = os.getenv('RESULTS_BUCKET', 'dcsc-final-project-results')
FIRESTORE_COLLECTION = 'video_tasks'
SUBSCRIPTION_ID = os.getenv('SUBSCRIPTION_ID', 'video-chunks-sub')

# Initialize Google Cloud clients
firestore_client = firestore.Client()
storage_client = storage.Client()
subscriber = pubsub_v1.SubscriberClient()

def process_message(message):
    """
    Process a single Pub/Sub message:
    - Download video chunk from Cloud Storage.
    - Perform transcription and summarization.
    - Store results in Cloud Storage and Firestore.
    """
    print(f"Received message: {message.data}")
    message_data = json.loads(message.data.decode('utf-8'))

    task_id = message_data['task_id']
    chunk_id = message_data['chunk_id']
    chunk_name = message_data['chunk_name']

    # Local paths
    local_chunk_path = f'tmp/{task_id}/{chunk_name.split("/")[-1]}'
    local_result_path = f'tmp/{task_id}/result_{chunk_id}.txt'

    try:
        # Step 1: Download the video chunk from Cloud Storage
        download_from_bucket(storage_client, VIDEO_BUCKET, chunk_name, local_chunk_path)

        # Step 2: Perform transcription
        transcript = transcribe_audio(local_chunk_path)
        print(f"Transcription completed for chunk {chunk_id}.")

        # Step 3: Perform summarization
        summary = summarize_text(transcript)
        print(f"Summarization completed for chunk {chunk_id}.")

        # Step 4: Save results to a file
        with open(local_result_path, 'w') as result_file:
            result_file.write(f"Transcript:\n{transcript}\n\nSummary:\n{summary}")
        
        # Step 5: Upload results to Cloud Storage
        result_blob_name = f'{task_id}/result_{chunk_id}.txt'
        upload_to_bucket(storage_client, RESULTS_BUCKET, local_result_path, result_blob_name)
        print(f"Results uploaded for chunk {chunk_id}.")

        # Step 6: Update Firestore
        doc_ref = firestore_client.collection(FIRESTORE_COLLECTION).document(task_id)
        doc_ref.update({
            f'chunk_{chunk_id}_status': 'COMPLETED',
            f'chunk_{chunk_id}_summary': summary,
            'processed_chunks': firestore.Increment(1)
        })

        print(f"Firestore updated for chunk {chunk_id}.")
        message.ack()  # Acknowledge the message

    except Exception as e:
        print(f"Error processing chunk {chunk_id}: {e}")
        message.nack()  # Negative acknowledge for retry

def listen_to_pubsub():
    """
    Listen to Pub/Sub messages and process video chunks.
    """
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=process_message)
    print(f"Listening for messages on {subscription_path}...")

    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
        subscriber.close()
        print("Shutting down worker.")

if __name__ == '__main__':
    os.makedirs('tmp', exist_ok=True)
    listen_to_pubsub()
