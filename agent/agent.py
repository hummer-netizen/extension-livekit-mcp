"""
Voice Browser Agent — Talk to an AI that browses for you.

LiveKit Agents + Webfuse MCP = voice-controlled browser.
The user speaks. The AI sees the page, clicks, types, navigates, and narrates.

Usage:
  uv run python agent.py dev
  uv run python agent.py console   # terminal-only (no browser needed)
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
    inference,
)
from livekit.agents.llm.mcp import MCPServerHTTP
from livekit.plugins import silero

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
- For navigation: "OK, I opened the article about clean rooms. It's about..."
- For page content: "The top story has 750 points. It's about Malus, a clean room service."
- When unsure: "I see a few options here. Want me to read the top story, or something else?"
- ALWAYS pass the session_id to every tool call.

BROWSING TIPS:
- Use see_domSnapshot with quality 0.1 for quick overviews (list pages, search results)
- Use narrower CSS selectors for specific content ("article", ".comment-tree", "h1")
- Use act_click to click links, act_type to type in inputs
- Use navigate to go to a URL directly
- If content is truncated, use a more specific selector
- On Hacker News: story IDs are in vote links (vote?id=XXXXX), comments at item?id=XXXXX
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

    # Get the Webfuse session ID from room metadata or participant metadata
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
        # STT: user's voice -> text
        stt=inference.STT(model="deepgram/nova-3"),
        # LLM: reasoning + tool use
        llm=inference.LLM(model="openai/gpt-4o"),
        # TTS: agent's voice
        tts=inference.TTS(
            model="cartesia/sonic-3",
            voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        ),
        vad=ctx.proc.userdata["vad"],
        mcp_servers=[mcp_server],
        max_tool_steps=10,
    )

    await session.start(
        room=ctx.room,
        agent=BrowserAgent(),
    )

    # Greet the user
    await session.say(
        "Hey! I can see your browser. What would you like me to look at?"
    )


if __name__ == "__main__":
    cli.run_app(server)
