"""
Voice Browser Agent — Self-hosted variant (uses API keys directly)

Same as agent.py but uses OpenAI, Deepgram, and ElevenLabs plugins
directly instead of LiveKit Inference. Use this when self-hosting
LiveKit or when you want to use your own API keys.

Usage:
  uv run python agent_selfhosted.py dev
"""

import logging
import os

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    AgentServer,
    JobContext,
    JobProcess,
    cli,
)
from livekit.agents.llm.mcp import MCPServerHTTP
from livekit.plugins import openai, silero

logger = logging.getLogger("voice-browser-agent")

load_dotenv(".env.local")

MCP_URL = "https://session-mcp.webfu.se/mcp"

AGENT_INSTRUCTIONS = """You are a voice-controlled browsing assistant. You can see and control
the user's live browser through Webfuse MCP tools.

The user SPEAKS to you. You browse for them and SPEAK BACK what you find.

VOICE RULES (critical — you are speaking, not writing):
- Keep responses under 3 sentences. Users are listening, not reading.
- No bullet points, no numbered lists, no markdown. Speak naturally.
- Say what you see. Say what you're doing. Then pause for the user.
- Summarize content in plain language. Never read raw HTML or long text.
- ALWAYS pass the session_id to every tool call.

BROWSING TIPS:
- Use see_domSnapshot with quality 0.1 for quick overviews
- Use narrower CSS selectors for specific content
- On Hacker News: story IDs in vote links (vote?id=XXXXX), comments at item?id=XXXXX
"""


class BrowserAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_INSTRUCTIONS)


server = AgentServer()


def prewarm(proc: JobProcess) -> None:
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="voice-browser")
async def voice_browser(ctx: JobContext) -> None:
    rest_key = os.environ["WEBFUSE_REST_KEY"]

    session_id = ctx.room.metadata or ""
    if not session_id:
        for p in ctx.room.remote_participants.values():
            if p.metadata:
                session_id = p.metadata
                break

    logger.info(f"Starting voice browser agent, session_id={session_id[:16]}...")

    mcp_server = MCPServerHTTP(
        url=MCP_URL,
        headers={"Authorization": f"Bearer {rest_key}"},
        timeout=15,
        sse_read_timeout=60,
    )

    session = AgentSession(
        stt=openai.STT(model="whisper-1"),
        llm=openai.LLM(model="gpt-4o"),
        tts=openai.TTS(model="tts-1", voice="nova"),
        vad=ctx.proc.userdata["vad"],
        mcp_servers=[mcp_server],
        max_tool_steps=10,
    )

    await session.start(
        room=ctx.room,
        agent=BrowserAgent(),
    )

    await session.say(
        "Hey! I can see your browser. What would you like me to look at?"
    )


if __name__ == "__main__":
    cli.run_app(server)
