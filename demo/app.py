from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

def summarize_url(url):
    # Simulate URL summarization (replace with your logic)
    return f"Summary of {url}: This is a simple placeholder summary."

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
