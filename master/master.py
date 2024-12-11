import os
import tempfile
import subprocess
from pytube import YouTube
from google.cloud import pubsub_v1, firestore, storage

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
    """
    Downloads the video using pytube.
    """
    yt = YouTube(youtube_url)
    video_stream = yt.streams.get_highest_resolution()

    # Save the video to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    video_stream.download(output_path=temp_file.name)
    return temp_file.name

# Split video into smaller chunks
def split_video(video_path):
    """
    Splits the video into smaller chunks.
    """
    # Step 1: Create temporary directory to store video chunks
    chunk_dir = tempfile.mkdtemp()

    # Step 2: Use ffmpeg to split the video into chunks (e.g., 10-minute segments)
    chunk_paths = []
    chunk_duration = 600  # 10 minutes

    # Use ffmpeg to split video
    cmd = f"ffmpeg -i {video_path} -c copy -map 0 -segment_time {chunk_duration} -f segment {chunk_dir}/chunk_%03d.mp4"
    subprocess.run(cmd, shell=True)

    # Collect the paths of the chunks
    for file in os.listdir(chunk_dir):
        if file.endswith(".mp4"):
            chunk_paths.append(os.path.join(chunk_dir, file))

    return chunk_paths

# Upload video chunk to Google Cloud Storage
def upload_to_gcs(chunk_path):
    """
    Uploads the video chunk to Google Cloud Storage.
    """
    # Create a Cloud Storage bucket object
    bucket = storage_client.get_bucket(bucket_name)

    # Create a blob in the GCS bucket for the chunk
    blob = bucket.blob(os.path.basename(chunk_path))
    blob.upload_from_filename(chunk_path)

    # Return the GCS path for the uploaded chunk
    gcs_path = f"gs://{bucket_name}/{os.path.basename(chunk_path)}"
    return gcs_path

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

