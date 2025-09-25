import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime
import re
from collections import defaultdict

class GmailJobScanner:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.labels']

        self.service = None
        
    def authenticate(self):
        """Handles Gmail API authentication"""
        creds = None
        
        # Check if token.pickle exists with stored credentials
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        # If credentials are invalid or don't exist, let user login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Save credentials for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def create_search_query(self, start_date):
        """Creates Gmail search query for job applications after start_date"""
        date_str = start_date.strftime('%Y/%m/%d')
        
        # Common job application related terms
        job_terms = [
            'application confirmation',
            'thank you for applying',
            'application received',
            'job application',
            'position at',
            'thank you for your interest',
            'application submitted'
        ]
        
        # Combine terms with OR operator
        terms_query = ' OR '.join(f'"{term}"' for term in job_terms)
        return f'({terms_query}) after:{date_str}'
    
    def extract_company_name(self, subject, body):
        """Attempt to extract company name from email subject and body"""
        # Common patterns in job application emails
        company_patterns = [
            r"position at ([A-Za-z0-9\s&]+)",
            r"application (?:to|for) ([A-Za-z0-9\s&]+)",
            r"([A-Za-z0-9\s&]+) application confirmation",
            r"([A-Za-z0-9\s&]+) careers"
        ]
        
        # First try subject line
        for pattern in company_patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Then try email body
        for pattern in company_patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        return "Unknown Company"
    
    def scan_emails(self, start_date):
        """Scans Gmail for job applications since start_date"""
        if not self.service:
            raise Exception("Not authenticated. Call authenticate() first.")
            
        query = self.create_search_query(start_date)
        applications = defaultdict(list)
        
        try:
            # Get list of messages matching query
            results = self.service.users().messages().list(
                userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            print(f"Found {len(messages)} potential job application emails...")
            
            for message in messages:
                # Get full message details
                msg = self.service.users().messages().get(
                    userId='me', id=message['id'], format='full').execute()
                
                headers = msg['payload']['headers']
                subject = next(h['value'] for h in headers if h['name'] == 'Subject')
                
                # Get email body
                if 'parts' in msg['payload']:
                    body = msg['payload']['parts'][0]['body'].get('data', '')
                else:
                    body = msg['payload']['body'].get('data', '')
                
                # Extract company and date
                company = self.extract_company_name(subject, body)
                date = datetime.fromtimestamp(int(msg['internalDate'])/1000)
                
                applications[company].append({
                    'date': date,
                    'subject': subject
                })
            
            return applications
            
        except Exception as e:
            print(f"Error scanning emails: {str(e)}")
            return None

def main():
    scanner = GmailJobScanner()
    
    try:
        # Authenticate with Gmail API
        print("Authenticating with Gmail...")
        scanner.authenticate()
        
        # Get start date from user
        while True:
            date_str = input("Enter start date (YYYY-MM-DD): ")
            try:
                start_date = datetime.strptime(date_str, '%Y-%m-%d')
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")
        
        # Scan emails
        print("Scanning emails for job applications...")
        applications = scanner.scan_emails(start_date)
        
        if applications:
            print("\nJob Application Summary:")
            print("-----------------------")
            print(f"Total unique companies applied to: {len(applications)}")
            
            for company, apps in applications.items():
                print(f"\n{company}:")
                for app in apps:
                    print(f"  - {app['date'].strftime('%Y-%m-%d')}: {app['subject']}")
        else:
            print("No job applications found in the specified date range.")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()