#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-api-python-client>=2.167.0",
#     "google-auth>=2.39.0",
#     "google-auth-oauthlib>=1.2.2",
# ]
# ///

import argparse
import base64
import json
import os
import sys
import time
from email.message import EmailMessage

import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
TOKEN_FILE = os.path.expanduser("~/.gmail_token.json")
FROM_ADDRESS = "erik.van.zijst@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# === TOKEN HELPERS ===
def save_token(data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    else:
        return None

def refresh_token(token_data):
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": token_data["client_id"],
            "client_secret": token_data["client_secret"],
            "refresh_token": token_data["refresh_token"],
            "grant_type": "refresh_token",
        },
    )
    resp.raise_for_status()
    new_token = resp.json()
    token_data["access_token"] = new_token["access_token"]
    token_data["expires_at"] = time.time() + new_token["expires_in"]
    save_token(token_data)
    return token_data

def get_valid_token():
    creds = load_token()
    if creds:
        if creds.get("expires_at", 0) > time.time():
            return creds["access_token"]
        return refresh_token(creds)["access_token"]
    raise Exception("No valid token found. Run `auth` first.")

# === AUTH FLOW ===
def do_auth(credentials_path):
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    creds = flow.run_local_server(port=0)
    token_data = {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "expires_at": creds.expiry.timestamp(),
    }
    save_token(token_data)
    print("✅ Auth complete. Token saved to:", TOKEN_FILE)

def send_email(subject: str, recipients: list, body: str):
    token_data = load_token()
    if token_data["expires_at"] < time.time():
        token_data = refresh_token(token_data)

    creds = Credentials(
        token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=SCOPES,
    )

    service = build("gmail", "v1", credentials=creds)

    msg = EmailMessage()
    msg["To"] = ','.join(recipients)
    msg["From"] = FROM_ADDRESS
    msg["Subject"] = subject
    msg.set_content(body)
    raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    try:
        send_result = service.users().messages().send(userId="me", body={"raw": raw_msg}).execute()
        print(f"✅ Email sent. ID: {send_result['id']}")
    except Exception as e:
        print("❌ Failed to send email:", e, file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Send email from the shell using your gmail account.")
    subparsers = parser.add_subparsers(dest="command")

    # Auth command
    auth_parser = subparsers.add_parser("auth", help="Authenticate with Gmail")
    auth_parser.add_argument("--credentials", default='credentials.json', help="Path to Google client credentials.json")

    # Send command
    send_parser = subparsers.add_parser("send", help="Send email")
    send_parser.add_argument("-s", "--subject", required=True, help="subject")
    send_parser.add_argument('recipients', nargs='+', help="recipient email addresses")

    args = parser.parse_args()

    if args.command == "auth":
        do_auth(args.credentials)
    elif args.command == "send":
        send_email(args.subject, args.recipients, sys.stdin.read())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
