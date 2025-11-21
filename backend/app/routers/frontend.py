from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["frontend"])

HTML_PAGE = """<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"UTF-8\"/><title>LuckyDraw 前端界面</title><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/><style>:root{--bg:#1e1f22;--panel:#2b2d31;--accent:#4e9cff;--danger:#ff4d5d;--success:#42c78b;--border:#3a3c40;--text:#e6e6e6}body{margin:0;font-family:system-ui,Arial;background:var(--bg);color:var(--text)}header{padding:16px 24px;background:#18191b;display:flex;justify-content:space-between;align-items:center}h1{font-size:20px;margin:0}main{max-width:1100px;margin:0 auto;padding:20px}.grid{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}.card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:16px;box-shadow:0 2px 4px rgba(0,0,0,.4)}.card h2{margin:0 0 12px;font-size:16px}label{display:block;margin:6px 0 4px;font-size:13px;opacity:.85}input{width:100%;padding:8px 10px;border-radius:6px;border:1px solid var(--border);background:#232427;color:var(--text);font-size:14px}button{cursor:pointer;border:none;padding:10px 14px;border-radius:6px;font-size:14px;font-weight:600;background:var(--accent);color:#fff;transition:.15s}button:hover{filter:brightness(1.15)}button.danger{background:var(--danger)}button.secondary{background:#3d3f44}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:6px 8px;border-bottom:1px solid var(--border);text-align:left}th{background:#202225;font-weight:600}tbody tr:hover{background:#26282c}.flex{display:flex;gap:10px;flex-wrap:wrap}.fair{font-size:12px;line-height:1.4;word-break:break-all;background:#222;padding:10px;border-radius:6px;border:1px solid #333}footer{text-align:center;padding:30px 0 50px;font-size:12px;opacity:.6}.status{font-size:13px;min-height:20px;margin-top:6px}@media(max-width:600px){header{flex-direction:column;align-items:flex-start;gap:10px}}</style></head><body><header><h1>🎉 LuckyDraw Web UI <span style=\"background:#383a40;padding:2px 8px;border-radius:20px;font-size:12px;\">v0.2</span></h1><div class=\"flex\"><input id=\"backendUrl\" placeholder=\"后端URL\" value=\"http://127.0.0.1:8000\" style=\"max-width:260px;\"/><button class=\"secondary\" onclick=\"pingHealth()\">健康检查</button></div></header><main><div class=\"grid\"><div class=\"card\"><h2>注册参与者</h2><label>学号</label><input id=\"regName\" placeholder=\"必填\"/><label>电话</label><input id=\"regPhone\" placeholder=\"可选\"/><label>邮箱</label><input id=\"regEmail\" placeholder=\"可选\"/><div class=\"flex\" style=\"margin-top:12px;\"><button onclick=\"register()\">注册并发号</button><button class=\"secondary\" onclick=\"refreshParticipants()\">刷新列表</button><button class=\"danger\" onclick=\"clearAll()\">清除名单</button></div><div class=\"status\" id=\"regStatus\"></div></div><div class=\"card\"><h2>参与者列表 <span id=\"totalSpan\">(0)</span></h2><div style=\"max-height:280px;overflow:auto;border:1px solid var(--border);border-radius:6px;\"><table id=\"partTable\"><thead><tr><th>ID</th><th>学号</th><th>电话</th><th>号码</th><th>时间</th></tr></thead><tbody></tbody></table></div><div style=\"margin-top:8px;\"><button class=\"secondary\" onclick=\"openDrawScreen()\">打开抽奖展示页面</button></div></div><div class=\"card\"><h2>抽奖与历史</h2><p style=\"margin:4px 0 10px;font-size:12px;opacity:.75;\">抽奖操作已迁移至展示页。这里查看历史并跳转。</p><div class=\"flex\" style=\"margin-bottom:10px;\"><button onclick=\"openDrawScreen()\">跳转抽奖展示页</button><button class=\"secondary\" onclick=\"loadWinners()\">刷新获奖历史</button></div><div class=\"status\" id=\"drawStatus\"></div><div style=\"max-height:260px;overflow:auto;margin-top:10px;border:1px solid var(--border);border-radius:6px;\"><table id=\"winnerTable\" style=\"width:100%;font-size:12px;\"><thead><tr><th>序号</th><th>奖项</th><th>号码</th><th>时间</th><th>Seed片段</th></tr></thead><tbody></tbody></table></div></div><div class=\"card\"><h2>公平性链</h2><div class=\"fair\" id=\"fairBox\">尚未抽奖</div><div class=\"flex\" style=\"margin-top:10px;\"><button class=\"secondary\" onclick=\"copyFair()\">复制信息</button><button class=\"secondary\" onclick=\"clearFair()\">清空</button></div></div></div></main><footer>© LuckyDrawBEST Demo</footer><script>const byId=i=>document.getElementById(i);function backend(){return byId('backendUrl').value.replace(/\/$/,'')}async function pingHealth(){try{const r=await fetch(backend()+'/health');const j=await r.json();byId('regStatus').textContent='后端健康: '+j.status}catch(e){byId('regStatus').textContent='后端不可达'}}async function register(){const name=byId('regName').value.trim();if(!name){byId('regStatus').textContent='学号必填';return}const payload={name,phone:byId('regPhone').value.trim()||null,email:byId('regEmail').value.trim()||null};try{let r=await fetch(backend()+'/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});if(!r.ok)throw new Error(await r.text());let j=await r.json();byId('regStatus').textContent='登记成功，号码: '+j.ticket_number;byId('regName').value='';byId('regPhone').value='';byId('regEmail').value='';refreshParticipants();}catch(err){byId('regStatus').textContent='失败: '+err.message}}function maskPhone(p){if(!p)return'';return p.replace(/(\d{3})\d{4}(\d{4})/,'$1****$2')}async function refreshParticipants(){try{let r=await fetch(backend()+'/api/participants?skip=0&limit=500');let j=await r.json();const body=byId('partTable').querySelector('tbody');body.innerHTML='';j.participants.forEach(p=>{const tr=document.createElement('tr');const ticketNumbers=(p.tickets||[]).map(t=>t.number).join(',');tr.innerHTML=`<td>${p.id}</td><td>${p.name}</td><td>${maskPhone(p.phone||'')}</td><td>${ticketNumbers}</td><td>${p.created_at.split('T')[0]}</td>`;body.appendChild(tr)});byId('totalSpan').textContent='('+j.total+')';}catch(e){}}async function clearAll(){const token=prompt('输入管理员令牌以清除所有参与者 (不可撤销)');if(!token)return;if(!confirm('确认删除全部参与者与记录？该操作不可恢复。'))return;try{let r=await fetch(backend()+'/api/participants/clear?admin_token='+encodeURIComponent(token),{method:'DELETE'});if(!r.ok)throw new Error(await r.text());let j=await r.json();byId('regStatus').textContent='已清除: '+j.status;refreshParticipants();}catch(err){byId('regStatus').textContent='清除失败: '+err.message}}function openDrawScreen(){window.open(backend()+'/draw_screen','_blank')}async function loadWinners(){try{const r=await fetch(backend()+'/api/winners?skip=0&limit=200');if(!r.ok)throw new Error(await r.text());const j=await r.json();const body=byId('winnerTable').querySelector('tbody');body.innerHTML='';j.winners.forEach((w,idx)=>{const tr=document.createElement('tr');const seedFrag=(w.session_seed||'').slice(0,8);tr.innerHTML=`<td>${idx+1}</td><td>${w.prize_level}</td><td>${w.number}</td><td>${w.announced_at.split('T')[0]}</td><td>${seedFrag}</td>`;body.appendChild(tr)});byId('drawStatus').textContent='已更新获奖历史 ('+j.total+')';}catch(e){byId('drawStatus').textContent='历史加载失败'}}function updateFair(payload){if(!payload)return;const seed=payload.session?.seed||'-';const chain=payload.session?.hash_chain||'-';const prev=payload.prev_chain||'-';byId('fairBox').textContent=`Seed=${seed}\nPrevChain=${prev}\nHashChain=${chain}`}function copyFair(){const t=byId('fairBox').textContent;navigator.clipboard.writeText(t).then(()=>alert('已复制'))}function clearFair(){byId('fairBox').textContent='尚未抽奖'}function initRealtime(){try{const ws=new WebSocket(backend().replace('http','ws')+'/ws/live');ws.onmessage=ev=>{try{const msg=JSON.parse(ev.data);if(msg.event==='draw'){loadWinners();updateFair(msg.payload)}if(msg.event==='register'){refreshParticipants()}}catch(e){}}}catch(e){}}refreshParticipants();loadWinners();initRealtime();</script></body></html>"""

