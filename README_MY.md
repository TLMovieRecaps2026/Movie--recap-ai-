# Movie Recap AI Web App (မြန်မာ UI)

ဒီ Project သည် FastAPI + FFmpeg ကို အခြေခံထားသော Movie Recap Web App starter ဖြစ်သည်။
Video upload, source audio ဖယ်ရှားခြင်း, aspect ratio, auto color correction, narration mode,
voice selection, AI scene analysis, Burmese narration/TTS, SRT, subtitle burn-in, progress, download ပါဝင်သည်။

## လိုအပ်ချက်
- Python 3.11+
- FFmpeg နှင့် ffprobe ကို PATH ထဲထည့်ထားရန်
- OpenAI API key (AI script/TTS အတွက်)
- API model တစ်ခုက မြန်မာဘာသာကို သဘာဝကျကျ ထုတ်ပေးနိုင်မှုသည် model/voice ပေါ်မူတည်သည်။
  မြန်မာ TTS အသံအရည်အသွေးကို မဖြစ်မနေ လက်တွေ့စမ်းသပ်ပါ။

## Run (Windows)
1. ZIP ဖြည်ပါ။
2. Python 3.11+ နှင့် FFmpeg install လုပ်ပါ။
3. `copy .env.example .env` လုပ်ပြီး `.env` ထဲမှာ `OPENAI_API_KEY` ထည့်ပါ။
4. Terminal မှာ:
   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate
   pip install -r requirements.txt
   uvicorn app:app --host 127.0.0.1 --port 8000
   ```
5. Browser မှာ http://127.0.0.1:8000 ဖွင့်ပါ။

## Run (Linux/macOS)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env ထဲတွင် OPENAI_API_KEY ထည့်ပါ
uvicorn app:app --host 0.0.0.0 --port 8000
```

## အရေးကြီး
- ဒီ app သည် server ပေါ်တွင် video processing လုပ်သည်။ Public internet ပေါ်တင်မည်ဆိုပါက login,
  storage limits, queue/worker, HTTPS, cleanup policy, API cost limits တို့ ထပ်ထည့်ပါ။
- AI scene analysis အတွက် video မှ frame များကို အချိန်အလိုက် ထုတ်ယူပြီး vision model သို့ပို့သည်။
  အရှည်ကြီး video များတွင် frame အရေအတွက်ကို `.env` မှ ကန့်သတ်နိုင်သည်။
- `Narrator` mode သည် ဇာတ်ကွက်ကို မြန်မာလို အကျဉ်းချုပ် narration ဖန်တီးသည်။
- `Dialogue` mode သည် မြင်ရ/ကြားရသော အဖြစ်အပျက်များအပေါ် အခြေခံပြီး dialogue-style script ဖန်တီးရန် ကြိုးစားသည်။
  မူရင်း dialogue ကို အတိအကျ ပြန်လည်ထုတ်ပေးမည်ဟု အာမမခံနိုင်ပါ။
- AI မှ ဖန်တီးထားသော SRT သည် narration audio ၏ အချိန်ပိုင်းများနှင့် ကိုက်ညီအောင် segment လုပ်ထားသော်လည်း
  publish မလုပ်မီ စစ်ဆေးရန် အကြံပြုသည်။
- ဒီ starter ကို production-ready cloud service အဖြစ် မယူဆပါနှင့်။
