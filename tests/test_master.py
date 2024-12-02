import pytest
from unittest.mock import patch
from master.master import MasterNode

def test_download_video():
    master_node = MasterNode()
    video_url = "https://www.youtube.com/watch?v=KdgQvgE3ji4"

    # Mock the YouTube download function
    with patch("master.master.YoutubeDownloader.download") as mock_download:
        mock_download.return_value = "video.mp4"
        
        result = master_node.download_video(video_url)
        assert result == "video.mp4"

def test_split_video():
    master_node = MasterNode()
    video_path = "video.mp4"

    # Mock the splitting function
    with patch("master.master.VideoSplitter.split") as mock_split:
        mock_split.return_value = ["chunk1.mp4", "chunk2.mp4"]
        
        result = master_node.split_video(video_path)
        assert result == ["chunk1.mp4", "chunk2.mp4"]

def test_publish_task_to_pubsub():
    master_node = MasterNode()
    task_data = {"chunk": "chunk1.mp4"}

    # Mock Pub/Sub publishing
    with patch("master.master.PubSubClient.publish") as mock_publish:
        mock_publish.return_value = "message_id_123"
        
        result = master_node.publish_task(task_data)
        assert result == "message_id_123"
