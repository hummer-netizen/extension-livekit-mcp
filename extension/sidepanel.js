/**
 * Voice Browser Agent — LiveKit + Webfuse
 *
 * Connects to a LiveKit room, sends microphone audio to the voice agent,
 * receives audio responses, and shows a live transcript.
 */

const TOKEN_URL = browser.webfuseSession.env.TOKEN_URL || 'https://livekit-mcp.webfuse.it/token';
const micEl = document.getElementById('mic');
const statusEl = document.getElementById('status');
const transcriptEl = document.getElementById('transcript');
const vizEl = document.getElementById('viz');
const promptsEl = document.getElementById('prompts');
const bars = vizEl.querySelectorAll('.bar');

let room = null;
let connected = false;
let sessionId = null;
let localAudioTrack = null;
let analyser = null;
let vizInterval = null;

function setStatus(msg, cls) {
  statusEl.textContent = msg;
  statusEl.className = cls || '';
}

function addTranscript(role, text) {
  if (!text || !text.trim()) return;
  const el = document.createElement('div');
  el.className = 't-entry ' + role;
  el.textContent = text;
  transcriptEl.appendChild(el);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

function showToolUse(name) {
  const names = {
    see_domSnapshot: 'reading the page...',
    act_click: 'clicking...',
    act_type: 'typing...',
    navigate: 'navigating...',
    act_scroll: 'scrolling...',
  };
  addTranscript('tool', names[name] || ('using ' + name));
}

function startViz(stream, speaking) {
  if (vizInterval) clearInterval(vizInterval);

  try {
    const actx = new AudioContext();
    const src = actx.createMediaStreamSource(stream);
    analyser = actx.createAnalyser();
    analyser.fftSize = 32;
    src.connect(analyser);

    const data = new Uint8Array(analyser.frequencyBinCount);

    vizEl.className = speaking ? 'viz speaking' : 'viz';
    vizInterval = setInterval(() => {
      analyser.getByteFrequencyData(data);
      bars.forEach((bar, i) => {
        const val = data[i * 3] || 0;
        bar.style.height = Math.max(4, val / 5) + 'px';
      });
    }, 50);
  } catch (e) {
    console.warn('Viz error:', e);
  }
}

function stopViz() {
  if (vizInterval) { clearInterval(vizInterval); vizInterval = null; }
  bars.forEach(b => b.style.height = '4px');
  vizEl.className = 'viz';
}

async function disconnect() {
  stopViz();
  if (room) { await room.disconnect(); room = null; }
  if (localAudioTrack) { localAudioTrack.stop(); localAudioTrack = null; }
  connected = false;
  micEl.className = '';
  setStatus('tap to start');
  if (promptsEl) promptsEl.style.display = '';
}

async function connect() {
  setStatus('connecting...');

  // Get Webfuse session
  try {
    const info = await browser.webfuseSession.getSessionInfo();
    sessionId = info.sessionId || info.session_id;
  } catch (e) {
    setStatus('no session: ' + e.message, 'error');
    return;
  }

  // Get LiveKit token
  let token, wsUrl;
  try {
    const resp = await fetch(TOKEN_URL + '?session_id=' + sessionId);
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    token = data.token;
    wsUrl = data.url;
  } catch (e) {
    setStatus('token error: ' + e.message, 'error');
    return;
  }

  setStatus('joining room...');

  try {
    room = new LivekitClient.Room({
      adaptiveStream: true,
      dynacast: true,
    });

    // Agent audio output
    room.on(LivekitClient.RoomEvent.TrackSubscribed, (track, pub, participant) => {
      if (track.kind === 'audio' && participant.identity !== room.localParticipant.identity) {
        const audioEl = track.attach();
        document.body.appendChild(audioEl);
        micEl.className = 'speaking';

        // Visualize agent speech
        const stream = new MediaStream([track.mediaStreamTrack]);
        startViz(stream, true);
      }
    });

    room.on(LivekitClient.RoomEvent.TrackUnsubscribed, (track) => {
      track.detach().forEach(el => el.remove());
      if (connected) {
        micEl.className = 'active';
        stopViz();
      }
    });

    // Transcription events
    room.on(LivekitClient.RoomEvent.TranscriptionReceived, (segments, participant) => {
      for (const seg of segments) {
        if (seg.final && seg.text && seg.text.trim()) {
          const isAgent = participant && participant.identity !== room.localParticipant.identity;
          addTranscript(isAgent ? 'agent' : 'user', seg.text);
        }
      }
    });

    // Data messages (tool use, etc.)
    room.on(LivekitClient.RoomEvent.DataReceived, (payload, participant) => {
      try {
        const msg = JSON.parse(new TextDecoder().decode(payload));
        if (msg.type === 'tool_use') showToolUse(msg.tool);
        else if (msg.type === 'transcript') addTranscript(msg.role || 'agent', msg.text);
      } catch (_) {}
    });

    room.on(LivekitClient.RoomEvent.Disconnected, () => disconnect());

    // Connect
    await room.connect(wsUrl, token);

    // Publish microphone
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    localAudioTrack = stream.getAudioTracks()[0];
    await room.localParticipant.publishTrack(localAudioTrack, {
      source: LivekitClient.Track.Source.Microphone,
    });

    connected = true;
    micEl.className = 'active';
    setStatus('listening...', 'active');

    // Hide prompt chips after connecting
    if (promptsEl) promptsEl.style.display = 'none';

    // Start mic visualizer
    startViz(stream, false);

  } catch (e) {
    setStatus('failed: ' + e.message, 'error');
    console.error('LiveKit error:', e);
  }
}

async function toggleVoice() {
  if (connected) await disconnect();
  else await connect();
}

window.toggleVoice = toggleVoice;
