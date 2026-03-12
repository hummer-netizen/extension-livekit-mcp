---
title: "Build a Voice Agent That Browses the Web (LiveKit + Webfuse)"
description: "A voice AI that controls a live browser. Speak commands, watch it browse, hear it narrate. LiveKit Agents + ElevenLabs + Webfuse MCP."
shortTitle: "LiveKit Voice Agent + Webfuse MCP"
created: 2026-03-11
category: ai-agents
authorId: nicholas-piel
tags: ["livekit", "voice-ai", "elevenlabs", "mcp", "browser-automation", "webfuse"]
featurePriority: 0
relatedLinks:
  - text: "OpenAI Agent + Webfuse"
    href: "/blog/build-an-ai-agent-that-controls-a-live-browser"
    description: "Text-based agent with the OpenAI Agents SDK."
  - text: "Claude Desktop + Webfuse"
    href: "/blog/connect-claude-to-a-live-browser-with-webfuse-mcp"
    description: "Zero-code setup with Claude Desktop."
  - text: "Session MCP Server Docs"
    href: "https://dev.webfu.se/session-mcp-server/"
    description: "Full reference for the 13 browser tools."
faqs:
  - question: "Does this need a phone call?"
    answer: "No. The voice runs in the browser via LiveKit. No phone number needed. Just a microphone."
  - question: "Can I use a different voice?"
    answer: "Yes. Swap the ElevenLabs voice ID or switch to OpenAI TTS. The agent framework is voice-provider agnostic."
  - question: "How fast is the response?"
    answer: "Sub-second for voice. Browser actions take 1-3 seconds depending on the tool. The agent narrates while browsing, so there's no dead air."
  - question: "Can the user take over the browser?"
    answer: "Yes. The user sees everything the agent does. They can grab the mouse at any time and browse manually, then hand back control by speaking."
---

What if you could just tell your browser what to do?

Not type commands. Not click through menus. Just say it. "Find me a hotel in Amsterdam under 200 euros." And watch it happen.

<TldrBox title="TL;DR">

**A voice agent that controls a live browser.** Built with LiveKit Agents (real-time voice), OpenAI (reasoning), ElevenLabs (natural speech), and Webfuse MCP (browser control). Speak, watch, listen.

