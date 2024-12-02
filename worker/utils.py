import os
import tempfile
from google.cloud import storage
import whisper
from transformers import pipeline

# Google Cloud Storage Setup
storage_client = storage.Client()
bucket_name = "dcsc-final-project-bucket-mava6837"

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
