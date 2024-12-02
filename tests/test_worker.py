import pytest
from unittest.mock import patch
from worker.worker import WorkerNode

def test_transcribe_video():
    worker_node = WorkerNode()
    video_chunk = "chunk1.mp4"
    
    # Mock transcription function
    with patch("worker.worker.Transcriber.transcribe") as mock_transcribe:
        mock_transcribe.return_value = "This is a transcribed text."
        
        result = worker_node.transcribe_video(video_chunk)
        assert result == "This is a transcribed text."

def test_summarize_text():
    worker_node = WorkerNode()
    transcribed_text = "This is a long transcribed text that needs summarization."
    
    # Mock summarization function
    with patch("worker.worker.Summarizer.summarize") as mock_summarize:
        mock_summarize.return_value = "Summarized text."
        
        result = worker_node.summarize_text(transcribed_text)
        assert result == "Summarized text."

def test_update_firestore():
    worker_node = WorkerNode()
    task_id = "task_1"
    summary = "Summarized text."

    # Mock Firestore update function
    with patch("worker.worker.FirestoreClient.update_task_status") as mock_update:
        mock_update.return_value = True
        
        result = worker_node.update_firestore(task_id, summary)
        assert result is True
