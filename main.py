import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import google.generativeai as genai

api_key = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6J7_0yHFUMce-70DRtDFjRdknyVD1fhHwvWdD0ehH3sMA")
genai.configure(api_key=api_key)

app = FastAPI()

@app.get("/")
def home():
    html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JT Movie Recap AI Studio</title>
    <style>
        body { font-family: sans-serif; background: #f0f4f8; text-align: center; padding: 20px; }
        .box { background: white; padding: 20px; border-radius: 10px; max-width: 400px; margin: auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        input, button { width: 100%; margin-top: 15px; padding: 10px; font-size: 16px; }
        button { background: #22c55e; color: white; border: none; border-radius: 5px; cursor: pointer; }
        #loading { display: none; margin-top: 15px; color: #0284c7; font-weight: bold; }
        #result { margin-top: 20px; white-space: pre-wrap; text-align: left; background: #f8fafc; padding: 10px; border-radius: 5px; border: 1px solid #cbd5e1; }
    </style>
</head>
<body>
    <div class="box">
        <h2>JT Movie Recap AI Studio</h2>
        <p>သင့်ရဲ့ဗီဒီယိုကို ရွေးချယ်ပြီး ဇာတ်ညွှန်းထုတ်ပါ</p>
        <input type="file" id="videoFile" accept="video/*">
        <button onclick="uploadVideo()">ဇာတ်ညွှန်းထုတ်ရန်</button>
        <div id="loading">AI ဇာတ်ညွှန်း စဉ်းစားနေပါသည်... (ခဏစောင့်ပါ)</div>
        <div id="result"></div>
    </div>
    <script>
        async function uploadVideo() {
            const fileInput = document.getElementById('videoFile');
            const resultDiv = document.getElementById('result');
            const loadingDiv = document.getElementById('loading');

            if (fileInput.files.length === 0) {
                alert('ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင် ရွေးချယ်ပါ');
                return;
            }

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);

            loadingDiv.style.display = 'block';
            resultDiv.innerText = '';

            try {
                const response = await fetch('/process-video', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                loadingDiv.style.display = 'none';
                if (data.success) {
                    resultDiv.innerText = data.script;
                } else {
                    resultDiv.innerText = 'Error: ' + data.error;
                }
            } catch (err) {
                loadingDiv.style.display = 'none';
                resultDiv.innerText = 'Failed to connect server: ' + err.message;
            }
        }
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_code)

@app.post("/process-video")
async def process_video(file: UploadFile = File(...)):
    try:
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        video_file = genai.upload_file(path=temp_file_path)
        
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        prompt = "ဒီဗီဒီယိုဖိုင်ကို ကြည့်ပြီး ဇာတ်လမ်းအစ၊ အလယ်၊ အဆုံး ပြီးပြည့်စုံတဲ့ မြန်မာလို ရုပ်ရှင်ဇာတ်ညွှန်း (Movie Recap) ကို သဘာဝကျကျ အသေးစိတ် ရေးပေးပါ။"
        
        response = model.generate_content([video_file, prompt])
        script_text = response.text

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        return {"success": True, "script": script_text}
    except Exception as e:
        return {"success": False, "error": str(e)}