@router.get('/ui', response_class=HTMLResponse)
def ui_page():
    return HTML_PAGE

DRAW_SCREEN_PAGE = """<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"UTF-8\" />
<title>抽奖展示</title><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
<style>
  body{margin:0;background:#0e0f12;color:#fff;font-family:system-ui;display:flex;flex-direction:column;min-height:100vh;}
  header{padding:14px 24px;background:#16181d;display:flex;justify-content:space-between;align-items:center;box-shadow:0 2px 6px rgba(0,0,0,.4);}
  h1{margin:0;font-size:20px;font-weight:600;letter-spacing:.5px;}
  main{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:30px 20px;}
  .digits{display:flex;gap:12px;margin-top:10px;}
  .digit-box{width:90px;height:120px;background:#1f2227;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:72px;font-weight:700;letter-spacing:2px;color:#ffcc00;box-shadow:0 4px 12px rgba(0,0,0,.5);transition:.25s;}
  .digit-box.locked{color:#8affc1;background:#18231d;}
  #winnerText{font-size:42px;font-weight:700;margin:34px 0 10px;min-height:50px;}
  button{background:#4e9cff;border:none;padding:12px 20px;color:#fff;font-size:16px;border-radius:8px;cursor:pointer;font-weight:600;letter-spacing:.5px;}
  button:hover{filter:brightness(1.15);}button:disabled{opacity:.45;cursor:not-allowed;}
  #fair{white-space:pre-line;font-size:12px;opacity:.7;margin-top:18px;max-width:640px;word-break:break-all;background:#15171b;padding:10px 14px;border-radius:8px;border:1px solid #2a2d31;}
  footer{text-align:center;font-size:12px;opacity:.35;padding:18px 0;}
  .panel{margin-top:26px;display:flex;gap:14px;flex-wrap:wrap;align-items:center;justify-content:center;}
  input{padding:8px 10px;border-radius:8px;border:1px solid #333;background:#1d1f23;color:#fff;font-size:14px;}
  .mini{font-size:12px;opacity:.6;margin-top:6px;}
  @media(max-width:680px){.digit-box{width:64px;height:90px;font-size:52px;}#winnerText{font-size:30px;} }
</style></head><body>
<header><h1>🎯 抽奖展示 (Web 动画版)</h1><div class=\"panel\" style=\"margin-top:0;\">
  <input id=\"backendUrl\" value=\"http://127.0.0.1:8000\" style=\"width:240px;\"/>
  <input id=\"prizeInput\" placeholder=\"奖项(默认 一等奖)\" style=\"width:140px;\"/>
  <input id=\"countInput\" type=\"number\" value=\"1\" min=\"1\" max=\"10\" style=\"width:80px;\"/>
  <button id=\"startBtn\" onclick=\"startDraw()\">开始抽奖</button>
  <button id=\"forceBtn\" class=\"secondary\" onclick=\"skipToBackend()\" disabled>立即揭晓</button>
</div></header>
<main>
  <div id=\"winnerText\">等待开始</div>
  <div class=\"digits\" id=\"digitRow\"></div>
  <div id=\"multiContainer\" style=\"display:none;margin-top:26px;max-width:900px;flex-wrap:wrap;gap:10px;justify-content:center;\"></div>
  <div id=\"fair\">尚无公平性数据</div>
  <div class=\"mini\">动画仅为展示，真实中奖由后端种子与哈希链确定。</div>
</main>
<footer>LuckyDraw 展示页 · 种子链可审计</footer>
<script>
const byId = id => document.getElementById(id);
function backend(){return byId('backendUrl').value.replace(/\/$/,'');}
let spinTimer=null;let spinActive=false;let lockSchedule=[];let finalDigits=[];let resultPayload=null;let digitBoxes=[];let drawPhase='idle';
function buildDigits(len){const row=byId('digitRow');row.innerHTML='';digitBoxes=[];for(let i=0;i<len;i++){const d=document.createElement('div');d.className='digit-box';d.textContent='0';row.appendChild(d);digitBoxes.push(d);} }
function randDigit(){return Math.floor(Math.random()*10);}
function spinTick(){if(!spinActive) return;digitBoxes.forEach((box,idx)=>{if(box.classList.contains('locked')) return;box.textContent=randDigit();});}
function startDraw(){if(spinActive) return;const prize=(byId('prizeInput').value.trim()||'一等奖');const cnt=parseInt(byId('countInput').value||'1');if(cnt>10||cnt<1){alert('数量范围1-10');return;}drawPhase='spinning';byId('winnerText').textContent='滚动中…';byId('startBtn').disabled=true;byId('forceBtn').disabled=false;resultPayload=null;finalDigits=[];lockSchedule=[];const digitLen=4;buildDigits(digitLen);spinActive=true;spinTimer=setInterval(spinTick,55); // 开始滚动
  // 延迟请求后端，制造动画时长
  setTimeout(()=>requestBackend(prize,cnt), 1500);
}
function skipToBackend(){if(drawPhase==='spinning' && !resultPayload){ // 立即请求
  requestBackend(byId('prizeInput').value.trim()||'一等奖', parseInt(byId('countInput').value||'1'));}
}
async function requestBackend(prize,cnt){try{let r=await fetch(backend()+'/api/draw',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prize_level:prize,count:cnt})});if(!r.ok) throw new Error(await r.text());let j=await r.json();resultPayload=j;prepareFinalDigits(j);startDeceleration();}catch(e){finishFailure(e.message);} }
function prepareFinalDigits(j){const winners=j.winners||[];if(!winners.length){finalDigits=['0','0','0','0'];return;} // 仅展示第一个号码动画，多号码下方列表
  const firstNumber=String(winners[0].number).padStart(4,'0');finalDigits=firstNumber.split(''); // 多 winner 渲染列表
  const multi=byId('multiContainer');multi.innerHTML='';if(winners.length>1){multi.style.display='flex';winners.forEach(w=>{const div=document.createElement('div');div.style.cssText='background:#222;padding:12px 16px;border-radius:10px;font-size:26px;font-weight:600;min-width:120px;text-align:center;border:1px solid #333;';div.textContent=w.number;multi.appendChild(div);});} else {multi.style.display='none';}
}
function startDeceleration(){drawPhase='decelerating';byId('winnerText').textContent='减速中…';// 生成锁定计划
  lockSchedule=[];for(let i=0;i<digitBoxes.length;i++){lockSchedule.push(400*(i+1));}
  lockNext(0);
}
function lockNext(idx){if(idx>=digitBoxes.length){return finalizeSuccess();}
  setTimeout(()=>{digitBoxes[idx].textContent=finalDigits[idx];digitBoxes[idx].classList.add('locked');lockNext(idx+1);}, lockSchedule[idx]);}
function finalizeSuccess(){spinActive=false;clearInterval(spinTimer);drawPhase='finished';const winners=resultPayload.winners||[];const prize=resultPayload.session?.prize_level||'';if(winners.length){byId('winnerText').textContent='🎉 '+prize+' 号码: '+winners.map(w=>w.number).join(', ');}else{byId('winnerText').textContent='无结果';}
  updateFair(resultPayload);byId('startBtn').disabled=false;byId('forceBtn').disabled=true;}
function finishFailure(msg){spinActive=false;clearInterval(spinTimer);drawPhase='error';byId('winnerText').textContent='失败: '+msg;byId('startBtn').disabled=false;byId('forceBtn').disabled=true;}
function updateFair(payload){const seed=payload?.session?.seed||'-';const chain=payload?.session?.hash_chain||'-';const prev=payload?.prev_chain||'-';byId('fair').textContent=`Seed=${seed}\nPrevChain=${prev}\nHashChain=${chain}`;}
// 接收其它客户端的抽奖广播（被动刷新）
function initRealtime(){try{const ws=new WebSocket(backend().replace('http','ws')+'/ws/live');ws.onmessage=ev=>{try{const msg=JSON.parse(ev.data);if(msg.event==='draw'&&drawPhase!=='spinning'){// 外部抽奖
  updateFair(msg.payload);const winners=msg.payload?.winners||[];if(winners.length){byId('winnerText').textContent='(外部) 🎉 '+winners.map(w=>w.number).join(', ');buildDigits(4);finalDigits=String(winners[0].number).padStart(4,'0').split('');digitBoxes.forEach((b,i)=>{b.textContent=finalDigits[i];b.classList.add('locked');});}}
  }catch(e){}};}catch(e){}}
initRealtime();
</script></body></html>"""

