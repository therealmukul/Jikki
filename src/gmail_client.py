import base64
import pickle
import os.path
import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]  # Read-only access


def get_gmail_service():
    creds = None
    # Token.pickle stores previously saved credentials
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials, initiate the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )  # Replace 'credentials.json' with your file
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def fetch_new_emails(service):
    today = datetime.date.today().strftime("%Y/%m/%d")
    query = "label:unread after:" + today

    results = service.users().messages().list(userId="me", q=query).execute()

    return results.get("messages", [])


def extract_email_data(service, message_id):
    body = ""
    sender = ""
    subject = ""

    message = (
        service.users().messages().get(userId="me", id=message_id).execute()
    )
    payload = message["payload"]
    headers = payload["headers"]

    for header in headers:
        if header["name"] == "Subject":
            subject = header["value"]
        if header["name"] == "From":
            sender = header["value"]

    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode(
                    "utf-8"
                )
                break
    else:
        if "body" in payload:
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode(
                "utf-8"
            )
        else:
            body = ""
    print(subject, sender, body)
    print()
    return subject, sender, body


if __name__ == "__main__":
    service = get_gmail_service()
    new_email_ids = fetch_new_emails(service)
    print(new_email_ids)

    if new_email_ids:
        for item in new_email_ids:
            message_id = item["id"]
            extract_email_data(service, message_id)
    # if new_email_ids:
    #     for message_id in new_email_ids:
    #         subject, sender, body = extract_email_data(message_id)
    #         print(f"From: {sender}\nSubject: {subject}\nBody: {body}\n")
    # else:
    #     print("No new emails found.")
