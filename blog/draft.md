---
title: "Build a Voice Agent That Controls a Live Browser"
description: "LiveKit voice pipeline + Webfuse MCP = an AI you talk to that browses for you. Say 'open the top story' and watch it click. Python. Real-time."
shortTitle: "LiveKit Voice + Webfuse MCP"
created: 2026-03-13
category: ai-agents
authorId: nicholas-piel
tags: ["livekit", "voice-ai", "mcp", "browser-automation", "webfuse", "python", "webrtc"]
featurePriority: 0
relatedLinks:
  - text: "Vercel AI SDK + Webfuse"
    href: "/blog/build-a-browsing-assistant-with-vercel-ai-sdk-and-webfuse"
    description: "TypeScript version with text chat."
  - text: "LangChain + Webfuse"
    href: "/blog/how-to-connect-langchain-to-a-live-browser-with-webfuse-mcp"
    description: "Python research agent with LangGraph."
  - text: "Session MCP Server Docs"
    href: "https://dev.webfu.se/session-mcp-server/"
    description: "Full reference for the 13 browser tools."
faqs:
  - question: "Do I need a LiveKit Cloud account?"
    answer: "Yes, for the managed version. LiveKit Cloud's free tier includes 10,000 participant minutes per month. You can also self-host LiveKit server for full control."
  - question: "What models does it use?"
    answer: "The default setup uses Deepgram Nova-3 for speech-to-text, GPT-4o for reasoning, and Cartesia Sonic-3 for text-to-speech. All through LiveKit Inference. You can swap any of these."
  - question: "Can I use ElevenLabs or other voices?"
    answer: "Yes. LiveKit Agents supports plugins for ElevenLabs, OpenAI TTS, Cartesia, and more. Change one line."
  - question: "How fast is the response?"
    answer: "Turn detection + STT takes about 500ms. LLM reasoning with tool calls takes 2-10 seconds depending on complexity. TTS starts streaming as soon as the first tokens arrive. Total: about 3-12 seconds from end of speech to hearing a response."
---

What if you could talk to your browser?

Not type a command. Not write a prompt. Just speak. "What's on this page?" And hear back: "The top story is about clean room software. It has 750 points and 291 comments. Want me to open it?"

Then say "yeah, open it" — and watch the browser click the link while the AI narrates what it finds.

<TldrBox title="TL;DR">

LiveKit handles real-time voice. Webfuse MCP handles browser control. Connect them with one `mcp_servers` parameter and you get a voice agent that sees and controls a live browser.

