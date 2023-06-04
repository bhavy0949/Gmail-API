import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import psycopg2
from dateutil.parser import parse

conn = psycopg2.connect(
    database="test1",
    user="bhavy",
    password="bhagup12",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def fetch_emails():
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=20).execute()
    messages = results.get('messages', [])
    if not messages:
        print('No messages found.')
    else:
        print('Messages:')
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = msg['payload']['headers']
            email_id = message['id']
            for values in email_data:
                name = values['name']
                if name == 'From':
                    from_value = values['value']
                elif name == 'Subject':
                    subject_value = values['value']
                elif name == 'Date':
                    date_received_value = values['value']
            # Parsing Different Timestamp
            datetime_str = date_received_value
            parsed_datetime = parse(datetime_str)
            cur.execute("INSERT INTO email (unique_id, email_from, subject, date_received) VALUES (%s, %s, %s, %s)",
                (email_id, from_value, subject_value, parsed_datetime))
            conn.commit()
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            print("Unique Id:", email_id)
            print("From:", from_value)
            print("Subject:", subject_value)
            print("Date Received:", date_received_value)
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        cur.close()
        conn.close()

if __name__ == '__main__':
    fetch_emails()
