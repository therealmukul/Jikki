import base64
import pickle
import os.path
import datetime
import re

import markdownify
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GmailClient:
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, credentials_path="credentials.json"):
        self.credentials_path = credentials_path
        self._service = self._get_gmail_service()

    def _get_gmail_service(self):
        """Handles authentication and service creation."""
        creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        self._service = build("gmail", "v1", credentials=creds)

        return self._service

    def fetch_new_unread_emails(self):
        """Fetches unread emails after a specific date."""
        today = datetime.date.today().strftime("%Y/%m/%d")
        query = "label:unread after:" + today
        results = (
            self._service.users()
            .messages()
            .list(userId="me", q=query)
            .execute()
        )
        return results.get("messages", [])

    def fetch_all_emails_by_date(self, date):
        """Fetches all emails received on a specific date."""
        start_date = date.strftime("%Y/%m/%d")
        end_date = date + datetime.timedelta(days=1)
        query = f"after: {start_date} before: {end_date}"
        results = (
            self._service.users()
            .messages()
            .list(userId="me", q=query)
            .execute()
        )

        return results.get("messages", [])

    @staticmethod
    def clean_email_body(body):
        """Prepares the email body for question answering by LLM."""
        markdown_body = markdownify.markdownify(body, heading_style="ATX")

        return markdown_body

    def extract_email_data(self, message_id):
        """Extracts subject, sender, and body from an email."""
        message = (
            self._service.users()
            .messages()
            .get(userId="me", id=message_id)
            .execute()
        )
        payload = message["payload"]
        headers = payload["headers"]

        subject = ""
        sender = ""
        body = ""

        for header in headers:
            if header["name"] == "Subject":
                subject = header["value"]
            if header["name"] == "From":
                sender = header["value"]

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(
                        part["body"]["data"]
                    ).decode("utf-8")
                    break
        elif "body" in payload:
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode(
                "utf-8"
            )

        body = self.clean_email_body(body)

        res = {"sender": sender, "subject": subject, "body": body}
        return res
