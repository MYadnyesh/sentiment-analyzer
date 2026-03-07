from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from models import Message
import os.path
from datetime import datetime
from typing import List
import base64

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/chat.messages.readonly'
]

class GoogleAuthenticator:
    """Handles OAuth authentication for Google APIs"""

    @staticmethod
    def get_credentials():
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return creds


class GmailFetcher:
    """Fetches emails from Gmail API"""

    def __init__(self):
        creds = GoogleAuthenticator.get_credentials()
        self.service = build('gmail', 'v1', credentials=creds)

    def fetch_by_keyword(self, keyword: str, max_results: int = 100) -> List[Message]:
        """Fetch emails containing keyword"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=keyword,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            email_messages = []
            for msg in messages:
                email_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                email_messages.append(self._parse_email(email_data))

            return email_messages

        except Exception as e:
            print(f"Error fetching Gmail messages: {e}")
            return []

    def _parse_email(self, email_data) -> Message:
        """Parse Gmail API response into Message object"""
        headers = email_data['payload']['headers']
        subject = next((h['value']
                       for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value']
                      for h in headers if h['name'] == 'From'), 'Unknown')

        # Extract body
        body = ""
        if 'parts' in email_data['payload']:
            for part in email_data['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
                        break
        else:
            if 'data' in email_data['payload']['body']:
                body = base64.urlsafe_b64decode(
                    email_data['payload']['body']['data']).decode('utf-8')

        timestamp = datetime.fromtimestamp(
            int(email_data['internalDate']) / 1000)

        return Message(
            id=email_data['id'],
            text=body,
            sender=sender,
            source='gmail',
            timestamp=timestamp,
            subject=subject
        )


class ChatFetcher:
    """Fetches messages from Google Chat API"""

    def __init__(self):
        creds = GoogleAuthenticator.get_credentials()
        self.service = build('chat', 'v1', credentials=creds)

    def fetch_by_keyword(self, keyword: str, max_results: int = 100) -> List[Message]:
        """Fetch chat messages containing keyword"""
        try:
            # Note: Google Chat API has limitations for personal accounts
            spaces = self.service.spaces().list().execute()

            chat_messages = []
            for space in spaces.get('spaces', [])[:10]:
                messages = self.service.spaces().messages().list(
                    parent=space['name'],
                    pageSize=min(max_results, 100)
                ).execute()

                for msg in messages.get('messages', []):
                    if keyword.lower() in msg.get('text', '').lower():
                        chat_messages.append(self._parse_message(msg))

            return chat_messages

        except Exception as e:
            print(f"Error fetching Chat messages: {e}")
            print("Note: Google Chat API may have limited access for personal accounts")
            return []

    def _parse_message(self, msg_data) -> Message:
        """Parse Chat API response into Message object"""
        return Message(
            id=msg_data['name'],
            text=msg_data.get('text', ''),
            sender=msg_data.get('sender', {}).get('displayName', 'Unknown'),
            source='chat',
            timestamp=datetime.fromisoformat(
                msg_data['createTime'].replace('Z', '+00:00'))
        )
