# Setup Guide

## Prerequisites

- Python 3.10+
- A [Webfuse](https://webfuse.com) Space with the Automation app enabled
- A [LiveKit Cloud](https://cloud.livekit.io) project (free tier works)
- An [OpenAI](https://platform.openai.com) API key
- An [ElevenLabs](https://elevenlabs.io) API key

## 1. Configure Environment

```bash
cp .env.example .env
```

Fill in all values:

| Variable | Where to get it |
|----------|----------------|
| `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `WEBFUSE_REST_KEY` | Webfuse Studio → Space → Settings → API Keys |
| `LIVEKIT_URL` | [LiveKit Cloud](https://cloud.livekit.io) → Project → Settings |
| `LIVEKIT_API_KEY` | LiveKit Cloud → Project → Settings → API Keys |
| `LIVEKIT_API_SECRET` | Same as above |
| `ELEVENLABS_API_KEY` | [ElevenLabs](https://elevenlabs.io/app/settings/api-keys) |

## 2. Install & Start the Agent

```bash
cd agent
pip install -r requirements.txt
python agent.py dev
```

The agent connects to LiveKit Cloud and waits for participants.

## 3. Start the Token Server

In a second terminal:

```bash
cd agent
pip install fastapi uvicorn
uvicorn token_server:app --port 8083
```

This generates room tokens for browser clients.

## 4. Deploy the Extension

Deploy the `extension/` folder to your Webfuse Space. The sidepanel opens automatically.

Set the extension environment variables:
- `TOKEN_URL` → `http://localhost:8083/token` (or your deployed URL)
- `LIVEKIT_URL` → Your LiveKit Cloud URL

## 5. Use It

1. Open your Webfuse Space in a browser
2. Navigate to any website
3. Click the microphone button in the sidepanel
4. Start talking: "What's on this page?"

## Changing the Voice

The default voice is "George" (ElevenLabs). To change it:

1. Browse voices at [elevenlabs.io/voice-library](https://elevenlabs.io/voice-library)
2. Copy the voice ID
3. Update `agent.py`: change the `voice` parameter in `elevenlabs.TTS()`

## Troubleshooting

### "Connection failed" in sidepanel
- Make sure the token server is running (`uvicorn token_server:app --port 8083`)
- Check that `TOKEN_URL` in the extension env points to the right address
- Check browser console for CORS errors

### Agent doesn't respond
- Check the agent terminal for errors
- Verify `WEBFUSE_REST_KEY` is correct and the Automation app is installed
- Make sure there's an active Webfuse session (browser tab open)

### No audio
- Allow microphone permissions when prompted
- Check that your speakers/headphones are working
- The agent needs a few seconds to process the first response
