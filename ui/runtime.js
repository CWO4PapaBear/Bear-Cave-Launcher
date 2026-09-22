// Loaded only by the local launcher service; the standalone HTML stays a preview.
document.querySelector('.preview').textContent='PTR LAUNCHER · EARLY TEST';
document.querySelector('footer span').textContent='The Bear Cave · PTR updater 0.2';
document.querySelector('[data-channel="main"]').disabled=true;
document.querySelector('[data-channel="main"] small').textContent='Main Server · Not enabled yet';
document.querySelector('[data-channel="ptr"]').click();
const panels=document.querySelectorAll('.panel');
panels[0].innerHTML='<h3>PTR updates</h3><p id="runtime-status" role="status">Choose your PTR client folder.</p><p id="runtime-error" style="color:#ffbc98" role="alert"></p>';
panels[1].innerHTML='<h3>PTR client folder</h3><p id="folder">Use a dedicated PTR client copy.</p><form id="client-form"><label for="client-path">Full path to the folder containing Wow.exe</label><input id="client-path" required placeholder="D:\\Games\\Bear Cave PTR" style="width:100%;padding:9px;margin:10px 0;background:#040e19;color:#eee5d3;border:1px solid #786035"><button class="action" type="submit">Save Folder</button></form>';
const browse=document.createElement('button');browse.type='button';browse.className='action';browse.id='client-browse';browse.textContent='Browse…';browse.style.marginRight='8px';
document.querySelector('#client-form button').before(browse);
browse.addEventListener('click',()=>send('browse'));
document.querySelector('.side-note').textContent='Use a dedicated PTR client copy. Do not select your Main Server client. The updater preserves your settings and unrelated addons.';
document.querySelector('.footnote').textContent='Checks published GitHub updates. Close WoW before installing. Backups are retained inside your PTR client. Recover restores an interrupted update. Account requests are not connected yet.';
const footer=document.querySelector('footer');
footer.querySelectorAll('button').forEach(b=>b.remove());
for(const [action,label] of [['check','Check / Repair'],['recover','Recover'],['update','Update PTR'],['play','Play']]){
 const button=document.createElement('button');button.className='action'+(action==='update'?' primary':'');button.textContent=label;button.dataset.action=action;
 button.addEventListener('click',()=>send(action));footer.appendChild(button);
}
let lastState=null;
function render(state){
 lastState=state;
 document.getElementById('runtime-status').textContent=state.message;
 document.getElementById('runtime-error').textContent=state.error||'';
 const input=document.getElementById('client-path');
 if(document.activeElement!==input)input.value=state.client||'';
 document.querySelectorAll('[data-action]').forEach(b=>{
  b.disabled=state.busy||!state.client||(b.dataset.action==='update'&&(!state.version||!state.changes.length));
 });
 document.querySelectorAll('#client-form button').forEach(button=>button.disabled=state.busy);
}
async function send(action,payload={}){
 try{
  const response=await fetch('api/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const data=await response.json();if(!response.ok)throw Error(data.error);render(data);
  if(action==='select')await send('check');
 }catch(error){document.getElementById('runtime-error').textContent=error.message;}
}
document.getElementById('client-form').addEventListener('submit',e=>{e.preventDefault();send('select',{path:document.getElementById('client-path').value.trim()});});
let firstPoll=true;
async function poll(){
 try{
  const response=await fetch('api/status');if(!response.ok)throw Error('Launcher session unavailable');
  const data=await response.json();render(data);
  if(firstPoll){firstPoll=false;if(data.client&&!data.busy)await send('check');}
 }catch(error){
  document.getElementById('runtime-error').textContent='Launcher service disconnected. Reopen the launcher to continue.';
  document.querySelectorAll('[data-action]').forEach(b=>b.disabled=true);
 }
}
poll();setInterval(poll,1000);
