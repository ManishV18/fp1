from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

import os
import requests
from moviepy.editor import VideoFileClip
import whisper
from transformers import pipeline

def summarize_url(url):
    # 1. Download the video
    video_path = "temp_video.mp4"
    download_video(url, video_path)

    # 2. Extract audio and save as temp_audio.wav
    audio_path = "temp_audio.wav"
    extract_audio(video_path, audio_path)

    # 3. Perform speech-to-text transcription
    transcription = transcribe_audio(audio_path)

    # 4. Summarize the transcription
    summary = summarize_text(transcription)

    # Clean up temporary files
    cleanup_files([video_path, audio_path])

    return summary

def download_video(url, output_path):
    """Download the video from the URL."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
    else:
        raise Exception("Failed to download video.")

def extract_audio(video_path, audio_path):
    """Extract audio from video using MoviePy."""
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, codec="pcm_s16le")

def transcribe_audio(audio_path):
    """Transcribe audio to text using Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def summarize_text(text):
    """Summarize text using Hugging Face Transformers."""
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]["summary_text"]

def cleanup_files(file_list):
    """Remove temporary files."""
    for file in file_list:
        if os.path.exists(file):
            os.remove(file)

# def summarize_url(url):
#     # Simulate URL summarization (replace with your logic)
#     return f"Summary of {url}: This is a simple placeholder summary."

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                summary = summarize_url(url)
            except Exception as e:
                summary = f"Error: {str(e)}"
    return render_template('index.html', summary=summary)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
