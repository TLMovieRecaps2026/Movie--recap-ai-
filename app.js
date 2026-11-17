let jobId=null;
const $=id=>document.getElementById(id);
$("video").addEventListener("change",()=>{$("filename").textContent=$("video").files[0]?.name||"ဗီဒီယို မရွေးရသေးပါ။"});
$("upload").onclick=async()=>{
 const f=$("video").files[0]; if(!f){alert("အရင်ဆုံး ဗီဒီယိုရွေးပါ။");return;}
 $("status").textContent="Upload လုပ်နေပါတယ်...";
 const data=new FormData();data.append("video",f);
 try{const r=await fetch("/api/upload",{method:"POST",body:data});const j=await r.json();if(!r.ok)throw Error(j.detail||"Upload failed");
 jobId=j.job_id;$("status").textContent="Upload အောင်မြင်ပါပြီ။ AI Analysis လုပ်နိုင်ပါပြီ။";$("analyze").disabled=false;
 }catch(e){$("status").textContent="အမှား: "+e.message;}
};
$("analyze").onclick=async()=>{
 if(!jobId)return;$("analyze").disabled=true;$("status").textContent="AI က ဗီဒီယိုကို လေ့လာနေပါတယ်။ အချိန်ယူနိုင်ပါတယ်...";
 try{const r=await fetch("/api/analyze/"+jobId,{method:"POST"});const j=await r.json();if(!r.ok)throw Error(j.detail||"Analysis failed");
 $("transcript").value=j.transcript;$("status").textContent="Transcript ထုတ်ပြီးပါပြီ။ စာသားကို ပြင်ဆင်နိုင်ပါတယ်။";["save","txt","srt"].forEach(x=>$(x).disabled=false);
 }catch(e){$("status").textContent="အမှား: "+e.message;}finally{$("analyze").disabled=false;}
};
$("save").onclick=async()=>{try{const r=await fetch("/api/export/"+jobId,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({transcript:$("transcript").value})});const j=await r.json();if(!r.ok)throw Error(j.detail);$("status").textContent="ပြင်ထားသော Transcript သိမ်းပြီးပါပြီ။";}catch(e){$("status").textContent="အမှား: "+e.message;}};
$("txt").onclick=()=>{if(jobId)location.href="/api/download/"+jobId+"/txt"};
$("srt").onclick=()=>{if(jobId)location.href="/api/download/"+jobId+"/srt"};
