# LiveKit + Webfuse MCP — Voice Browser Agent

Talk to an AI that controls your browser. Speak commands. Watch it browse. Hear it narrate.

## What It Does

A voice agent running on LiveKit that connects to a Webfuse browser session via MCP. The user speaks, the agent browses. "Find the population of Amsterdam" — the agent navigates to Wikipedia, reads the infobox, and says the answer out loud.

## Quick Start

```bash
cd agent
pip install -r requirements.txt
cp ../.env.example .env  # Add all keys
python agent.py dev      # Start the LiveKit agent
uvicorn token_server:app --port 8083  # Start token server
```

Deploy `extension/` to your Webfuse Space.

## Architecture

```
User's mic                LiveKit Cloud              Agent Server
                          
  🎤 Speech   ──audio──>   Room                     agent.py
                            ├── STT (Whisper)
                            ├── LLM (GPT-4o + MCP)  → Webfuse browser
                            └── TTS (ElevenLabs)
  🔊 Speaker  <──audio──                            
                                                     
  👀 Browser   <── Webfuse MCP ──────────────────── tool calls
```

The user talks. LiveKit handles audio streaming. The agent reasons with GPT-4o, controls the browser via MCP, and responds with ElevenLabs voice. Everything happens in real time.

## What Makes This Different

Other demos show text-based browser control. This one is voice-first.

The user says "scroll down and read me the Architecture section." The agent scrolls the page (visible in the browser), reads the content, and speaks a summary. The user watches and listens simultaneously.

It's like having someone browse the web for you while you sit back and talk to them.

## Links

- [Blog Post](/blog/build-a-voice-agent-that-browses-with-livekit-and-webfuse)
- [Webfuse](https://webfuse.com)
- [LiveKit Agents](https://docs.livekit.io/agents/)
- [Session MCP Server Docs](https://dev.webfu.se/session-mcp-server/)
