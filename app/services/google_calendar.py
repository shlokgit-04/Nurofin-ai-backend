import os
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from app.core.config import settings

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "YOUR_PROJECT_ID")

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

CLIENT_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "project_id": GOOGLE_PROJECT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": GOOGLE_CLIENT_SECRET,
    }
}


def get_google_auth_url(redirect_uri: str) -> str:
    CLIENT_CONFIG["web"]["redirect_uris"] = [redirect_uri]
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url


def exchange_code_for_tokens(code: str, redirect_uri: str):
    CLIENT_CONFIG["web"]["redirect_uris"] = [redirect_uri]
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return {
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "expires_at": credentials.expiry.isoformat() if credentials.expiry else None
    }


def refresh_credentials(user) -> Credentials:
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        user.google_access_token = creds.token
        if creds.expiry:
            user.google_token_expires_at = creds.expiry.isoformat()
    return creds


def fetch_calendar_events(user, time_min: datetime, time_max: datetime):
    creds = refresh_credentials(user)

    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        maxResults=250,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    return events_result.get('items', [])
