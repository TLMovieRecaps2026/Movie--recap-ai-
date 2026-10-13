import os, uuid, json, shutil, subprocess, asyncio, re
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()
ROOT = Path(__file__).parent.resolve()
DATA = ROOT / "jobs"
DATA.mkdir(exist_ok=True)
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "700"))
MAX_FRAMES = int(os.getenv("MAX_FRAMES", "18"))
app = FastAPI(title="Movie Recap AI")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

JOBS = {}
def ffmpeg_bin():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg/ffprobe မတွေ့ပါ။ FFmpeg ကို install လုပ်ပြီး PATH ထဲထည့်ပါ။")
def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError((p.stderr or "Command failed")[-2500:])
    return p.stdout
def probe_duration(path):
    ffmpeg_bin()
    out = run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)])
    return max(0.1, float(out.strip()))
def srt_time(seconds):
    ms = int(max(0, seconds) * 1000)
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
def clean_text(s):
    return re.sub(r"\n{3,}", "\n\n", (s or "")).strip()

async def ai_make_script(job, video_path, mode, voice, language_hint):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY မထည့်ရသေးပါ။ .env ဖိုင်ထဲတွင် API key ထည့်ပါ။")
    from openai import OpenAI
    client = OpenAI(api_key=key)
    job["status"] = "ဗီဒီယို Scene များကို စစ်ဆေးနေသည်"
    job["progress"] = 12
    # Extract a small, bounded set of frames evenly across the video.
    duration = probe_duration(video_path)
    frame_dir = DATA / job["id"] / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    count = max(4, min(MAX_FRAMES, int(duration // 12) + 1))
    frames = []
    for i in range(count):
        sec = min(duration - 0.1, (duration * i / max(1, count - 1)))
        out = frame_dir / f"frame_{i:03}.jpg"
        run(["ffmpeg","-y","-ss",str(sec),"-i",str(video_path),"-frames:v","1","-vf","scale=768:-2","-q:v","5",str(out)])
        if out.exists() and out.stat().st_size:
            import base64
            frames.append({"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+base64.b64encode(out.read_bytes()).decode()}})
    job["progress"] = 24
    job["status"] = "မြန်မာ ဇာတ်ကြောင်းစာသား ဖန်တီးနေသည်"
    mode_desc = ("Natural Burmese movie recap narrator script" if mode == "narrator" else
                 "Burmese dialogue-style script that describes character exchanges; do not invent exact quotes when not visible/audible")
    prompt = f"""You are a careful movie recap scriptwriter. Analyze these video frames in chronological order.
Write a coherent, concise Burmese-language voice-over script describing only what the frames support.
Mode: {mode_desc}. Voice preference: {voice}. {language_hint}
Do not claim unseen details as facts. Do not include timestamps, speaker labels, markdown, or production notes.
Output only the Burmese spoken script. Use natural spoken Burmese and connect scenes in order."""
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_VISION_MODEL","gpt-4o-mini"),
        messages=[{"role":"user","content":[{"type":"text","text":prompt},*frames]}],
        temperature=0.4
    )
    script = clean_text(response.choices[0].message.content)
    if len(script) < 20:
        raise RuntimeError("AI က narration စာသား မထုတ်ပေးနိုင်ပါ။ နောက်တစ်ကြိမ် စမ်းကြည့်ပါ။")
    (DATA/job["id"]/"transcript.txt").write_text(script, encoding="utf-8")
    job["progress"] = 38
    job["status"] = "မြန်မာ AI Voice ဖန်တီးနေသည်"
    # TTS may have language-specific limitations depending on selected model/voice.
    speech = client.audio.speech.create(
        model=os.getenv("OPENAI_TTS_MODEL","gpt-4o-mini-tts"),
        voice=voice if voice in ["alloy","ash","ballad","coral","echo","fable","onyx","nova","sage","shimmer"] else "alloy",
        input=script,
        instructions="Speak clearly and naturally in Burmese (Myanmar language), with expressive movie-recap narration."
    )
    audio_path = DATA/job["id"]/"voice.mp3"
    speech.stream_to_file(audio_path)
    return script, audio_path

def make_srt(script, duration, path):
    # Approximate line segmentation proportional to Burmese character count.
    chunks = []
    for paragraph in script.splitlines():
        paragraph = paragraph.strip()
        if not paragraph: continue
        # split into ~90-character chunks without trying to tokenize Burmese incorrectly
        while len(paragraph) > 90:
            cut = paragraph.rfind("။", 0, 90)
            if cut < 35: cut = paragraph.rfind(" ", 0, 90)
            if cut < 35: cut = 90
            chunks.append(paragraph[:cut+1].strip())
            paragraph = paragraph[cut+1:].strip()
        if paragraph: chunks.append(paragraph)
    if not chunks: chunks = [script]
    weights = [max(1,len(c)) for c in chunks]
    total = sum(weights)
    # keep a small end margin
    usable = max(1, duration - 0.15)
    cursor = 0.0
    out = []
    for idx, (chunk, weight) in enumerate(zip(chunks, weights), 1):
        end = min(usable, cursor + usable * weight / total)
        if end <= cursor: end = cursor + 0.2
        out.extend([str(idx), f"{srt_time(cursor)} --> {srt_time(end)}", chunk, ""])
        cursor = end
    path.write_text("\n".join(out), encoding="utf-8-sig")

def render_job(job, video_path, mode, voice, ratio, color_correct, subtitles):
    job["status"] = "Video ကို ပြင်ဆင်နေသည်"
    job["progress"] = 50
    work = DATA/job["id"]
    script, audio_path = asyncio.run(ai_make_script(job, video_path, mode, voice, "Keep narration faithful to the supplied frames."))
    duration = probe_duration(video_path)
    srt_path = work/"captions.srt"
    make_srt(script, duration, srt_path)
    job["progress"] = 65
    job["status"] = "Video ratio နှင့် အရောင်ကို ပြင်ဆင်နေသည်"
    filters = []
    if color_correct:
        filters.append("eq=contrast=1.04:saturation=1.08:brightness=0.01")
    if ratio == "9:16":
        filters.append("scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2")
    elif ratio == "1:1":
        filters.append("scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2")
    elif ratio == "3:4":
        filters.append("scale=1080:1440:force_original_aspect_ratio=decrease,pad=1080:1440:(ow-iw)/2:(oh-ih)/2")
    else:
        filters.append("scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2")
    if subtitles:
        # use escaped absolute path for ffmpeg subtitles filter
        srt_escaped = str(srt_path.resolve()).replace("\\","/").replace(":","\\:").replace("'","\\'")
        filters.append(f"subtitles='{srt_escaped}':force_style='FontName=Noto Sans Myanmar,FontSize=22,Outline=2,Shadow=1,Alignment=2,MarginV=45'")
    vf = ",".join(filters)
    output = work/"movie_recap.mp4"
    job["progress"] = 74
    job["status"] = "အသံနှင့် Video ကို ပေါင်းစပ်နေသည်"
    cmd = ["ffmpeg","-y","-i",str(video_path),"-i",str(audio_path),"-vf",vf,
           "-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","veryfast","-crf","23",
           "-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(output)]
    run(cmd)
    job["progress"] = 100
    job["status"] = "ပြီးပါပြီ"
    job["done"] = True
    job["files"] = {"video":"/download/"+job["id"]+"/video","srt":"/download/"+job["id"]+"/srt","transcript":"/download/"+job["id"]+"/transcript"}
    job["script"] = script

@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT/"static"/"index.html").read_text(encoding="utf-8")

@app.post("/api/jobs")
async def create_job(background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    mode: str = Form("narrator"),
    voice: str = Form("alloy"),
    ratio: str = Form("9:16"),
    color_correct: bool = Form(True),
    subtitles: bool = Form(True)):
    if not video.filename:
        raise HTTPException(400, "Video ဖိုင်ကို ရွေးပါ။")
    if not video.filename.lower().endswith((".mp4",".mov",".mkv",".webm",".avi",".m4v")):
        raise HTTPException(400, "MP4/MOV/MKV/WEBM/AVI ဖိုင်ကို အသုံးပြုပါ။")
    jid = uuid.uuid4().hex[:12]
    folder = DATA/jid
    folder.mkdir(parents=True)
    dest = folder/("source" + Path(video.filename).suffix.lower())
    size = 0
    with dest.open("wb") as f:
        while True:
            chunk = await video.read(1024*1024)
            if not chunk: break
            size += len(chunk)
            if size > MAX_UPLOAD_MB*1024*1024:
                shutil.rmtree(folder, ignore_errors=True)
                raise HTTPException(413, f"ဖိုင်အရွယ်အစား {MAX_UPLOAD_MB} MB ထက် မကျော်ရပါ။")
            f.write(chunk)
    job = {"id":jid,"status":"စတင်ရန် စီစဉ်နေသည်","progress":2,"done":False,"error":None}
    JOBS[jid] = job
    def work():
        try:
            render_job(job,dest,mode,voice,ratio,color_correct,subtitles)
        except Exception as e:
            job["error"] = str(e)
            job["status"] = "အမှားဖြစ်နေသည်"
            job["done"] = True
    background_tasks.add_task(work)
    return {"job_id":jid}

@app.get("/api/jobs/{jid}")
def job_status(jid: str):
    if jid not in JOBS: raise HTTPException(404,"Job မတွေ့ပါ။")
    j = JOBS[jid]
    return {k:j.get(k) for k in ["id","status","progress","done","error","files","script"]}

@app.get("/download/{jid}/{kind}")
def download(jid: str, kind: str):
    if jid not in JOBS: raise HTTPException(404,"Job မတွေ့ပါ။")
    folder = DATA/jid
    names = {"video":("movie_recap.mp4","video/mp4"),"srt":("captions.srt","application/x-subrip"),"transcript":("transcript.txt","text/plain; charset=utf-8")}
    if kind not in names: raise HTTPException(404,"ဖိုင်အမျိုးအစား မမှန်ပါ။")
    name, media = names[kind]
    path = folder/name
    if not path.exists(): raise HTTPException(404,"ဖိုင် မပြင်ဆင်ရသေးပါ။")
    return FileResponse(path, media_type=media, filename=name)
