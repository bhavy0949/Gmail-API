import json
import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import psycopg2
import datetime
import requests

conn = psycopg2.connect(
    database="test1",
    user="bhavy",
    password="bhagup12",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
USER_ID = 'me'

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


def filter_emails(filter_from, filter_subject, days):
    sql = "SELECT * FROM email WHERE TRUE"
    if filter_from!='':
        sql += f" AND email_from LIKE '%{filter_from}%'"
    if filter_subject!='':
        sql += f" AND subject LIKE '%{filter_subject}%'"
    if days:
        sql += f" AND date_received >= '{days}'"

    cur.execute(sql)
    results = cur.fetchall()
    return results


def is_email_read(headers, USER_ID, email_id):
    response = requests.get(
        f'https://www.googleapis.com/gmail/v1/users/{USER_ID}/messages/{email_id}',
        headers=headers
    )
    response.raise_for_status()
    label_ids = response.json()['labelIds']
    return 'UNREAD' not in label_ids


def mark_email(headers, USER_ID, email_id, mark_action):
    response = None
    email_read_or_not = is_email_read(headers, USER_ID, email_id)
    REQUEST_BODY = {
        'addLabelIds': [],
        'removeLabelIds': []
}
    if mark_action:
        REQUEST_BODY['removeLabelIds'] = ['UNREAD']
        if not email_read_or_not:
            response = requests.post(
                f'https://www.googleapis.com/gmail/v1/users/{USER_ID}/messages/{email_id}/modify',
                json=REQUEST_BODY,
                headers=headers
            )
            response.raise_for_status()
        return response if response is None else response.json()

    REQUEST_BODY['addLabelIds'] = ['UNREAD']
    if email_read_or_not:
        response = requests.post(
            f'https://www.googleapis.com/gmail/v1/users/{USER_ID}/messages/{email_id}/modify',
            json=REQUEST_BODY,
            headers=headers
        )
        response.raise_for_status()
    return response if response is None else response.json()


def move_message(headers, USER_ID, email_id, destination):
	valid_destinations = ['INBOX', 'SPAM', 'TRASH']
	if destination not in valid_destinations:
		raise ValueError('Invalid destination')
	REQUEST_BODY = {
        'addLabelIds': [destination],
        'removeLabelIds': []
}
	response = requests.post(
        f'https://www.googleapis.com/gmail/v1/users/{USER_ID}/messages/{email_id}/modify',
        json=REQUEST_BODY,
        headers=headers
    )
	response.raise_for_status()
	return response.json()


def main():
    with open('/Users/bhavy/Downloads/data.json') as json_file:
        data = json.load(json_file)

    #Rules
    filter_days = data.get("filter_date_received", "")
    filter_from = data.get("filter_from", "")
    filter_subject = data.get("filter_subject", "")

    # Actions
    mark_action = data["mark_action"]
    if mark_action == "READ":
        mark_action = True
    elif mark_action == "UNREAD":
        mark_action = False
    else:
        raise ValueError('Invalid destination')

    destination = data["destination"]


    days = datetime.datetime.now().date() - datetime.timedelta(days=filter_days)
    
    filtered_emails = filter_emails(filter_from, filter_subject, days)

    cur.close()
    conn.close()

    print("Total Filtered Emails:", len(filtered_emails))

    creds = authenticate()
    access_token = creds.token
    header = {'Authorization': f'Bearer {access_token}'}

    for email in filtered_emails:
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print(f"UNIQUE ID: {email[1]}")
        result = mark_email(header, USER_ID, email[1], mark_action)
        print("ALREADY MARKED WITH THE GIVEN ACTION" if result is None else result)
        print("SUCCESS: TRUE, RESPONSE LABEL_IDS:", move_message(header, USER_ID, email[1], destination)['labelIds'])
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")


if __name__ == '__main__':
    main()
