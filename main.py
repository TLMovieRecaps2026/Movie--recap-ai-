from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse

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
      body { background-color: #f0f4f8; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding-top: 50px; color: #333;}
      h1 { color: #2c3e50; margin-bottom: 10px;}
      p { color: #666; margin-bottom: 30px;}
      .upload-container { background-color: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: inline-block; max-width: 90%;}
      input[type="file"] { display: none; }
      .custom-file-upload { border: 2px dashed #3498db; color: #3498db; padding: 15px 30px; font-size: 16px; border-radius: 8px; cursor: pointer; display: inline-block; margin-bottom: 20px; transition: all 0.3s ease;}
      .custom-file-upload:hover { background-color: #3498db; color: white; }
      #file-name { margin-top: 10px; font-style: italic; color: #7f8c8d; }
      button { background-color: #2ecc71; color: white; padding: 12px 25px; font-size: 16px; border: none; border-radius: 8px; cursor: pointer; transition: background-color 0.3s ease;}
      button:hover { background-color: #27ae60; }
    </style>
    </head>
    <body>
      <div class="upload-container">
          <h1>Movie Recap AI Studio</h1>
          <p>သင့်ရဲ့ ဗီဒီယိုဖိုင်ကို အောက်ပါခလုတ်မှတစ်ဆင့် ရွေးချယ်ပါ။</p>
          
          <label class="custom-file-upload">
              <input type="file" id="video-upload" accept="video/*" onchange="updateFileName()">
              ဗီဒီယိုဖိုင် ရွေးရန်
          </label>
          <div id="file-name">ဖိုင်ရွေးချယ်ထားခြင်း မရှိသေးပါ</div>
          <br>
          <button onclick="startUpload()">ဇာတ်ညွှန်းထုတ်ရန် စတင်ပါ</button>
      </div>

      <script>
        function updateFileName() {
            const input = document.getElementById('video-upload');
            const fileNameDisplay = document.getElementById('file-name');
            if (input.files.length > 0) {
                fileNameDisplay.textContent = "ရွေးချယ်ထားသောဖိုင်: " + input.files[0].name;
            } else {
                fileNameDisplay.textContent = "ဖိုင်ရွေးချယ်ထားခြင်း မရှိသေးပါ";
            }
        }

        function startUpload() {
             const input = document.getElementById('video-upload');
             if (input.files.length === 0) {
                 alert("ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင် တစ်ခုခုကို အရင်ရွေးချယ်ပေးပါ။");
                 return;
             }
             alert("ဗီဒီယိုဖိုင် လက်ခံရရှိပါပြီ! မကြာမီ AI နှင့် ချိတ်ဆက်ပါမည်။ (ဒါက အစမ်းပြသခြင်းဖြစ်ပါတယ်)");
        }
      </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_code)

