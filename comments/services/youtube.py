from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CLIENT_SECRET_FILE = os.environ.get("YOUTUBE_CLIENT_SECRET", "client_secret.json")
TOKEN_FILE = Path(os.environ.get("YOUTUBE_TOKEN_FILE", settings.BASE_DIR / "youtube_token.json"))


def get_credentials() -> Credentials:
    """Retrieve OAuth credentials, refreshing or creating when needed."""

    creds: Credentials | None = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return creds


def build_youtube_service():
    creds = get_credentials()
    return build("youtube", "v3", credentials=creds)


def get_live_chat_metadata(youtube, video_id: str) -> dict | None:
    request = youtube.videos().list(part="liveStreamingDetails,snippet", id=video_id)
    response = request.execute()
    items = response.get("items", [])
    if not items:
        return None
    data = items[0]
    details = data.get("liveStreamingDetails", {})
    snippet = data.get("snippet", {})
    return {
        "live_chat_id": details.get("activeLiveChatId"),
        "title": snippet.get("title"),
        "scheduled_start_time": details.get("scheduledStartTime"),
    }


def fetch_live_chat_page(youtube, live_chat_id: str, page_token: str | None = None) -> Tuple[
    Iterable[Dict[str, Any]],
    str | None,
    int,
]:
    request = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet,authorDetails",
        maxResults=200,
        pageToken=page_token,
    )
    response = request.execute()

    return (
        response.get("items", []),
        response.get("nextPageToken"),
        response.get("pollingIntervalMillis", 1500),
    )
