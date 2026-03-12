# Setup Guide

## Prerequisites

- [LiveKit Cloud](https://cloud.livekit.io) account (free tier: 10k minutes/month)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- Python >= 3.10
- A Webfuse space with the Automation app installed

## 1. LiveKit Cloud

```bash
# Install LiveKit CLI
curl -sSL https://get.livekit.io/cli | bash

# Authenticate
lk cloud auth

# Create and export credentials
lk app env -w -d agent/.env.local
```

This creates `agent/.env.local` with `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET`.

## 2. Add Webfuse key

Edit `agent/.env.local` and add:

```
WEBFUSE_REST_KEY=rk_your_space_rest_key
```

Get this from your Webfuse space settings.

## 3. Install & run the agent

```bash
cd agent
uv sync
uv run python agent.py download-files
uv run python agent.py dev
```

The agent registers with LiveKit Cloud and waits for rooms.

## 4. Run the token server

In another terminal:

```bash
cd agent
uv run uvicorn token_server:app --port 8083
```

## 5. Deploy the extension

Deploy the `extension/` folder to your Webfuse space:

```bash
curl -X PUT "https://api.webfu.se/api/spaces/YOUR_SPACE_ID/extensions/YOUR_EXT_ID/github/" \
  -H "Authorization: Token YOUR_REST_KEY" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/hummer-netizen/extension-livekit-mcp/extension"}'
```

Set the `TOKEN_URL` env var to point to your token server.

## 6. Test

1. Open your Webfuse space URL
2. The sidebar shows a mic button
3. Click it — it connects to LiveKit via WebRTC
4. Speak: "What's on this page?"
5. The agent reads the page and speaks back

## Architecture

```
User's browser
  ↕ WebRTC (LiveKit)
Voice Agent (Python)
  ↕ MCP (HTTP)
Webfuse Session MCP
  ↕ Automation API
User's browser tab (same one!)
```

The agent and the user's browser are connected through two channels:
- **Voice** flows through LiveKit (WebRTC)
- **Browser control** flows through Webfuse MCP

Both target the same browser session.

## Self-hosting

Use `agent_selfhosted.py` instead of `agent.py`. This uses OpenAI directly
for STT/LLM/TTS instead of LiveKit Inference. Add `OPENAI_API_KEY` to `.env.local`.

For self-hosted LiveKit server, see [docs.livekit.io/transport/self-hosting](https://docs.livekit.io/transport/self-hosting/local/).
