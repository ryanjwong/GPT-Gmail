import os
import requests
import json

def summarize_text(text):
    """Sends text to the GPT API for summarization."""
    openai_api_key = os.getenv('OPENAI_KEY')

    api_url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': 'Bearer ' + openai_api_key,
        'Content-Type': 'application/json',
    }
    data = {
        'model' : 'gpt-3.5-turbo',
        'messages': [{"role": "user", "content": 'Summarize the following email concisely in one to two sentences, leave key details in and preserve names especially: ' + text}],
    }
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    return response.json()

def summarize(transcript, percent):
    if percent == 100:
        return transcript

    # Summarize transcript using rapidapi
    api_url = "https://text-analysis12.p.rapidapi.com/summarize-text/api/v1.1"

    payload = {
        "language": "english",
        "summary_percent": percent,
        "text": transcript
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": os.getenv('RAPIDAPI_KEY'),
        "X-RapidAPI-Host": "text-analysis12.p.rapidapi.com"
    }

    response = requests.post(api_url, json=payload, headers=headers)
    if not response.json()['ok']:
        raise ValueError(response.json()['msg'])

    summarized_transcript = response.json()['summary']
    return summarized_transcript