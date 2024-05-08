import base64
import json
import re
from collections import defaultdict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
import os
from dotenv import load_dotenv
load_dotenv()

import sys

def append_json_to_file(data, file_path):
    """
    Append JSON data to a JSON file. If the file does not exist, create a new file.

    Parameters:
        data (dict): JSON data to append.
        file_path (str): The path to the JSON file.
    """
    # Check if the file exists
    if os.path.exists(file_path):
        # Read the existing data
        with open(file_path, 'r', encoding='utf-8') as file:
            # Load existing data into a dictionary
            file_data = json.load(file)
            # Append new data
            if isinstance(file_data, list):
                file_data.append(data)
            elif isinstance(file_data, dict):
                file_data.update(data)
    else:
        # Create a new list with the new data if file does not exist
        file_data = [data]

    # Write the updated data back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(file_data, file, indent=4)

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
    results = service.users().messages().list(userId='me', q="after:2024/05/05").execute()
    messages = results.get('messages', [])

    emails = defaultdict(list)
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        if 'labelIds' in msg:
            if 'CATEGORY_PERSONAL' in msg['labelIds'] and 'SENT' not in msg['labelIds']:
                payload = msg['payload']
                subject = ''
                if 'headers' in payload:
                    for header in payload['headers']:
                        if header['name'] == 'Subject':
                            subject = header['value']
                            break
                else:
                    continue
                append_json_to_file(payload, './out.json')
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body'].get('data')
                            emails[subject].append((base64.urlsafe_b64decode(data).decode('utf-8')))
                            break
                        elif 'parts' in part:
                            for part2 in part['parts']:
                                if part2['mimeType'] == 'text/plain':
                                    data = part2['body'].get('data')
                                    emails[subject].append((base64.urlsafe_b64decode(data).decode('utf-8')))
                                    break
                elif 'mimeType' in payload:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data')
                        emails[subject].append((base64.urlsafe_b64decode(data).decode('utf-8')))
                
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
        'messages': [{"role": "user", "content": 'Summarize the following email concisely in one to two sentences, leave key details in: ' + text}],
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

# Function to save an array of text to a markdown file
def save_to_markdown(text_array, file_path):
    # Open the file in write mode
    with open(file_path, 'w', encoding='utf-8') as file:
        # Write each string in the array to the file on a new line
         for index, subject in enumerate(text_array, start=1):
            file.write(f"# {index}. {subject}:\n\n")
            for text in text_array[subject]:
                file.write(f"{text}\n\n")

def main():
    service = get_gmail_service()
    emails = fetch_emails(service)
    summaries = defaultdict(list)
    try:
        for subject in emails:
            for text in emails[subject]:
                summary = summarize_text(text)['choices'][0]['message']['content']
            #summary = summarize(email, 10)
            
                summaries[subject].append(summary)
    except Exception as e:
        print('Error parsing', e)
    save_to_markdown(summaries, './out.md')


if __name__ == '__main__':
    main()
