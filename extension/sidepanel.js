const LIVEKIT_URL = browser.webfuseSession.env.LIVEKIT_URL || '';
const TOKEN_URL = browser.webfuseSession.env.TOKEN_URL || 'https://livekit-mcp.webfuse.it/token';
const micEl = document.getElementById('mic');
const statusEl = document.getElementById('status');
const transcriptEl = document.getElementById('transcript');

let connected = false;
let sessionId = null;

function addTranscript(role, text) {
  const el = document.createElement('div');
  el.className = `t-entry ${role}`;
  el.textContent = `${role === 'user' ? '🗣️' : '🤖'} ${text}`;
  transcriptEl.appendChild(el);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

async function toggleVoice() {
  if (connected) {
    // Disconnect
    connected = false;
    micEl.className = '';
    statusEl.textContent = 'Click to start';
    return;
  }

  statusEl.textContent = 'Connecting...';

  try {
    const info = await browser.webfuseSession.getSessionInfo();
    sessionId = info.sessionId;
  } catch (e) {
    statusEl.textContent = '❌ ' + e.message;
    return;
  }

  // Get LiveKit token from our server
  try {
    const resp = await fetch(`${TOKEN_URL}?session_id=${sessionId}`);
    const { token, url } = await resp.json();

    statusEl.textContent = '🎤 Listening... (speak to browse)';
    micEl.className = 'active';
    connected = true;

    addTranscript('agent', 'Connected! I can see your browser. What would you like me to do?');

    // In production, connect to LiveKit room here using livekit-client SDK
    // For demo, the agent auto-starts when a participant joins the room

  } catch (e) {
    statusEl.textContent = '❌ ' + e.message;
  }
}
