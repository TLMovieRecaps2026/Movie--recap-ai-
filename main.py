import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import google.generativeai as genai

# === သင့်ရဲ့ လျှို့ဝှက်သော့ကို အောက်တွင် ထည့်ပါ =
API_KEY = AQ.Ab8RN6JkK-Dr0Qr3c45BVqrZrZVUcHFWWlJ0AGdbn34GpbigxA

genai.configure(api_key=API_KEY)

app = FastAPI()

@app.get("/")
def home():
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body { background-color: #f0f4f8; text-align: center; font-family: sans-serif; padding: 20px;}
      .box { background: white; padding: 20px; border-radius: 10px; max-width: 500px; margin: auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1);}
      button { background: #2ecc71; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 16px; margin-top: 10px; cursor: pointer;}
      button:disabled { background: #95a5a6; cursor: not-allowed; }
      #progress-container { width: 100%; background-color: #e0e0e0; border-radius: 5px; margin-top: 15px; display: none; overflow: hidden;}
      #progress-bar { width: 0%; height: 28px; background-color: #e67e22; text-align: center; line-height: 28px; color: white; font-weight: bold; transition: width 0.3s; font-size: 14px;}
      #result { margin-top: 20px; text-align: left; background: #eee; padding: 15px; border-radius: 5px; white-space: pre-wrap; font-size: 14px; line-height: 1.6;}
    </style>
    </head>
    <body>
      <div class="box">
          <h2>Movie Recap AI Studio</h2>
          <p>သင့်ရဲ့ ဗီဒီယိုကို ရွေးချယ်ပြီး ဇာတ်ညွှန်းထုတ်ပါ</p>
          <input type="file" id="video-upload" accept="video/*">
          <br><br>
          <button id="submit-btn" onclick="uploadVideo()">ဇာတ်ညွှန်းထုတ်ရန်</button>
          
          <div id="progress-container">
              <div id="progress-bar">0%</div>
          </div>
          
          <div id="result"></div>
      </div>

      <script>
        function uploadVideo() {
             const input = document.getElementById('video-upload');
             if (input.files.length === 0) {
                 alert("ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင် တစ်ခုခုကို အရင်ရွေးချယ်ပေးပါ။"); return;
             }
             
             document.getElementById('submit-btn').disabled = true;
             document.getElementById('result').innerText = '';
             
             const progressContainer = document.getElementById('progress-container');
             const progressBar = document.getElementById('progress-bar');
             progressContainer.style.display = 'block';
             progressBar.style.width = '0%';
             progressBar.innerText = '0%';
             
             const formData = new FormData();
             formData.append("file", input.files[0]);

             const xhr = new XMLHttpRequest();
             xhr.open("POST", "/generate", true);
             
             xhr.upload.onprogress = function(e) {
                 if (e.lengthComputable) {
                     let percentComplete = Math.round((e.loaded / e.total) * 100);
                     progressBar.style.width = percentComplete + '%';
                     progressBar.innerText = percentComplete + '% (ဗီဒီယို တင်နေပါသည်)';
                     
                     if (percentComplete === 100) {
                         progressBar.style.backgroundColor = '#3498db';
                         progressBar.innerText = 'AI ဇာတ်ညွှန်း စဉ်းစားနေပါသည်... (ခဏစောင့်ပါ)';
                     }
                 }
             };
             
             xhr.onload = function() {
                 progressContainer.style.display = 'none';
                 document.getElementById('submit-btn').disabled = false;
                 progressBar.style.backgroundColor = '#e67e22'; // အရောင် ပြန်ပြောင်းရန်
                 
                 if (xhr.status === 200) {
                     const data = JSON.parse(xhr.responseText);
                     document.getElementById('result').innerText = data.script || data.error;
                 } else {
                     document.getElementById('result').innerText = "ချိတ်ဆက်မှု ပြတ်တောက်သွားပါသည်။";
                 }
             };
             
             xhr.onerror = function() {
                 progressContainer.style.display = 'none';
                 document.getElementById('submit-btn').disabled = false;
                 document.getElementById('result').innerText = "အမှားအယွင်း ဖြစ်ပွားခဲ့ပါသည်။";
             };
             
             xhr.send(formData);
        }
      </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_code)

@app.post("/generate")
async def generate(file: UploadFile = File(...)):
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        video_file = genai.upload_file(path=temp_path)
        
        prompt = """
        မင်းက မြန်မာလို Movie Recap ဇာတ်ညွှန်းရေးပေးရမယ့် ကျွမ်းကျင်သူဖြစ်တယ်။ 
        ဒီဗီဒီယိုကို ကြည့်ပြီး အောက်ပါ စည်းမျဉ်းတွေနဲ့အညီ ဇာတ်ညွှန်းရေးပေးပါ:
        ၁။ ဇာတ်ကြောင်းပြောခြင်း (Narrator) နှင့် ဇာတ်ကောင်များ၏ ပြောစကား (Dialogue) များကို ပေါင်းစပ်ရေးပါ။
        ၂။ စကားပြောဟန် သဘာဝကျကျ မြန်မာလိုသာ ရေးပါ။ အင်္ဂလိပ်စာလုံးများ မသုံးပါနှင့်။
        ၃။ ဂဏန်းများကို စာသားဖြင့်သာ ရေးပါ။ (ဥပမာ- ၁ အစား တစ်)
        ၄။ ခေါင်းစဉ်၊ Timestamp၊ အခန်းခွဲများ လုံးဝ မထည့်ပါနှင့်။
        ၅။ ဇာတ်လမ်းကို အစမှ အဆုံးထိ အသေးစိတ် (Full Scene) ရေးပါ။ အတိုချုပ် မရေးပါနှင့်။
        ၆။ အဆုံးသတ်တွင် ကြည့်ရှုသူများကို သဘာဝကျကျ နှုတ်ဆက်စကား ထည့်ပေးပါ။
        """
        
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        response = model.generate_content([prompt, video_file])
        
        os.remove(temp_path)
        return JSONResponse(content={"script": response.text})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

