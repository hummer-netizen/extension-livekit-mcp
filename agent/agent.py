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

import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.agents.llm import ChatContext, ChatMessage
from livekit.plugins import openai, silero, elevenlabs

logger = logging.getLogger("voice-browser-agent")

MCP_URL = "https://session-mcp.webfu.se/mcp"

AGENT_INSTRUCTIONS = """You are a voice-controlled browser agent. You can see and control
a live web browser through Webfuse MCP tools.

The user talks to you. You browse for them and narrate what you see and do.

Guidelines:
- Keep responses SHORT and conversational — you're speaking out loud, not writing an essay.
- Say what you see. Say what you're doing. Ask if the user wants to continue.
- When reading page content, summarize. Don't read raw HTML or huge text blocks.
- For navigation, confirm what loaded: "OK, I'm now on the Wikipedia page for Amsterdam."
- If a tool call fails, explain simply and suggest an alternative.
- Use see_domSnapshot or see_accessibilityTree to understand page structure before acting.
- Use act_click with CSS selectors from the DOM snapshot.

Examples of good voice responses:
- "I can see the Wikipedia page for Amsterdam. The infobox shows a population of 933,000. Want me to read a specific section?"
- "Scrolling down... I see sections on History, Geography, and Architecture. Which one?"
- "I clicked the link. We're on the Begijnhof page now. There's info about the Wooden House from 1528."
- "Let me search for that. Typing 'Amsterdam hotels' into the search box... and pressing Enter."
"""


class BrowserVoiceAgent(Agent):
    """Voice agent that controls a browser via Webfuse MCP."""

    def __init__(self):
        super().__init__(instructions=AGENT_INSTRUCTIONS)


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

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

    agent = BrowserVoiceAgent()

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(),
    )

    # Greet the user
    await session.say(
        "Hi! I can see your browser. What would you like me to do?"
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
