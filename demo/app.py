from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

app = Flask(__name__)

def get_transcript(video_id, language='en'):
    """Fetch transcript of a specific language using YouTube Transcript API."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        # Join the transcript segments into a single string
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

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
                # Extract video ID from the YouTube URL
                video_id = url.split("v=")[-1].split("&")[0]
                
                # Step 1: Fetch transcript in English
                transcript = get_transcript(video_id, language='en')
                if "Error" in transcript:
                    raise Exception(transcript)
                
                # Step 2: Summarize the transcript
                summary = summarize_text(transcript)

            except Exception as e:
                summary = f"Error: {str(e)}"
    return render_template('index.html', summary=summary)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
