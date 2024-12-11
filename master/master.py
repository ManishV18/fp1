import os
import tempfile
import subprocess
from pytube import YouTube
from google.cloud import pubsub_v1, firestore, storage
from transformers import pipeline
import json
import time

# Huggingface Transformer Pipeline for Summarization
summarizer = pipeline("summarization")

# Google Cloud Setup
project_id = "dcsc-final-project-443518"
topic_id = "video-processing-tasks"
bucket_name = "dcsc-final-project-bucket-mava6837"
firestore_client = firestore.Client()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)
storage_client = storage.Client()

# Download video from YouTube
def download_video(youtube_url):
    yt = YouTube(youtube_url)
    video_stream = yt.streams.get_highest_resolution()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    video_stream.download(output_path=os.path.dirname(temp_file.name), filename=os.path.basename(temp_file.name))
    return temp_file.name

# Split video into smaller chunks
def split_video(video_path):
    chunk_dir = tempfile.mkdtemp()
    chunk_paths = []
    chunk_duration = 300  # 5 minutes in seconds

    cmd = f"ffmpeg -i {video_path} -c copy -map 0 -segment_time {chunk_duration} -f segment {chunk_dir}/chunk_%03d.mp4"
    subprocess.run(cmd, shell=True, check=True)

    for file in os.listdir(chunk_dir):
        if file.endswith(".mp4"):
            chunk_paths.append(os.path.join(chunk_dir, file))

    return chunk_paths

# Upload video chunk to Google Cloud Storage
def upload_to_gcs(chunk_path):
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(os.path.basename(chunk_path))
    blob.upload_from_filename(chunk_path)
    return f"gs://{bucket_name}/{os.path.basename(chunk_path)}"

# Retrieve transcriptions from GCS
def retrieve_transcriptions(task_id, total_chunks):
    bucket = storage_client.get_bucket(bucket_name)
    transcriptions = []

    for i in range(total_chunks):
        blob_name = f"{task_id}_chunk_{i}_transcription.json"
        blob = bucket.blob(blob_name)
        if blob.exists():
            transcription = json.loads(blob.download_as_text())
            transcriptions.append(transcription['text'])
        else:
            print(f"Transcription file {blob_name} not found in GCS.")

    return transcriptions

# Summarize aggregated transcriptions
def summarize_text(text):
    summary = summarizer(text, max_length=200, min_length=100, do_sample=False)
    return summary[0]['summary_text']

# Orchestration of video processing
def process_video(youtube_url, task_id):
    try:
        # Step 1: Download the video
        video_path = download_video(youtube_url)
        print(f"Video downloaded to {video_path}")

        # Step 2: Split the video into chunks
        chunk_paths = split_video(video_path)
        print(f"Video split into {len(chunk_paths)} chunks")

        # Step 3: Upload chunks to Cloud Storage and publish tasks
        gcs_paths = []
        for i, chunk_path in enumerate(chunk_paths):
            gcs_path = upload_to_gcs(chunk_path)
            gcs_paths.append(gcs_path)

            message = {"task_id": task_id, "gcs_path": gcs_path, "chunk_id": i}
            publisher.publish(topic_path, data=json.dumps(message).encode("utf-8"))
            print(f"Task for chunk {i} published to Pub/Sub.")

        # Step 4: Update task status in Firestore
        doc_ref = firestore_client.collection("video-tasks").document(task_id)
        doc_ref.set({"status": "processing", "chunks": len(chunk_paths)})

        # Step 5: Wait for all worker nodes to finish processing
        while True:
            doc = doc_ref.get().to_dict()
            if doc.get("completed_chunks", 0) == len(chunk_paths):
                print("All chunks processed.")
                break
            print("Waiting for worker nodes to complete processing...")
            time.sleep(2)

        # Step 6: Retrieve transcriptions from GCS
        transcriptions = retrieve_transcriptions(task_id, len(chunk_paths))

        # Step 7: Aggregate transcriptions
        aggregated_text = " ".join(transcriptions)

        # Step 8: Summarize aggregated transcriptions
        summary = summarize_text(aggregated_text)
        print(f"Generated Summary: {summary}")

        # Step 9: Upload summary to GCS
        summary_blob = storage_client.get_bucket(bucket_name).blob(f"{task_id}_summary.txt")
        summary_blob.upload_from_string(summary)

        # Step 10: Update Firestore with completion status
        doc_ref.update({"status": "completed", "summary": summary})

    except Exception as e:
        print(f"Error in processing video: {e}")
        doc_ref = firestore_client.collection("video-tasks").document(task_id)
        doc_ref.update({"status": "failed", "error": str(e)})
