# Voice Browser Agent

**Talk to an AI that controls your browser.** LiveKit + Webfuse MCP.

The user speaks. The AI browses. "What's on this page?" → reads it. "Open the top story" → clicks it. "Write a funny comment" → types one in the text box.

Voice in, browser actions out, voice back.

## How it works

```
User speaks → LiveKit (WebRTC) → STT → LLM (GPT-4o + Webfuse MCP tools) → TTS → User hears
                                         ↓
                                  Browser actions (click, type, navigate)
                                         ↓
                                  User sees it happen in real time
```

The LLM has access to 13 browser tools via Webfuse's MCP endpoint. When you say "open the first link", GPT-4o calls `act_click` through MCP, and the browser clicks in the user's live tab.

## Stack

- **LiveKit Agents** — real-time voice pipeline (STT → LLM → TTS)
- **Webfuse Session MCP** — 13 browser tools, auto-discovered
- **LiveKit Cloud** — WebRTC transport, deployment, inference
- **Webfuse Extension** — sidebar UI with mic button + transcript

## Quick start

### 1. LiveKit Cloud

Sign up at [cloud.livekit.io](https://cloud.livekit.io) (free tier: 10k minutes/month).

### 2. Agent setup

```bash
cd agent
cp ../.env.example .env.local
# Fill in your keys

uv sync
uv run python agent.py download-files
uv run python agent.py dev
```

### 3. Token server

```bash
cd agent
uvicorn token_server:app --port 8083
```

### 4. Webfuse extension

Deploy the `extension/` folder to your Webfuse space. Set the `TOKEN_URL` env var to your token server URL.

## Files

```
agent/
  agent.py          — Voice agent (LiveKit + Webfuse MCP)
  token_server.py   — Generates LiveKit room tokens
  pyproject.toml    — Python dependencies

extension/
  sidepanel.html    — Voice UI (mic button, transcript, visualizer)
  sidepanel.js      — LiveKit client connection
  background.js     — Extension scaffold
  manifest.json     — Webfuse extension manifest

proxy/
  worker.js         — Cloudflare Worker (CORS proxy for token server)
```

## Live demo

[webfu.se/+livekit-mcp/](https://webfu.se/+livekit-mcp/)

## Architecture

The voice agent runs server-side and joins a LiveKit room. The extension sidebar connects to the same room via WebRTC. Audio flows both ways in real-time.

When the LLM decides to use a browser tool, it calls the Webfuse MCP endpoint. Webfuse routes the action to the user's browser tab. The user sees the browser move while the agent narrates.

The key insight: LiveKit handles the hard parts of real-time voice (turn detection, interruption handling, echo cancellation). Webfuse handles browser control. Your code is just the agent logic.
