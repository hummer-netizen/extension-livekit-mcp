# LiveKit + Webfuse MCP — Voice Browser Agent

Talk to an AI that controls your browser. Speak commands. Watch it browse. Hear it narrate.

Built with [LiveKit Agents](https://docs.livekit.io/agents/), [OpenAI](https://platform.openai.com), [ElevenLabs](https://elevenlabs.io), and [Webfuse MCP](https://webfuse.com).

## What It Does

A voice agent that connects to a live Webfuse browser session via MCP. You speak. The agent navigates, reads pages, clicks links, and tells you what it found — out loud. You watch it happen in your browser in real time.

**Example:** Say "Find the population of Amsterdam." The agent navigates to Wikipedia, reads the infobox, and speaks the answer. You watch the page load and scroll.

## Quick Start

```bash
cd agent
pip install -r requirements.txt
cp ../.env.example .env  # Add all keys
python agent.py dev      # Start the LiveKit agent
```

In a second terminal:
```bash
cd agent
uvicorn token_server:app --port 8083
```

Deploy `extension/` to your Webfuse Space. See [SETUP.md](SETUP.md) for the full guide.

## Architecture

```
User's microphone          LiveKit Cloud             Agent Server

  🎤 speech  ──audio──>     Room routing             agent.py
                             Whisper STT              ├── GPT-4o (reasoning)
                                                      ├── MCP tools (browsing)
  🔊 speaker <──audio──     ElevenLabs TTS           └── Webfuse Session
                                                      
  👀 browser  <──────────── Webfuse MCP ────────────┘
```

Three streams happen simultaneously:
1. **Voice in:** User speech → LiveKit → Whisper STT → text
2. **Reasoning:** GPT-4o decides what to do, calls Webfuse MCP tools
3. **Voice out:** Agent response → ElevenLabs TTS → speaker

The browser is just another tool. The agent calls `see_domSnapshot` to read pages, `act_click` to click, `navigate` to go somewhere new. Same 13 tools as every Webfuse integration — but voice-controlled.

## What Makes This Different

Every other demo in this series uses text. This one is **voice-first**.

The user says "Scroll down and read me the pricing section." The agent scrolls (visible in the browser), reads the content, and speaks a summary. No typing. No reading. Just talking and watching.

It's like having someone browse the web for you while you sit back and listen.

## Use Cases

- **Accessibility.** Visually impaired users navigate the web by voice. The agent describes what's on screen.
- **Hands-free workflows.** Check inventory, read dashboards, fill forms — while your hands are busy.
- **Customer service.** "I need to return this order." The agent navigates the return flow and confirms.
- **Research.** "What's on this page? Find the architecture section and summarize it."
- **Elderly tech support.** "Help me find my email." The agent opens Gmail, reads the inbox.

## The Agent Stack

| Component | Technology | Role |
|-----------|-----------|------|
| Speech-to-Text | OpenAI Whisper | Ears — converts speech to text |
| Reasoning | GPT-4o + MCP tools | Brain — decides what to do |
| Text-to-Speech | ElevenLabs Turbo v2 | Voice — speaks responses naturally |
| Voice Activity | Silero VAD | Timing — knows when you stopped talking |
| Audio Transport | LiveKit Cloud | Pipes — real-time audio streaming |
| Browser Control | Webfuse Session MCP | Hands — 13 tools for any website |

## Swap Components

**Different voice:**
```python
# Change voice in agent.py
tts=elevenlabs.TTS(voice="YOUR_VOICE_ID")
```

Browse voices at [elevenlabs.io/voice-library](https://elevenlabs.io/voice-library).

**Different LLM:**
```python
# Use Anthropic instead of OpenAI
from livekit.plugins import anthropic
llm=anthropic.LLM(model="claude-sonnet-4-20250514")
```

**Different STT:**
```python
# Use Deepgram
from livekit.plugins import deepgram
stt=deepgram.STT()
```

## Project Structure

```
agent/
  agent.py           # LiveKit voice agent with MCP tools
  token_server.py    # Generates LiveKit room tokens
  requirements.txt   # Python dependencies
extension/
  manifest.json      # Webfuse extension config
  sidepanel.html     # Voice UI (microphone button + transcript)
  sidepanel.js       # LiveKit JS client connection
  background.js      # Auto-opens sidepanel
blog/
  draft.md           # Blog post
```

## Links

- [Blog Post](blog/draft.md)
- [Webfuse](https://webfuse.com) — AI browser actuation platform
- [LiveKit Agents Docs](https://docs.livekit.io/agents/) — Voice agent framework
- [Session MCP Server Docs](https://dev.webfu.se/session-mcp-server/) — Full tool reference
- [ElevenLabs](https://elevenlabs.io) — Voice synthesis

## License

MIT
