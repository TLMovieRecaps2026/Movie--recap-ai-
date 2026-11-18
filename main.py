from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def home():
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
      body { background-color: #e8f4f8; text-align: center; font-family: Arial, sans-serif; padding-top: 50px; }
      h1 { color: #2c3e50; }
      p { color: #555; }
      button { background-color: #ff4757; color: white; padding: 15px 30px; font-size: 16px; border: none; border-radius: 8px; }
    </style>
    </head>
    <body>
      <h1>Movie Recap AI Studio</h1>
      <p>သင့်ရဲ့ ဗီဒီယိုဖိုင်ကို ဒီနေရာမှာ တင်ပေးပါ။</p>
      <button onclick="alert('Backend ဆာဗာနှင့် အောင်မြင်စွာ ချိတ်ဆက်မိပါပြီ! ဇာတ်ညွှန်းထုတ်ရန် အသင့်ဖြစ်နေပါပြီ။')">Upload Video</button>
    </body>
    </html>
    """
    return HTMLResponse(content=html_code)
