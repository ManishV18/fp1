import os
import tempfile
import subprocess
from pytube import YouTube
from google.cloud import storage, firestore

# Google Cloud Storage and Firestore Setup
storage_client = storage.Client()
firestore_client = firestore.Client()
bucket_name = "dcsc-final-project-bucket-mava6837"

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
