"""
LiveKit voice agent with Webfuse browser control.

A voice AI agent that can see and control the user's browser.
The user speaks commands. The agent browses, narrates what it sees,
and responds with voice.

Uses:
- LiveKit Agents SDK for real-time voice
- OpenAI for reasoning + tool use
- ElevenLabs for natural TTS
- Webfuse Session MCP for browser control

Usage:
  python agent.py dev
"""

import os, json, logging
from dotenv import load_dotenv
load_dotenv()

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.agents.llm import ChatContext, ChatMessage
from livekit.plugins import openai, silero, elevenlabs

logger = logging.getLogger("voice-browser-agent")

MCP_URL = "https://session-mcp.webfu.se/mcp"


class BrowserVoiceAgent(Agent):
    """Voice agent that controls a browser via Webfuse MCP."""

    def __init__(self, session_id: str):
        super().__init__(
            instructions=f"""You are a voice-controlled browser agent. You can see and control
a live web browser through Webfuse MCP tools.

The user talks to you. You browse for them and narrate what you see and do.

Keep your responses SHORT and conversational — you're speaking, not writing.
Say what you see. Say what you're doing. Ask if the user wants to continue.

The Webfuse session ID is: {session_id}

Examples:
- "I can see the Wikipedia page for Amsterdam. Want me to read something specific?"
- "Scrolling down to the Architecture section... I can see a list of notable buildings."
- "I clicked the link. We're now on the Begijnhof page. There's a nice section about the Wooden House."
""",
        )
        self.session_id = session_id


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    # Get session ID from room metadata or participant attributes
    session_id = ctx.room.metadata or "unknown"

    # Look for session_id in participant attributes
    for p in ctx.room.remote_participants.values():
        sid = p.attributes.get("session_id", "")
        if sid:
            session_id = sid
            break

    rest_key = os.environ["WEBFUSE_REST_KEY"]

    session = AgentSession(
        stt=openai.STT(model="whisper-1"),
        llm=openai.LLM(
            model="gpt-4o",
            mcp_servers=[
                {
                    "url": MCP_URL,
                    "headers": {"Authorization": f"Bearer {rest_key}"},
                }
            ],
        ),
        tts=elevenlabs.TTS(
            model="eleven_turbo_v2",
            voice="JBFqnCBsd6RMkjVDRZzb",  # George - warm, natural
        ),
        vad=silero.VAD.load(),
    )

    agent = BrowserVoiceAgent(session_id=session_id)

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(),
    )

    # Greet the user
    await session.say("Hi! I can see your browser. What would you like me to do?")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
