# LiveKit + Webfuse MCP — Voice Browser Agent

Talk to an AI that controls your browser. Speak commands. Watch it browse. Hear it narrate.

## What It Does

A voice agent running on [LiveKit](https://livekit.io) that connects to a Webfuse browser session via MCP. The user speaks, the agent browses. "Find the population of Amsterdam" — the agent navigates to Wikipedia, reads the infobox, and says the answer out loud.

## Quick Start

```bash
cd agent
pip install -r requirements.txt
cp ../.env.example .env  # Add all keys
python agent.py dev      # Start the LiveKit agent
uvicorn token_server:app --port 8083  # Start token server (second terminal)
```

Deploy `extension/` to your Webfuse Space. See [SETUP.md](SETUP.md) for the full guide.

Try the [voice walkthrough](examples/WALKTHROUGH.md) for demo conversations.

## Architecture

```
User's microphone          LiveKit Cloud             Agent Server

  🎤 Speech   ──audio──>   Room routing              agent.py
                            Whisper STT               ├── GPT-4o (reason)
                                                      ├── MCP tools (browse)
  🔊 Speaker  <──audio──   ElevenLabs TTS            └── Webfuse Session
                                                      
  👀 Browser  <──────────── Webfuse MCP ─────────────┘
```

Three streams run simultaneously:
1. **Voice in:** User speech → LiveKit → Whisper STT → text
2. **Reasoning:** GPT-4o reads the text, decides what to do, calls MCP tools
3. **Voice out:** Agent response → ElevenLabs TTS → LiveKit → speaker

Response time: ~2-4 seconds for simple commands.

## What Makes This Different

Other demos show **text-based** browser control. This one is **voice-first**.

The user says "scroll down and read me the Architecture section." The agent scrolls the page (visible in the browser), reads the content, and speaks a summary. The user watches and listens simultaneously.

It's like having someone browse the web for you while you sit back and talk to them.

## Stack

| Component | Tech | Role |
|-----------|------|------|
| Voice transport | [LiveKit](https://livekit.io) | Real-time audio streaming |
| Speech-to-text | [Whisper](https://openai.com/whisper) (via LiveKit) | Understand speech |
| Reasoning | [GPT-4o](https://openai.com) | Plan actions, summarize |
| Text-to-speech | [ElevenLabs](https://elevenlabs.io) | Natural voice output |
| Browser control | [Webfuse MCP](https://webfuse.com) | 13 browser tools |
| Voice activity | [Silero VAD](https://github.com/snakers4/silero-vad) | Detect speech boundaries |

## Use Cases

- **Accessibility.** Visually impaired users navigate the web by voice
- **Hands-free workflows.** Control web apps while your hands are busy
- **Customer service.** Voice agents that handle web-based processes for callers
- **Elderly tech support.** "Help me find my email" — spoken, not typed

## Swap the Voice

Change the ElevenLabs voice in `agent.py`:

```python
tts=elevenlabs.TTS(
    model="eleven_turbo_v2",
    voice="JBFqnCBsd6RMkjVDRZzb",  # George — swap voice ID here
)
```

Browse voices at [elevenlabs.io/voice-library](https://elevenlabs.io/voice-library).

Or switch to OpenAI TTS:

```python
from livekit.plugins import openai
tts=openai.TTS(model="tts-1", voice="nova")
```

## Links

- [Blog Post](blog/draft.md)
- [Voice Walkthrough](examples/WALKTHROUGH.md) — demo conversations to try
- [Webfuse](https://webfuse.com) — AI browser actuation platform
- [LiveKit Agents Docs](https://docs.livekit.io/agents/) — Voice agent framework
- [Session MCP Server Docs](https://dev.webfu.se/session-mcp-server/) — Full tool reference

## License

MIT
