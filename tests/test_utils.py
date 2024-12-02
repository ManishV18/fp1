import pytest
from unittest.mock import patch
from utils import utils

def test_validate_youtube_url_valid():
    valid_url = "https://www.youtube.com/watch?v=KdgQvgE3ji4"
    
    with patch("utils.utils.YoutubeValidator.is_valid") as mock_validator:
        mock_validator.return_value = True
        
        result = utils.validate_youtube_url(valid_url)
        assert result is True

def test_validate_youtube_url_invalid():
    invalid_url = "https://www.youtube.com/watch?v=invalidurl"
    
    with patch("utils.utils.YoutubeValidator.is_valid") as mock_validator:
        mock_validator.return_value = False
        
        result = utils.validate_youtube_url(invalid_url)
        assert result is False

def test_download_video():
    video_url = "https://www.youtube.com/watch?v=KdgQvgE3ji4"
    
    with patch("utils.utils.YoutubeDownloader.download") as mock_download:
        mock_download.return_value = "video.mp4"
        
        result = utils.download_video(video_url)
        assert result == "video.mp4"

def test_update_firestore():
    task_id = "task_1"
    summary = "Summarized text."
    
    with patch("utils.utils.FirestoreClient.update_task_status") as mock_update:
        mock_update.return_value = True
        
        result = utils.update_firestore(task_id, summary)
        assert result is True
