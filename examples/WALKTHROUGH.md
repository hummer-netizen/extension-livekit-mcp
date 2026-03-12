# Demo Walkthrough

Try these voice commands after clicking the microphone in the Webfuse sidebar.

## 1. Explore a Page

Navigate to any website in your Webfuse session, then:

**Say:** "What's on this page?"

The agent reads the DOM, summarizes the content, and speaks it back. You'll hear something like: "I can see a Wikipedia article about Amsterdam. There are sections on history, geography, and culture. The infobox shows a population of about 933,000."

## 2. Navigate and Read

**Say:** "Go to wikipedia.org and search for 'Eiffel Tower'"

Watch the browser navigate to Wikipedia, type in the search box, and press Enter. The agent narrates each step as it happens.

**Say:** "Read me the first paragraph."

The agent reads the intro section and speaks a summary.

## 3. Compare Information

**Say:** "What's the height of the Eiffel Tower?"

After getting the answer:

**Say:** "Now find the height of the Empire State Building and tell me which one is taller."

The agent navigates to a new page, extracts the data, and gives you the comparison by voice.

## 4. Fill a Form

Navigate to a contact form or search page.

**Say:** "Fill in the email field with test@example.com"

**Say:** "Type 'AI browser agents' in the search box and press Enter"

## 5. Accessibility Check

**Say:** "Check the accessibility tree on this page. Are there any issues?"

The agent reads the accessibility tree and reports back verbally.

## Tips for Voice Interaction

- **Keep it conversational.** Talk like you would to a person browsing for you.
- **Be specific when needed.** "Click the blue button that says Submit" is better than "click submit."
- **Ask follow-ups.** The agent remembers context: "Tell me more about that" works after a summary.
- **Take over anytime.** Grab the mouse and browse manually, then speak again to hand back control.
- **Short commands work best.** The agent responds faster to focused requests than long multi-step ones.

## What Happens Under the Hood

1. You speak → LiveKit captures audio, sends to cloud
2. Whisper STT converts speech to text
3. GPT-4o decides what to do (reason + tool selection)
4. Webfuse MCP tools execute browser actions (navigate, click, read, etc.)
5. GPT-4o summarizes the result
6. ElevenLabs TTS converts the response to speech
7. LiveKit streams audio back to your speaker

All of this happens in ~2-4 seconds for simple commands.
