"""
SupportFlow AI — Gmail Email Reader
------------------------------------
Phase: Email Channel Integration
Goal:  Authenticate with Gmail OAuth and read the latest emails.

Run this script ONCE to authorize your Gmail account.
After authorization, a token.json file is saved locally so
you won't need to log in again on subsequent runs.

Usage:
    python gmail_reader.py

Prerequisites:
    1. credentials.json must be in the same directory as this script.
    2. pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

import os
import base64
import json
from email import message_from_bytes
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    Credentials = None
    InstalledAppFlow = None
    Request = None
    build = None


# ─── Scopes ────────────────────────────────────────────────────────────────────
# gmail.modify  → read + mark as read + move emails
# gmail.send    → send replies (needed later for the full support loop)
# If you change scopes, delete token.json and re-authenticate.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
]

CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
TOKEN_FILE = os.getenv("GMAIL_TOKEN_PATH", "token.json")


# ─── Authentication ─────────────────────────────────────────────────────────────
def get_gmail_service():
    """
    Handles OAuth authentication and returns an authorized Gmail service.

    Priority:
    1. GMAIL_TOKEN_JSON env variable (Serialized JSON string of credentials token)
    2. GMAIL_TOKEN_PATH file (token.json)
    3. GMAIL_CREDENTIALS_PATH file / GMAIL_CREDENTIALS_JSON env variable

    In production (ENVIRONMENT=production), opening interactive browser is disabled.
    """
    if not GOOGLE_AUTH_AVAILABLE:
        return None
    creds = None
    env_name = os.getenv("ENVIRONMENT", "development").lower()

    # 1. Try loading token from environment variable
    token_json_env = os.getenv("GMAIL_TOKEN_JSON")
    if token_json_env:
        try:
            info = json.loads(token_json_env)
            creds = Credentials.from_authorized_user_info(info, SCOPES)
        except Exception as e:
            print(f"⚠️ Failed to parse GMAIL_TOKEN_JSON from env: {e}")

    # 2. Fallback to token file
    if not creds and os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"⚠️ Failed to load token from file {TOKEN_FILE}: {e}")

    # 3. Validate or refresh token
    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️ Token refresh failed: {e}")
                creds = None

    # 4. Handle initial authorization if no valid credentials
    if not creds:
        if env_name == "production":
            raise RuntimeError(
                "❌ Gmail token is missing or expired in production environment. "
                "Interactive login browser flow is disabled in production. "
                "Set GMAIL_TOKEN_JSON env var or deploy an authorized token.json file."
            )

        # Development interactive authorization flow
        credentials_json_env = os.getenv("GMAIL_CREDENTIALS_JSON")
        if credentials_json_env:
            try:
                client_config = json.loads(credentials_json_env)
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            except Exception as e:
                raise RuntimeError(f"Failed to load credentials from GMAIL_CREDENTIALS_JSON: {e}")
        elif os.path.exists(CREDENTIALS_FILE):
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        else:
            raise FileNotFoundError(
                f"\n❌ '{CREDENTIALS_FILE}' not found and GMAIL_CREDENTIALS_JSON is unset.\n"
                "Download it from: Google Cloud Console → APIs & Services "
                "→ Credentials → OAuth 2.0 Client ID → Download JSON\n"
                f"Place it in: {os.path.abspath('.')}"
            )

        creds = flow.run_local_server(port=0)

        # Save token file in dev mode for subsequent runs
        try:
            with open(TOKEN_FILE, "w") as token_file:
                token_file.write(creds.to_json())
            print(f"✅ Token saved to '{TOKEN_FILE}' — no login needed next time.\n")
        except Exception as e:
            print(f"⚠️ Could not write token to file {TOKEN_FILE}: {e}")

    return build("gmail", "v1", credentials=creds)


# ─── Email Parsing ──────────────────────────────────────────────────────────────
def decode_body(payload) -> str:
    """
    Extract plain text body from email payload.
    Handles both single-part and multipart emails.
    """
    body = ""

    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    elif payload.get("mimeType", "").startswith("multipart"):
        for part in payload.get("parts", []):
            body = decode_body(part)
            if body:
                break

    return body.strip()


def extract_header(headers: list, name: str) -> str:
    """Pull a specific header value (e.g. From, Subject, Date) from the headers list."""
    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]
    return "(not found)"


def parse_email(msg: dict) -> dict:
    """
    Convert raw Gmail API message into a clean structured dict.

    Returns:
        {
            "id":       Gmail message ID (needed for replies, marking read, etc.)
            "sender":   Sender email address
            "subject":  Email subject line
            "date":     Date received
            "body":     Plain text body
        }
    """
    payload = msg.get("payload", {})
    headers = payload.get("headers", [])

    return {
        "id":       msg["id"],
        "sender":   extract_header(headers, "From"),
        "subject":  extract_header(headers, "Subject"),
        "date":     extract_header(headers, "Date"),
        "body":     decode_body(payload),
    }


# ─── Core Functions ─────────────────────────────────────────────────────────────
def fetch_latest_emails(service, max_results: int = 5, label: str = "INBOX") -> list:
    """
    Fetch and parse the latest emails from a Gmail label.

    Args:
        service:      Authorized Gmail service object.
        max_results:  Number of emails to retrieve (default: 5).
        label:        Gmail label to read from (default: INBOX).

    Returns:
        List of parsed email dicts, newest first.
    """
    # Step 1: Get list of message IDs
    results = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        labelIds=[label]
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        return []

    # Step 2: Fetch full content for each message ID
    emails = []
    for msg_ref in messages:
        full_msg = service.users().messages().get(
            userId="me",
            id=msg_ref["id"],
            format="full"
        ).execute()
        emails.append(parse_email(full_msg))

    return emails


def display_email(email: dict, index: int) -> None:
    """Print a single email in a clean, readable format."""
    divider = "─" * 60
    print(f"\n{divider}")
    print(f"  Email #{index + 1}")
    print(divider)
    print(f"  📨 From    : {email['sender']}")
    print(f"  📋 Subject : {email['subject']}")
    print(f"  🕐 Date    : {email['date']}")
    print(f"  🔑 ID      : {email['id']}")
    print(f"\n  📝 Body:\n")

    body_preview = email["body"][:500] if email["body"] else "(no plain text body)"
    for line in body_preview.splitlines():
        print(f"     {line}")

    if email["body"] and len(email["body"]) > 500:
        print(f"\n     ... [{len(email['body']) - 500} more characters]")

    print(divider)


# ─── Entry Point ────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  SupportFlow AI — Gmail Reader")
    print("=" * 60)
    print()

    # 1. Authenticate
    service = get_gmail_service()
    print("✅ Gmail authentication successful.\n")

    # 2. Fetch latest emails
    emails = fetch_latest_emails(service, max_results=5)

    if not emails:
        return

    # 3. Display results
    print(f"📊 Found {len(emails)} email(s):\n")
    for i, email in enumerate(emails):
        display_email(email, i)

    # 4. Show structured output (what your agent will receive later)
    print("\n\n" + "=" * 60)
    print("  Structured Output (what your AI agent will receive)")
    print("=" * 60)
    print(json.dumps(emails[0], indent=2, ensure_ascii=False))
    print("\n✅ Done. Your next step: pass this structured dict to the Intent Agent.")


if __name__ == "__main__":
    main()