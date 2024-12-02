import os
import subprocess
from google.cloud import storage, pubsub_v1

def split_video(video_url, output_dir, chunk_duration=60):
    """
    Split a video into chunks of specified duration.
    Args:
        video_url: The path or URL to the video.
        output_dir: The directory to save the chunks.
        chunk_duration: Duration of each chunk in seconds.
    Returns:
        List of paths to the video chunks.
    """
    chunk_paths = []
    base_name = os.path.basename(video_url).split('.')[0]

    command = [
        'ffmpeg', '-i', video_url,
        '-c', 'copy', '-f', 'segment', '-segment_time', str(chunk_duration),
        '-reset_timestamps', '1', f'{output_dir}/{base_name}_chunk_%03d.mp4'
    ]

    subprocess.run(command, check=True)

    for file_name in os.listdir(output_dir):
        if file_name.endswith('.mp4'):
            chunk_paths.append(os.path.join(output_dir, file_name))

    return chunk_paths

def upload_to_bucket(storage_client, bucket_name, source_file_path, destination_blob_name):
    """
    Upload a file to a Cloud Storage bucket.
    """
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_path)
    print(f"Uploaded {source_file_path} to {destination_blob_name}.")

def publish_message(publisher, topic, message_data):
    """
    Publish a message to a Pub/Sub topic.
    """
    topic_path = publisher.topic_path(os.getenv('GOOGLE_CLOUD_PROJECT'), topic)
    publisher.publish(topic_path, data=str(message_data).encode('utf-8'))
    print(f"Published message to topic {topic}: {message_data}")
