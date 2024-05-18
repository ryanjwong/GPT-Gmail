from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import base64
from collections import defaultdict
from datetime import date

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service(profile_name):
    """Shows basic usage of the Gmail API.
    Returns a Gmail API service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    path = os.getenv('PROFILES_PATH')
    profile_path = path + '/' + profile_name + '.json'
    if os.path.exists(profile_path):
        creds = Credentials.from_authorized_user_file(profile_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=3000)
        # Save the credentials for the next run
        with open(profile_path, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def fetch_emails(service):
    """Fetches emails from the Gmail API."""
    # Call the Gmail API to fetch INBOX
    today = date.today()
    d1 = today.strftime("%Y/%m/%d")

    results = service.users().messages().list(userId='me', q='after:' + d1).execute()
    messages = results.get('messages', [])

    emails = defaultdict(list)
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        if 'labelIds' in msg:
            if 'INBOX' in msg['labelIds'] and 'CATEGORY_PROMOTIONS' not in msg['labelIds'] and 'CATEGORY_SOCIAL' not in msg['labelIds']:
                payload = msg['payload']
                subject = ''
                if 'headers' in payload:
                    for header in payload['headers']:
                        if header['name'] == 'Subject':
                            subject = header['value']
                            break
                else:
                    continue
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
                    if payload['mimeType'] == 'text/plain':
                        data = payload['body'].get('data')
                        emails[subject].append((base64.urlsafe_b64decode(data).decode('utf-8')))
    return emails