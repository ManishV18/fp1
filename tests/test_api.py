import pytest
from app import app
from unittest.mock import patch

# Test the validation of YouTube URL
def test_validate_youtube_url_valid():
    valid_url = "https://www.youtube.com/watch?v=KdgQvgE3ji4"
    
    # Assume we have a mock for the actual YouTube URL validation
    with patch("app.utils.validate_youtube_url") as mock_validate_url:
        mock_validate_url.return_value = True
        
        response = app.test_client().post('/process-video', json={"url": valid_url})
        assert response.status_code == 200
        assert b"Video processing started" in response.data

def test_validate_youtube_url_invalid():
    invalid_url = "https://www.youtube.com/watch?v=invalidurl"
    
    with patch("app.utils.validate_youtube_url") as mock_validate_url:
        mock_validate_url.return_value = False
        
        response = app.test_client().post('/process-video', json={"url": invalid_url})
        assert response.status_code == 400
        assert b"Invalid YouTube URL" in response.data

# Test task status retrieval
def test_get_task_status():
    task_id = "task_1"
    
    with patch("app.utils.get_task_status") as mock_get_status:
        mock_get_status.return_value = "completed"
        
        response = app.test_client().get(f'/task-status/{task_id}')
        assert response.status_code == 200
        assert b"completed" in response.data
