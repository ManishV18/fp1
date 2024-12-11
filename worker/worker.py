import os
import tempfile
from google.cloud import storage, pubsub_v1
import whisper
from transformers import pipeline

# Google Cloud Setup
project_id = "dcsc-final-project-443518"
subscription_id = "video-processing-tasks-subscription"
bucket_name = "dcsc-final-project-bucket-mava6837"
storage_client = storage.Client()

# Initialize Pub/Sub Subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# Initialize Whisper Model for Transcription
whisper_model = whisper.load_model("base")

# Initialize Huggingface Transformer Pipeline for Summarization
summarizer = pipeline("summarization")

# Transcribe video chunk using Whisper
def transcribe_video(video_path):
    """
    Transcribes a video chunk using Whisper.
    """
    # Load video with Whisper
    audio = whisper_model.transcribe(video_path)
    return audio["text"]

# Summarize the transcription using Huggingface Transformers
def summarize_text(text):
    """
    Summarizes the transcribed text using a Transformer model.
    """
    summary = summarizer(text, max_length=200, min_length=50, do_sample=False)
    return summary[0]["summary_text"]

# Upload the summary to Cloud Storage
def upload_summary_to_gcs(summary, task_id, chunk_id):
    """
    Uploads the summary text to Cloud Storage.
    """
    summary_filename = f"summary_{task_id}_chunk_{chunk_id}.txt"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(summary_filename)

    # Upload the summary text to Cloud Storage
    blob.upload_from_string(summary)

    # Return the GCS path for the uploaded summary
    return f"gs://{bucket_name}/{summary_filename}"

# Download a video chunk from Google Cloud Storage
def download_chunk_from_gcs(gcs_path):
    """
    Downloads a chunk from Cloud Storage to a temporary local file.
    """
    blob = storage_client.bucket(bucket_name).blob(gcs_path)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    blob.download_to_filename(temp_file.name)
    return temp_file.name

# Callback for handling incoming tasks from Pub/Sub
def callback(message):
    try:
        task_data = eval(message.data.decode('utf-8'))  # Parse the incoming message
        task_id = task_data['task_id']
        gcs_path = task_data['gcs_path']
        chunk_id = task_data['chunk_id']

        print(f"Processing task {task_id}, chunk {chunk_id} from GCS path: {gcs_path}")

        # Step 1: Download video chunk from Cloud Storage
        video_chunk_path = download_chunk_from_gcs(gcs_path)
        print(f"Downloaded chunk {chunk_id} to {video_chunk_path}")

        # Step 2: Transcribe the video chunk into text
        transcription = transcribe_video(video_chunk_path)
        print(f"Transcription completed for chunk {chunk_id}")

        # Step 3: Summarize the transcription using NLP
        summary = summarize_text(transcription)
        print(f"Summary generated for chunk {chunk_id}")

        # Step 4: Upload the summary to Cloud Storage
        summary_path = upload_summary_to_gcs(summary, task_id, chunk_id)
        print(f"Summary uploaded to GCS: {summary_path}")

        # Acknowledge the message so it won't be processed again
        message.ack()

    except Exception as e:
        print(f"Error processing task: {e}")
        message.nack()

# Listen for tasks from Pub/Sub
def listen_for_tasks():
    print(f"Listening for tasks on {subscription_path}...")
    subscriber.subscribe(subscription_path, callback=callback)

if __name__ == "__main__":
    listen_for_tasks()