Source: [github.com/hummer-netizen/extension-livekit-mcp](https://github.com/hummer-netizen/extension-livekit-mcp)

</TldrBox>

## The Experience

Click the microphone. Say "What's on this page?"

The agent reads the page. Not a raw dump. A natural summary. "I can see the Wikipedia article for Amsterdam. It has sections on history, geography, architecture, and culture. The infobox shows a population of about 933,000. Want me to read something specific?"

Say "Find the architecture section and tell me about it."

You watch the browser scroll down. The agent finds the section. "There's a section about Amsterdam's canal ring being a UNESCO World Heritage site. It mentions several notable buildings. Want me to click into any of them?"

Say "Click on the Begijnhof."

The browser navigates. A new page loads. The agent reads the intro and tells you about it. You're browsing the web by talking.

## Why Voice Changes Everything

Text-based browser agents are powerful. But they require your hands and eyes. You type a command. You read the output. You type another command.

Voice lets you lean back.

The agent narrates what it sees while it browses. You listen. You watch. When you want to change direction, you just say so. No typing, no clicking, no copy-pasting.

This is closer to how humans actually collaborate. Think of calling a colleague and asking them to look something up. They talk you through what they see. You ask follow-up questions. Natural.

## The Architecture

```
User's microphone          LiveKit Cloud             Agent

  🎤 speech ──audio──>      Room routing             agent.py
                             Whisper STT              ├── GPT-4o (reason)
                                                      ├── MCP tools (browse)
  🔊 speaker <──audio──     ElevenLabs TTS           └── Webfuse Session
                                                      
  👀 browser  <──────────── Webfuse MCP ─────────────┘
```

Three streams happening simultaneously:
1. **Voice in:** User speech → LiveKit → Whisper STT → text
2. **Reasoning:** GPT-4o reads the text, decides what to do, calls MCP tools
3. **Voice out:** Agent response → ElevenLabs TTS → LiveKit → user's speaker

The browser is just another tool. The agent calls `see_domSnapshot` to read a page, `act_click` to click a link, `navigate` to go somewhere new. Same 13 tools as every other integration. But now they're voice-controlled.

::ArticleSignupCta
---
heading: "Give your voice agent a browser"
subtitle: "Webfuse connects any voice AI to live web sessions via MCP. Your agent can finally see and touch the web."
---
::

## The Agent Code

LiveKit's Agent SDK makes the voice part surprisingly simple:

```python
session = AgentSession(
    stt=openai.STT(model="whisper-1"),
    llm=openai.LLM(
        model="gpt-4o",
        mcp_servers=[{
            "url": "https://session-mcp.webfu.se/mcp",
            "headers": {"Authorization": f"Bearer {rest_key}"},
        }],
    ),
    tts=elevenlabs.TTS(voice="George"),
    vad=silero.VAD.load(),
)
```

That's the core. STT for ears. LLM for brains. MCP for hands. TTS for voice. VAD for knowing when the user stopped talking.

The agent instructions tell it to keep responses short and conversational:

```
Keep your responses SHORT — you're speaking, not writing.
Say what you see. Say what you're doing. Ask if the user wants to continue.
```

Nobody wants a paragraph read to them. The agent speaks in quick, natural phrases.

## What People Build With This

The demo browses Wikipedia. But voice + browser unlocks much bigger things:

- **Accessibility.** Visually impaired users navigate the web by voice. The agent describes what's on screen and acts on commands.
- **Hands-free workflows.** A warehouse worker checks inventory on a web app while their hands are full. "Show me the stock for item 4521."
- **Customer service.** "I need to return this order." The agent navigates the return flow, fills in the details, reads back the confirmation. The customer just talks.
- **Elderly tech support.** "Can you help me find my email?" The agent opens Gmail, reads the inbox, opens the right message.

Voice is the most natural interface humans have. The browser is where everything lives. Connecting them was the missing piece.

## Running It

**1. Start the agent:**
```bash
cd agent && pip install -r requirements.txt
python agent.py dev
```

**2. Start the token server:**
```bash
uvicorn token_server:app --port 8083
```

**3. Deploy the extension** to your Webfuse Space.

**4. Click the microphone** and start talking.

## Source Code

Everything is on GitHub: [hummer-netizen/extension-livekit-mcp](https://github.com/hummer-netizen/extension-livekit-mcp)

- `agent/agent.py` -- LiveKit voice agent with Webfuse MCP
- `agent/token_server.py` -- Token generation for LiveKit rooms
- `extension/` -- Webfuse sidebar extension (voice UI)
- `blog/` -- This blog post

## ElevenLabs Just Made This Easier

As of March 2026, ElevenLabs added native MCP tool support to their Conversational AI platform. That means you can connect an ElevenLabs voice agent directly to Webfuse's Session MCP Server — no LiveKit, no custom agent code.

The LiveKit approach gives you full control over the audio pipeline: custom VAD, model selection, streaming behavior. The ElevenLabs approach gives you zero infrastructure: configure tools in their dashboard, point at the MCP endpoint, done.

Both use the same Webfuse MCP tools. Same 13 browser actions. The difference is where the voice stack runs.

## The Bigger Picture

Voice agents are growing fast. Vapi, ElevenLabs, Retell, Deepgram, LiveKit — the voice infrastructure is mature. What's missing is the _action layer_.

A voice agent that can talk is a chatbot with good audio. A voice agent that can _browse_ is an assistant. It can check your calendar, fill out forms, look things up, compare prices, read documentation — anything a human does in a browser.

Webfuse provides that action layer via MCP. Any voice platform that supports MCP tool calls (and most do, or will soon) can connect to a live browser session and act.

The user doesn't install anything. The agent doesn't need a headless browser. It uses the user's real browser, with their real login state, in real time.

That's the future: voice in, browser actions, voice out. This demo is one implementation of that idea.