REGISTER_FORM_PAGE = """<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"UTF-8\" />
<title>参会登记</title><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
<style>body{margin:0;font-family:system-ui;background:#f5f6fa;color:#222;}main{max-width:420px;margin:40px auto;padding:24px;background:#fff;border-radius:16px;box-shadow:0 4px 16px rgba(0,0,0,.08);}h1{margin:0 0 20px;font-size:22px;}label{display:block;margin:12px 0 6px;font-size:14px;font-weight:600;}input{width:100%;padding:10px 12px;border:1px solid #ccc;border-radius:8px;font-size:14px;}button{margin-top:20px;width:100%;padding:12px 16px;border:none;border-radius:8px;background:#4e9cff;color:#fff;font-size:16px;font-weight:600;cursor:pointer;}button:hover{filter:brightness(1.12);}#status{margin-top:14px;font-size:14px;min-height:20px;}footer{text-align:center;margin-top:30px;font-size:12px;opacity:.5;} .ok{color:#0a7d55;} .err{color:#d63340;}</style></head><body><main>
<h1>参会登记 (获取抽奖号码)</h1>
<label>学号</label><input id=\"fName\" placeholder=\"必填\" />
<label>手机号</label><input id=\"fPhone\" placeholder=\"可选\" />
<label>邮箱</label><input id=\"fEmail\" placeholder=\"可选\" />
<button onclick=\"submitForm()\">提交登记</button>
<div id=\"status\"></div>
<p style=\"font-size:12px;opacity:.7;\">信息仅用于现场抽奖，不做其他用途。</p>
</main><footer>Powered by LuckyDrawBEST</footer>
<script>function backend(){return location.origin;}async function submitForm(){const name=document.getElementById('fName').value.trim();if(!name){setStatus('学号必填',true);return;}const payload={name,phone:document.getElementById('fPhone').value.trim()||null,email:document.getElementById('fEmail').value.trim()||null};try{let r=await fetch(backend()+'/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});if(!r.ok) throw new Error(await r.text());let j=await r.json();setStatus('登记成功，您的号码: '+j.ticket_number,false);document.getElementById('fName').value='';document.getElementById('fPhone').value='';document.getElementById('fEmail').value='';}catch(e){setStatus('失败: '+e.message,true);} }function setStatus(msg,err){const s=document.getElementById('status');s.textContent=msg;s.className=err?'err':'ok';}</script></body></html>"""

@router.get('/draw_screen', response_class=HTMLResponse)
def draw_screen_page():
  return DRAW_SCREEN_PAGE

@router.get('/register_form', response_class=HTMLResponse)
def register_form_page():
  return REGISTER_FORM_PAGE