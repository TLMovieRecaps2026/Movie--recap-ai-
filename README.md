
# Movie Recap AI Studio (MVP starter)

A phone-friendly web app starter for uploading a movie clip, generating a Burmese recap draft,
creating narration audio, and exporting subtitle files.

## Important
This is a working **starter/MVP**, not a one-click production service. AI video understanding,
Burmese text-to-speech, and accurate subtitle timing require provider credentials and testing.
The app is designed so those services can be connected without changing the user interface.

## Requirements
- Python 3.11+
- FFmpeg installed and available on PATH
- A Gemini API key (for video analysis)
- Optional TTS provider credentials for natural Burmese narration

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux/Android Termux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add GEMINI_API_KEY to .env
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
Open `http://127.0.0.1:8000`.

On Android, running a server locally is possible with Termux but is not the easiest route.
For reliable phone access, deploy the backend to a hosting provider after configuration.

## Current MVP workflow
1. Upload an MP4/MOV file.
2. Backend stores it and creates a job.
3. If `GEMINI_API_KEY` is configured, Gemini analyzes the uploaded video and drafts a Burmese recap.
4. User can edit the transcript in the browser.
5. Export TXT and a basic SRT draft.
6. Optional TTS adapter is intentionally separated; configure a Burmese-capable TTS provider before enabling MP3/MP4 export.

## Limitations to solve before public use
- Long videos should be chunked and analyzed with continuity notes; this MVP limits upload size and is intended for short test clips.
- Generated SRT from text alone is approximate. Accurate word-level subtitle timing requires speech alignment against the generated audio.
- Do not upload copyrighted material unless you have the rights or permission to process it.
- Add authentication, storage lifecycle rules, rate limits, and cost controls before public deployment.
