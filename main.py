
import os, uuid, shutil, mimetypes, time
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).parent
UPLOADS = ROOT / "uploads"
OUTPUTS = ROOT / "outputs"
UPLOADS.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)
MAX_MB = int(os.getenv("MAX_UPLOAD_MB", "500"))

app = FastAPI(title="Movie Recap AI Studio")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

JOBS = {}

@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")

@app.post("/api/upload")
async def upload_video(video: UploadFile = File(...)):
    suffix = Path(video.filename or "video.mp4").suffix.lower()
    if suffix not in {".mp4", ".mov", ".m4v", ".webm"}:
        raise HTTPException(400, "MP4, MOV, M4V သို့မဟုတ် WEBM ဖိုင်သာ တင်နိုင်ပါတယ်။")
    job_id = uuid.uuid4().hex[:12]
    target = UPLOADS / f"{job_id}{suffix}"
    size = 0
    with target.open("wb") as out:
        while chunk := await video.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_MB * 1024 * 1024:
                target.unlink(missing_ok=True)
                raise HTTPException(413, f"ဖိုင်အရွယ်အစား {MAX_MB} MB ထက် မကျော်ရပါ။")
            out.write(chunk)
    JOBS[job_id] = {
        "id": job_id, "filename": video.filename, "path": str(target),
        "status": "uploaded", "transcript": "", "error": ""
    }
    return {"job_id": job_id, "filename": video.filename, "size": size}

@app.post("/api/analyze/{job_id}")
async def analyze(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Video job မတွေ့ပါ။")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "put_your_api_key_here":
        raise HTTPException(400, "GEMINI_API_KEY မထည့်ရသေးပါ။ .env ဖိုင်ထဲမှာ API key ထည့်ပါ။")
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        uploaded = client.files.upload(file=job["path"])
        prompt = """
သင်သည် Professional Myanmar Movie Recap Script Writer ဖြစ်သည်။
ပေးထားသော ဗီဒီယိုကို ဇာတ်လမ်းအစမှအဆုံး သေချာလေ့လာပါ။
မြန်မာဘာသာဖြင့် သဘာဝကျပြီး အေးအေးဆေးဆေး နားထောင်ကောင်းသော Movie Recap transcript ရေးပါ။

စည်းမျဉ်းများ:
- ဇာတ်လမ်းအစီအစဉ် မပြောင်းပါနှင့်။ အရေးကြီးသော အဖြစ်အပျက်၊ အကြောင်းရင်း၊ တုံ့ပြန်မှုနှင့် ဇာတ်ကောင်စကားများ မချန်ခဲ့ပါနှင့်။
- အကျဉ်းချုပ်မလုပ်ပါနှင့်။ မြင်ရသောအချက်အလက်ကိုသာ ရေးပြီး မရှိသောအဖြစ်အပျက် မတီထွင်ပါနှင့်။
- စကားပြောခန်းများ၏ အဓိပ္ပာယ်ကို ထိန်းသိမ်းပြီး လိုအပ်သည့်နေရာတွင် တိုက်ရိုက်စကားပြောပုံစံ ထည့်ပါ။
- ဇာတ်လမ်းအချက်အလက်အသစ်မပေးသော အသေးအဖွဲ လှုပ်ရှားမှုဖော်ပြချက်များနှင့် ထပ်နေသောစာသားများကို ရှောင်ပါ။
- သဘာဝကျသော မြန်မာစကားပြောဟန်ကို သုံးပါ။ “သည်” ထက် “တယ်” ကို ဦးစားပေးပါ။
- Transcript ကို စာသားသက်သက် ထုတ်ပါ။ ခေါင်းစဉ်ရှည်၊ အချိန်တံဆိပ်၊ speaker label မထည့်ပါနှင့်။
- ဗီဒီယိုတစ်ခုလုံးကို မမြင်နိုင်/မဖတ်နိုင်ပါက ပြီးပြည့်စုံသကဲ့သို့ မပြောဘဲ ကန့်သတ်ချက်ကို ရှင်းပြပါ။
"""
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=[uploaded, prompt]
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("AI က transcript မထုတ်ပေးနိုင်ပါ။")
        job["transcript"] = text
        job["status"] = "completed"
        outpath = OUTPUTS / f"{job_id}.txt"
        outpath.write_text(text, encoding="utf-8")
        return {"job_id": job_id, "status": "completed", "transcript": text}
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        raise HTTPException(500, f"AI analysis မအောင်မြင်ပါ: {e}")

@app.get("/api/job/{job_id}")
def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job မတွေ့ပါ။")
    return {k: v for k, v in job.items() if k != "path"}

@app.post("/api/export/{job_id}")
async def export_text(job_id: str, payload: dict):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job မတွေ့ပါ။")
    transcript = str(payload.get("transcript", "")).strip()
    if not transcript:
        raise HTTPException(400, "Transcript မရှိပါ။")
    path = OUTPUTS / f"{job_id}.txt"
    path.write_text(transcript, encoding="utf-8")
    job["transcript"] = transcript
    return {"download": f"/api/download/{job_id}/txt"}

@app.get("/api/download/{job_id}/{kind}")
def download(job_id: str, kind: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job မတွေ့ပါ။")
    transcript = job.get("transcript", "")
    if kind == "txt":
        path = OUTPUTS / f"{job_id}.txt"
        if not path.exists():
            path.write_text(transcript, encoding="utf-8")
        return FileResponse(path, filename="myanmar-movie-recap.txt", media_type="text/plain")
    if kind == "srt":
        # Approximate placeholder: split into readable chunks. Accurate sync requires audio alignment.
        import re
        sentences = [s.strip() for s in re.split(r'(?<=[။!?])\s*', transcript) if s.strip()]
        def stamp(sec):
            h, rem = divmod(sec, 3600); m, s = divmod(rem, 60)
            return f"{h:02}:{m:02}:{s:02},000"
        blocks, cursor = [], 0
        for i, sentence in enumerate(sentences):
            duration = max(2, min(6, len(sentence) / 12))
            start, end = cursor, cursor + duration
            blocks.append(f"{i+1}\n{stamp(int(start))} --> {stamp(int(end))}\n{sentence}")
            cursor = end
        path = OUTPUTS / f"{job_id}.srt"
        path.write_text("\n\n".join(blocks), encoding="utf-8-sig")
        return FileResponse(path, filename="myanmar-subtitles-draft.srt", media_type="application/x-subrip")
    raise HTTPException(400, "txt သို့မဟုတ် srt ကိုသာ ယခု export လုပ်နိုင်ပါတယ်။")
