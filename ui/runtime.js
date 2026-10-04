// Loaded only by the local launcher service; the standalone HTML stays a preview.
document.querySelector('.preview').textContent='PTR LAUNCHER · EARLY TEST';
document.querySelector('footer span').textContent='The Bear Cave · PTR launcher';
document.querySelector('[data-channel="main"]').disabled=true;
document.querySelector('[data-channel="main"] small').textContent='Main Server · Not enabled yet';
document.querySelector('[data-channel="ptr"]').click();
const panels=document.querySelectorAll('.panel');
panels[0].innerHTML='<h3>PTR updates</h3><p id="runtime-status" role="status">Choose your PTR client folder.</p><p id="runtime-error" style="color:#ffbc98" role="alert"></p>';
panels[1].innerHTML='<h3>PTR client folder</h3><p id="folder">Use a dedicated PTR client copy.</p><form id="client-form"><label for="client-path">Full path to the folder containing Wow.exe</label><input id="client-path" required placeholder="D:\\Games\\Bear Cave PTR" style="width:100%;padding:9px;margin:10px 0;background:#040e19;color:#eee5d3;border:1px solid #786035"><button class="action" type="submit">Save Folder</button></form>';
const browse=document.createElement('button');browse.type='button';browse.className='action';browse.id='client-browse';browse.textContent='Browse…';browse.style.marginRight='8px';
document.querySelector('#client-form button').before(browse);
browse.addEventListener('click',()=>send('browse'));
document.querySelector('.side-note').textContent='Each realm uses its own client folder and updates. Keep PTR and Area 52 separate.';
document.querySelector('.footnote').textContent='Checks published GitHub updates. Close WoW before installing. Backups are retained inside your PTR client. Recover restores an interrupted update. Use Discord to request an account.';
const footer=document.querySelector('footer');
footer.querySelectorAll('button').forEach(b=>b.remove());
for(const [action,label] of [['check','Check / Repair'],['recover','Recover'],['update','Update PTR'],['play','Play']]){
 const button=document.createElement('button');button.className='action'+(action==='update'?' primary':'');button.textContent=label;button.dataset.action=action;
 button.addEventListener('click',()=>send(action));footer.appendChild(button);
}
const alpha=document.createElement('button');alpha.className='realm';alpha.dataset.channel='area52';
alpha.innerHTML='<strong>Area 52 - Free Pick Alpha Dev</strong><small>Alpha Dev � COACore client</small>';
document.querySelector('.side-note').before(alpha);
for(const channel of ['ptr','area52']){
 document.querySelector('[data-channel="'+channel+'"]').addEventListener('click',()=>send('channel',{channel}));
}
const baseClient=document.createElement('button');baseClient.type='button';baseClient.className='action';baseClient.id='base-client-download';baseClient.textContent='Get COACore Client on Discord';baseClient.hidden=true;panels[1].appendChild(baseClient);baseClient.addEventListener('click',()=>send('base-client'));
let lastState=null;
function render(state){
 lastState=state;
 document.getElementById('account-open').disabled=!state.discord_ready;
 document.getElementById('account-open').title=state.discord_ready?'Open Discord in your browser':'Discord invitation is being configured';
 const area52=state.channel==='area52';
 document.getElementById('base-client-download').hidden=!area52;
 document.querySelectorAll('[data-channel]').forEach(b=>{b.classList.toggle('selected',b.dataset.channel===state.channel);b.disabled=state.busy||b.dataset.channel==='main';});
 document.getElementById('badge').textContent=area52?'PRIVATE ALPHA':'PUBLIC TEST REALM';
 document.getElementById('title').textContent=area52?'Area 52 - Free Pick Alpha Dev':'Help shape the next adventure.';
 document.getElementById('description').textContent=area52?'Test Season 9 Free Pick progression, builds, and the shared world.':'Explore new abilities, companions and character builds.';
 panels[0].querySelector('h3').textContent=area52?'Area 52 updates':'PTR updates';
 panels[1].querySelector('h3').textContent=area52?'Area 52 client folder':'PTR client folder';
 document.querySelector('label[for="client-path"]').textContent='Full path to the folder containing '+(area52?'Ascension.exe':'Wow.exe');
 document.getElementById('folder').textContent='Use a separate client folder for this realm.';
 document.querySelector('[data-action="update"]').textContent=area52?'Update Area 52':'Update PTR';
 document.querySelector('footer span').textContent='The Bear Cave · Launcher '+(state.launcher_version||'');
 document.getElementById('runtime-status').textContent=state.message;
 document.getElementById('runtime-error').textContent=state.error||'';
 const input=document.getElementById('client-path');
 if(document.activeElement!==input)input.value=state.client||'';
 document.querySelectorAll('[data-action]').forEach(b=>{
  b.disabled=state.busy||!state.channel_ready||!state.client||(b.dataset.action==='update'&&(!state.version||!state.changes.length));
 });
 document.querySelectorAll('#client-form button').forEach(button=>button.disabled=state.busy);
}
async function send(action,payload={}){
 try{
  const response=await fetch('api/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const data=await response.json();if(!response.ok)throw Error(data.error);render(data);
  if(action==='select'&&data.channel_ready)await send('check');
 }catch(error){document.getElementById('runtime-error').textContent=error.message;}
}
document.getElementById('client-form').addEventListener('submit',e=>{e.preventDefault();send('select',{path:document.getElementById('client-path').value.trim()});});
let firstPoll=true;
async function poll(){
 try{
  const response=await fetch('api/status');if(!response.ok)throw Error('Launcher session unavailable');
  const data=await response.json();render(data);
  if(firstPoll){firstPoll=false;if(data.client&&!data.busy&&data.channel_ready)await send('check');}
 }catch(error){
  document.getElementById('runtime-error').textContent='Launcher service disconnected. Reopen the launcher to continue.';
  document.querySelectorAll('[data-action]').forEach(b=>b.disabled=true);
 }
}
poll();setInterval(poll,1000);

function connectWindowControls(){
 for(const [id,method] of [['window-minimize','minimize'],['window-close','close']]){
  const button=document.getElementById(id);button.disabled=false;
  button.onclick=()=>window.pywebview.api[method]();
 }
}
window.addEventListener('pywebviewready',connectWindowControls);
if(window.pywebview&&window.pywebview.api)connectWindowControls();

const oldAccountButton=document.getElementById('account-open');
const discordButton=oldAccountButton.cloneNode(true);oldAccountButton.replaceWith(discordButton);
discordButton.textContent='Request Account on Discord';
discordButton.addEventListener('click',()=>send('discord'));
document.getElementById('account-dialog').remove();
document.querySelector('.account-entry p').innerHTML='<strong>Need an account?</strong>Contact the administrator directly on Discord.';
