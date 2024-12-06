from flask import Flask, render_template, request, jsonify
from transformers import pipeline
from youtube_dl import YoutubeDL
import os
from moviepy.editor import AudioFileClip

app = Flask(__name__)

def download_audio_from_youtube(url, output_path):
    """Download audio from a YouTube video."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': output_path
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def summarize_text(text):
    """Summarize text using Hugging Face Transformers."""
    summarizer = pipeline("summarization", model="google/pegasus-xsum")
    tokenizer_kwargs = {'truncation': True, 'max_length': 512}
    summary = summarizer(text, min_length=30, do_sample=False, **tokenizer_kwargs)
    return summary[0]['summary_text']

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                # Step 1: Download audio from YouTube
                audio_path = "audio.wav"
                download_audio_from_youtube(url, "temp_video.%(ext)s")
                
                # Step 2: Extract text from audio using Hugging Face's pipeline
                model = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-large-960h-lv60-self")
                transcription = model(audio_path, chunk_length_s=10)['text']

                # Step 3: Summarize the transcription
                summary = summarize_text(transcription)
                
                # Cleanup
                os.remove(audio_path)

            except Exception as e:
                summary = f"Error: {str(e)}"
    return render_template('index.html', summary=summary)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
