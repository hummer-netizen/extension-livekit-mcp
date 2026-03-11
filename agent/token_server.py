"""
Token server — generates LiveKit room tokens for Webfuse extension clients.

Creates a room per Webfuse session and returns a join token.

Usage:
  uvicorn token_server:app --port 8083
"""

import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from livekit.api import AccessToken, VideoGrants
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/token")
def get_token(session_id: str = Query(...)):
    api_key = os.environ["LIVEKIT_API_KEY"]
    api_secret = os.environ["LIVEKIT_API_SECRET"]
    livekit_url = os.environ["LIVEKIT_URL"]

    room_name = f"browser-{session_id[:16]}"

    token = (
        AccessToken(api_key, api_secret)
        .with_identity(f"user-{session_id[:8]}")
        .with_grants(VideoGrants(room_join=True, room=room_name))
        .with_metadata(session_id)
    )

    return {
        "token": token.to_jwt(),
        "url": livekit_url.replace("wss://", "https://"),
        "room": room_name,
    }

@app.get("/health")
def health():
    return {"status": "ok"}