Source: [github.com/hummer-netizen/extension-livekit-mcp](https://github.com/hummer-netizen/extension-livekit-mcp)

Live demo: [webfu.se/+livekit-mcp/](https://webfu.se/+livekit-mcp/)

</TldrBox>

## The Architecture

```
You speak → WebRTC → STT → LLM (+ browser tools) → TTS → You hear
                              ↕
                     Webfuse MCP (click, type, read)
                              ↕
                     Your actual browser tab
```

The user talks to the agent through WebRTC. LiveKit handles turn detection, echo cancellation, and streaming audio. The LLM has access to 13 browser tools via Webfuse MCP. When you say "click the first link", GPT-4o decides to call `act_click`, Webfuse executes it in the user's browser, and the agent reads the new page and speaks a summary.

Everything happens in the user's real browser. Same tab, same cookies, same session.

## The Agent

The entire voice agent is one Python file:

```python
from livekit.agents import Agent, AgentSession, AgentServer, JobContext, JobProcess, cli, inference
from livekit.agents.llm.mcp import MCPServerHTTP
from livekit.plugins import silero

class BrowserAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are a voice-controlled browsing assistant.
            Keep responses under 3 sentences. You're speaking, not writing.
            Say what you see. Say what you're doing. Then pause."""
        )

server = AgentServer()

@server.rtc_session(agent_name="voice-browser")
async def voice_browser(ctx: JobContext):
    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3"),
        llm=inference.LLM(model="openai/gpt-4o"),
        tts=inference.TTS(model="cartesia/sonic-3"),
        vad=ctx.proc.userdata["vad"],
        mcp_servers=[
            MCPServerHTTP(
                url="https://session-mcp.webfu.se/mcp",
                headers={"Authorization": f"Bearer {REST_KEY}"},
            )
        ],
        max_tool_steps=10,
    )

    await session.start(room=ctx.room, agent=BrowserAgent())
    await session.say("Hey! I can see your browser. What should I look at?")
```

The key is `mcp_servers`. One line connects the voice agent to Webfuse's 13 browser tools. The LLM auto-discovers them via MCP and decides when to use them based on what the user says.

`inference.STT`, `inference.LLM`, and `inference.TTS` use LiveKit Inference — no separate API keys needed for individual providers. Everything runs through your LiveKit Cloud project.

## Voice-Specific Challenges

Building a voice agent that browses is different from a text chat that browses. A few things matter:

**Response length.** In text, you can send a 500-word summary. In voice, that's 3 minutes of talking. The system prompt enforces "under 3 sentences." The AI summarizes aggressively and asks if you want more.

**Tool call latency.** Reading a page takes 1-2 seconds. The user is waiting in silence. LiveKit's `preemptive_generation` helps — the LLM starts generating a response while the tool call is still running, so the first words come faster.

**Turn detection.** When the user says "open the first—no wait, the third link", the agent needs to handle interruptions. LiveKit's turn detector handles this natively. The AI stops what it's doing and processes the correction.

**Session identity.** The agent needs to know which browser tab to control. The Webfuse session ID is passed as room metadata when the frontend creates the LiveKit room. The agent reads it and passes it to every MCP tool call.

## The Frontend

The sidebar extension connects to the same LiveKit room. No custom audio streaming — LiveKit's client SDK handles everything:

```javascript
room = new LivekitClient.Room({ adaptiveStream: true });
await room.connect(wsUrl, token);

// Publish microphone
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
await room.localParticipant.publishTrack(stream.getAudioTracks()[0]);

// Receive agent audio
room.on(LivekitClient.RoomEvent.TrackSubscribed, (track) => {
  if (track.kind === 'audio') track.attach(); // plays automatically
});
```

The frontend is intentionally minimal — a mic button, a transcript, and a waveform visualizer. The browser does the heavy lifting through WebRTC.

A token server generates room-specific tokens and passes the Webfuse session ID as room metadata:

```python
@app.get("/token")
async def get_token(session_id: str):
    room_name = f"browser-{session_id[:20]}"
    await lk.room.create_room(CreateRoomRequest(
        name=room_name,
        metadata=session_id,  # Agent reads this to know which browser
    ))
    token = AccessToken(api_key, api_secret) \
        .with_identity(f"user-{session_id[:8]}") \
        .with_grants(VideoGrants(room_join=True, room=room_name))
    return {"token": token.to_jwt(), "url": ws_url}
```

## Swapping Voices

LiveKit Agents supports most major TTS providers:

```python
# LiveKit Inference (included with Cloud)
tts=inference.TTS(model="cartesia/sonic-3", voice="...")

# ElevenLabs (rich, expressive voices)
from livekit.plugins import elevenlabs
tts=elevenlabs.TTS(model="eleven_turbo_v2", voice="George")

# OpenAI TTS
from livekit.plugins import openai
tts=openai.TTS(model="tts-1", voice="nova")
```

The same goes for STT and LLM. The voice pipeline is modular — swap any component without changing the rest.

::ArticleSignupCta
---
heading: "Give your voice agent a browser"
subtitle: "Webfuse connects LiveKit voice agents to live browser sessions via MCP. Build voice-controlled browsing in Python."
---
::

## Beyond Browsing

The demo browses Hacker News by voice. The pattern works for anything a human does in a browser:

- **Voice-driven customer support.** "Pull up this customer's account." The agent navigates the CRM, reads the data, and explains it to the support rep — hands-free.
- **Accessibility.** Users who can't easily type or click can navigate any website by voice.
- **Field workers.** Technicians with their hands full can voice-control dashboards, forms, and documentation.
- **Meeting assistants.** "Look up last quarter's numbers" — the agent opens the spreadsheet and reads the relevant cells while you stay in the meeting.

Same agent code. Different instructions. Different browser target.

## Source Code

Everything is on GitHub: [hummer-netizen/extension-livekit-mcp](https://github.com/hummer-netizen/extension-livekit-mcp)

- `agent/agent.py` — Voice agent with MCP browser tools
- `agent/token_server.py` — Room token generation
- `extension/` — Sidebar UI (mic button, transcript, visualizer)

Try the demo: [webfu.se/+livekit-mcp/](https://webfu.se/+livekit-mcp/)

## The Simpler Alternative: ElevenLabs + Webfuse (Zero Code)

If self-hosting a LiveKit agent feels like too much, ElevenLabs just shipped native MCP support in their Conversational AI platform. That means you can connect an ElevenLabs voice agent to Webfuse with zero code:

1. Go to ElevenLabs → Agents → Integrations → Add Custom MCP Server
2. Server URL: `https://session-mcp.webfu.se/mcp`
3. Secret Token: your Webfuse REST key
4. Done

The ElevenLabs agent gets the same 13 browser tools. No LiveKit, no Python, no server.

**When to use LiveKit (this demo):**
- You need full control over the agent logic
- You want custom voice models or VAD
- You're building for production with specific latency requirements
- You need custom tool orchestration beyond what MCP provides

**When to use ElevenLabs:**
- You want the fastest path from idea to working demo
- You're prototyping or building a showcase
- You need natural-sounding voices out of the box
- You want a managed platform with no infrastructure

Both approaches use Webfuse as the browser layer. The difference is who runs the voice pipeline.
