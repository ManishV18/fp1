from flask import Flask, render_template, request, jsonify
from transformers import pipeline
from pytube import YouTube
import os
#from moviepy.editor import AudioFileClip

import time



app = Flask(__name__)

def download_audio_from_youtube(url, output_path):
    # """Download audio from a YouTube video."""
    # yt = YouTube(url)
    
    # # Extract only the audio stream
    # audio_stream = yt.streams.filter(only_audio=True).first()
    
    # # Download the audio
    # out_file = audio_stream.download(output_path=output_path)
    
    # # Rename the file to .mp3
    # base, ext = os.path.splitext(out_file)
    # new_file = base + '.mp3'
    # os.rename(out_file, new_file)
    
    # return new_file

    return "Done"
    
def summarize_text(text):
    # """Summarize text using Hugging Face Transformers."""
    # summarizer = pipeline("summarization", model="google/pegasus-xsum")
    # tokenizer_kwargs = {'truncation': True, 'max_length': 512}
    # summary = summarizer(text, min_length=30, do_sample=False, **tokenizer_kwargs)
    # return summary[0]['summary_text']

    output = "This is the final summary."

    return output
    
@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                # # Step 1: Download audio from YouTube
                # audio_path = "temp_audio.mp3"
                # audio_file = download_audio_from_youtube(url, ".")

                # # Step 2: Extract text from audio using Hugging Face's pipeline
                # model = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-large-960h-lv60-self")
                # transcription = model(audio_file)['text']

                # # Step 3: Summarize the transcription
                # summary = summarize_text(transcription)

                time.sleep(5)

                summary = "This is the final summary."

                
                # Cleanup
                #os.remove(audio_file)

            except Exception as e:
                summary = f"Error: {str(e)}"
    return render_template('index.html', summary=summary)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
