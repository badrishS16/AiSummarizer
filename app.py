from flask import Flask, jsonify, request #Flask web framework
from flask_cors import CORS  
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi  #read youtube transcripts
import fitz  #PyMuPDF to read PDF files
from dotenv import load_dotenv # load environment variables
import os # operating system functionalities (to use the env variables)

load_dotenv() # Load environment variables from .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY")) # Initialize Groq client with API key

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])  # Enable CORS for specified origin

def get_summary(prompt):
    response = client.chat.completions.create(
        model="groq-1.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content

@app.route('/summarize/text', methods=['POST'])
def summarize_text():
    data = request.get_json() # Get JSON data from request(frontend)
    text = data.get('text', '') # Extract 'text' field from JSON data
    summary = get_summary(f"Summarize the following text:\n\n{text}")
    return jsonify({'summary': summary})
@app.route('/summarize/pdf', methods=['POST'])
def summarize_pdf():
    file = request.files['file']  # Get the uploaded file from the request
    doc = fitz.open(stream=file.read(), filetype="pdf")  # Open the PDF file using PyMuPDF
    text = ""
    for page in doc:
        text += page.get_text()  # Extract text from each page and concatenate
    summary = get_summary(f"Summarize the following PDF content:\n\n{text}")
    return jsonify({'summary': summary})
@app.route('/summarize/youtube', methods=['POST'])
def summarize_youtube():
    data = request.get_json()
    url = data.get('youtubeURL', '')
    video_id = url.split("v=")[-1]  # Extract video ID from URL
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    text = " ".join([item['text'] for item in transcript_list])  # Combine transcript segments
    summary = get_summary(f"Summarize the following YouTube transcript:\n\n{text}")
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)