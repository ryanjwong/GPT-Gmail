import base64
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
import os
from dotenv import load_dotenv
load_dotenv()

import sys

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Returns a Gmail API service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=3000)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def fetch_emails(service):
    """Fetches emails from the Gmail API."""
    # Call the Gmail API to fetch INBOX
    results = service.users().messages().list(userId='me', q="after:2024/05/06", maxResults="25").execute()
    messages = results.get('messages', [])

    emails = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        if 'INBOX' in msg['labelIds']:
            payload = msg['payload']
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data')
                        emails.append(base64.urlsafe_b64decode(data).decode('utf-8'))
                        break
            elif 'mimeType' in payload:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    emails.append(base64.urlsafe_b64decode(data).decode('utf-8'))
    return emails

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
        'messages': [{"role": "user", "content": 'Summarize the following email concisely in one sentence: ' + text}],
    }
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    return response.json()

def summarize(transcript, percent=50):
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
    print(response.json())
    return summarized_transcript

def main():
    service = get_gmail_service()
    emails = fetch_emails(service)
    summaries = []
    try:
        for email in emails:
            summary = summarize(email, 50)
            summaries.append(summary)
    except Exception as e:
        print('Error parsing', e)
    # for summary in summaries:
    #     print(summary + '\n')


if __name__ == '__main__':
    main()
