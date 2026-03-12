"""
Token server — generates LiveKit room tokens for the Webfuse extension.

Creates one room per Webfuse session. The agent joins via dispatch.
The session_id is passed as room metadata so the agent knows which browser to control.

Usage:
  uvicorn token_server:app --port 8083
"""

import os
import time
import logging

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit.api import LiveKitAPI, CreateRoomRequest, AccessToken, VideoGrants
from dotenv import load_dotenv

load_dotenv(".env.local")
logger = logging.getLogger("token-server")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/token")
async def get_token(session_id: str = Query(..., min_length=4)):
    api_key = os.environ["LIVEKIT_API_KEY"]
    api_secret = os.environ["LIVEKIT_API_SECRET"]
    livekit_url = os.environ["LIVEKIT_URL"]

    room_name = f"browser-{session_id[:20]}"

    # Create the room with session_id as metadata so the agent can find it
    try:
        lk = LiveKitAPI(
            url=livekit_url,
            api_key=api_key,
            api_secret=api_secret,
        )
        await lk.room.create_room(
            CreateRoomRequest(
                name=room_name,
                metadata=session_id,
                empty_timeout=300,  # 5 min idle
                max_participants=3,  # user + agent + buffer
            )
        )
        await lk.aclose()
    except Exception as e:
        logger.warning(f"Room create (may already exist): {e}")

    token = (
        AccessToken(api_key, api_secret)
        .with_identity(f"user-{session_id[:8]}")
        .with_name("Browser User")
        .with_grants(VideoGrants(room_join=True, room=room_name))
        .with_metadata(session_id)
        .with_ttl(3600)
    )

    ws_url = livekit_url
    if ws_url.startswith("https://"):
        ws_url = ws_url.replace("https://", "wss://")
    elif not ws_url.startswith("wss://"):
        ws_url = f"wss://{ws_url}"

    return {
        "token": token.to_jwt(),
        "url": ws_url,
        "room": room_name,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
