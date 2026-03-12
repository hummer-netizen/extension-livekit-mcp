/**
 * Voice Browser Agent — LiveKit Sidepanel
 *
 * Connects to a LiveKit room via LiveKit's JS client SDK (loaded from CDN).
 * Sends/receives audio to/from the voice agent.
 */

const TOKEN_URL = browser.webfuseSession.env.TOKEN_URL || 'https://livekit-mcp.webfuse.it/token';
const micEl = document.getElementById('mic');
const statusEl = document.getElementById('status');
const transcriptEl = document.getElementById('transcript');

let room = null;
let connected = false;
let sessionId = null;
let localAudioTrack = null;

function addTranscript(role, text) {
  const el = document.createElement('div');
  el.className = `t-entry ${role}`;
  el.textContent = `${role === 'user' ? '🗣️' : '🤖'} ${text}`;
  transcriptEl.appendChild(el);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

function setStatus(msg) {
  statusEl.textContent = msg;
}

async function disconnect() {
  if (room) {
    await room.disconnect();
    room = null;
  }
  if (localAudioTrack) {
    localAudioTrack.stop();
    localAudioTrack = null;
  }
  connected = false;
  micEl.className = '';
  setStatus('Click to start');
}

async function connect() {
  setStatus('Getting session info...');

  try {
    const info = await browser.webfuseSession.getSessionInfo();
    sessionId = info.sessionId || info.session_id;
  } catch (e) {
    setStatus('❌ Could not get session: ' + e.message);
    return;
  }

  setStatus('Getting room token...');

  let token, url;
  try {
    const resp = await fetch(`${TOKEN_URL}?session_id=${sessionId}`);
    if (!resp.ok) throw new Error(`Token server ${resp.status}`);
    const data = await resp.json();
    token = data.token;
    url = data.url;
  } catch (e) {
    setStatus('❌ Token error: ' + e.message);
    return;
  }

  setStatus('Connecting to voice...');

  try {
    // Use LiveKit JS SDK (loaded from CDN in sidepanel.html)
    room = new LivekitClient.Room({
      adaptiveStream: true,
      dynacast: true,
    });

    // Handle agent audio output
    room.on(LivekitClient.RoomEvent.TrackSubscribed, (track, pub, participant) => {
      if (track.kind === 'audio') {
        const audioEl = track.attach();
        document.body.appendChild(audioEl);
        micEl.className = 'speaking';
      }
    });

    room.on(LivekitClient.RoomEvent.TrackUnsubscribed, (track) => {
      track.detach().forEach(el => el.remove());
      if (connected) micEl.className = 'active';
    });

    // Handle data messages (transcripts from agent)
    room.on(LivekitClient.RoomEvent.DataReceived, (payload, participant) => {
      try {
        const msg = JSON.parse(new TextDecoder().decode(payload));
        if (msg.type === 'transcript') {
          addTranscript(msg.role || 'agent', msg.text);
        }
      } catch (_) {}
    });

    room.on(LivekitClient.RoomEvent.Disconnected, () => {
      disconnect();
    });

    // Connect to room
    await room.connect(url.replace('https://', 'wss://'), token);

    // Publish microphone
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    localAudioTrack = stream.getAudioTracks()[0];
    const localTrackPub = await room.localParticipant.publishTrack(localAudioTrack, {
      source: LivekitClient.Track.Source.Microphone,
    });

    connected = true;
    micEl.className = 'active';
    setStatus('🎤 Listening... speak to browse');
    addTranscript('agent', 'Connected! Speak to control the browser.');

  } catch (e) {
    setStatus('❌ Connection failed: ' + e.message);
    console.error('LiveKit connect error:', e);
  }
}

async function toggleVoice() {
  if (connected) {
    await disconnect();
  } else {
    await connect();
  }
}

// Expose globally for onclick
window.toggleVoice = toggleVoice;
