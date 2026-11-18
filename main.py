import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

@app.get("/")
def home():
    html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie Recap AI Studio</title>
    <style>
        body { font-family: sans-serif; background: #f0f4f8; text-align: center; padding: 20px; }
        .box { background: white; padding: 20px; border-radius: 10px; max-width: 400px; margin: auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        input, button { width: 100%; margin-top: 15px; padding: 10px; font-size: 16px; }
        button { background: #22c55e; color: white; border: none; border-radius: 5px; cursor: pointer; }
        #loading { display: none; margin-top: 15px; color: #0284c7; font-weight: bold; }
        #progressBar { width: 100%; background: #e2e8f0; border-radius: 5px; margin-top: 10px; display: none; overflow: hidden; }
        #progressFill { width: 0%; height: 20px; background: #0284c7; text-align: center; color: white; font-size: 12px; line-height: 20px; }
        #result { margin-top: 20px; white-space: pre-wrap; text-align: left; background: #f8fafc; padding: 10px; border-radius: 5px; border: 1px solid #cbd5e1; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Movie Recap AI Studio</h2>
        <p>သင့်ရဲ့ဗီဒီယိုကို ရွေးချယ်ပြီး ဇာတ်ညွှန်းထုတ်ပါ</p>
        <input type="file" id="videoFile" accept="video/*">
        <button onclick="uploadVideo()">ဇာတ်ညွှန်းထုတ်ရန်</button>
        <div id="progressBar"><div id="progressFill">0%</div></div>
        <div id="loading">AI ဇာတ်ညွှန်း စဉ်းစားနေပါသည်... (ခဏစောင့်ပါ)</div>
        <div id="result"></div>
    </div>
    <script>
        async function uploadVideo() {
            const fileInput = document.getElementById('videoFile');
            const resultDiv = document.getElementById('result');
            const loadingDiv = document.getElementById('loading');
            const progressBar = document.getElementById('progressBar');
            const progressFill = document.getElementById('progressFill');

            if (fileInput.files.length === 0) {
                alert('ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင် ရွေးချယ်ပါ');
                return;
            }

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);

            progressBar.style.display = 'block';
            progressFill.style.width = '0%';
            progressFill.innerText = '0%';
            resultDiv.innerText = '';

            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/process-video', true);

            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    const percentComplete = Math.round((e.loaded / e.total) * 100);
                    progressFill.style.width = percentComplete + '%';
                    progressFill.innerText = percentComplete + '%';
                }
            };

            xhr.onloadstart = function() {
                progressBar.style.display = 'block';
            };

            xhr.onload = function() {
                progressBar.style.display = 'none';
                loadingDiv.style.display = 'block';
            };

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
        sample_script = "ဇာတ်လမ်းအစ - ဒီရုပ်ရှင်လေးမှာတော့ မထင်မှတ်ထားတဲ့ အဖြစ်အပျက်တွေနဲ့ စတင်ခဲ့ပါတယ်...\n\nဇာတ်ကောင်တွေက အကြပ်အတည်းကို ရင်ဆိုင်ရင်း ရှေ့ဆက်ကြပုံကို စိတ်ဝင်စားစရာ တွေ့ရပါတယ်။\n\nဇာတ်သိမ်းပိုင်း - အားလုံးကတော့ ပျော်စရာကောင်းတဲ့ အဆုံးသတ်နဲ့ ပြီးဆုံးသွားပါတယ် ဆရာ။"
        return {"success": True, "script": sample_script}
    except Exception as e:
        return {"success": False, "error": str(e)}
