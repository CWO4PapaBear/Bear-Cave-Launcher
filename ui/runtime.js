// Loaded only by the local launcher service; the standalone HTML stays a preview.
document.querySelector('.preview').textContent='PTR LAUNCHER Â· EARLY TEST';
document.querySelector('footer span').textContent='The Bear Cave Â· PTR launcher';
document.querySelector('[data-channel="main"]').disabled=true;
document.querySelector('[data-channel="main"] small').textContent='Main Server Â· Not enabled yet';
document.querySelector('[data-channel="ptr"]').click();
const panels=document.querySelectorAll('.panel');
panels[0].innerHTML='<h3>PTR updates</h3><p id="runtime-status" role="status">Choose your PTR client folder.</p><p id="runtime-error" style="color:#ffbc98" role="alert"></p>';
panels[1].innerHTML='<h3>PTR client folder</h3><p id="folder">Use a dedicated PTR client copy.</p><form id="client-form"><label for="client-path">Full path to the folder containing Wow.exe</label><input id="client-path" required placeholder="D:\\Games\\Bear Cave PTR" style="width:100%;padding:9px;margin:10px 0;background:#040e19;color:#eee5d3;border:1px solid #786035"><button class="action" type="submit">Save Folder</button></form>';
const browse=document.createElement('button');browse.type='button';browse.className='action';browse.id='client-browse';browse.textContent='Browseâ€¦';browse.style.marginRight='8px';
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
const alpha=document.createElement('button');alpha.className='realm';alpha.dataset.channel='area52';
alpha.innerHTML='<strong>Area 52 - Free Pick Alpha Dev</strong><small>Private Alpha · Preparing distribution</small>';
document.querySelector('.side-note').before(alpha);
for(const channel of ['ptr','area52']){
 document.querySelector('[data-channel="'+channel+'"]').addEventListener('click',()=>send('channel',{channel}));
}
let lastState=null;
function render(state){
 lastState=state;
 const area52=state.channel==='area52';
 document.querySelectorAll('[data-channel]').forEach(b=>{b.classList.toggle('selected',b.dataset.channel===state.channel);b.disabled=state.busy||b.dataset.channel==='main';});
 document.getElementById('badge').textContent=area52?'PRIVATE ALPHA':'PUBLIC TEST REALM';
 document.getElementById('title').textContent=area52?'Area 52 - Free Pick Alpha Dev':'Help shape the next adventure.';
 document.getElementById('description').textContent=area52?'Test Season 9 Free Pick progression, builds, and the shared world.':'Explore new abilities, companions and character builds.';
 panels[0].querySelector('h3').textContent=area52?'Area 52 updates':'PTR updates';
 panels[1].querySelector('h3').textContent=area52?'Area 52 client folder':'PTR client folder';
 document.querySelector('label[for="client-path"]').textContent='Full path to the folder containing '+(area52?'Ascension.exe':'Wow.exe');
 document.getElementById('folder').textContent='Use a separate client folder for this realm.';
 document.querySelector('[data-action="update"]').textContent=area52?'Update Area 52':'Update PTR';
 document.querySelector('footer span').textContent='The Bear Cave Â· Launcher '+(state.launcher_version||'');
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

document.getElementById('account-open').addEventListener('click',()=>{document.getElementById('account-realm').textContent=lastState?.channel==='area52'?'Area 52 - Free Pick Alpha Dev':'The Bear Cave — PTR';});

const passwordLabel=document.createElement('label');passwordLabel.htmlFor='account-password';passwordLabel.textContent='Game password (10–16 characters; case-insensitive)';
const passwordInput=document.createElement('input');passwordInput.id='account-password';passwordInput.type='password';passwordInput.autocomplete='new-password';passwordInput.minLength=10;passwordInput.maxLength=16;
document.querySelector('.account-note').before(passwordLabel,passwordInput);
const statusButton=document.createElement('button');statusButton.type='button';statusButton.className='action';statusButton.textContent='Check Account Status';document.querySelector('.dialog-actions').prepend(statusButton);
document.getElementById('account-open').addEventListener('click',()=>{
 const alpha=lastState?.channel==='area52';
 document.getElementById('account-title').textContent=alpha?'Activate Your Invitation':'Request an Account';
 document.querySelector('label[for="account-contact"]').textContent=alpha?'One-time invitation key':'Email or Discord username';
 const key=document.getElementById('account-contact');key.type=alpha?'password':'text';key.placeholder=alpha?'Invitation provided by the administrator':'Where we can contact you privately';
 passwordInput.hidden=passwordLabel.hidden=!alpha;passwordInput.required=alpha;statusButton.hidden=!alpha;
 const submit=document.querySelector('#account-form button[type="submit"]');submit.disabled=!alpha||!lastState?.access_ready;submit.textContent=alpha?'Create Account':'Send Request';
 document.querySelector('.account-note').textContent=alpha?'Your invitation is your approval. No email is required. Passwords follow the game’s case-insensitive login rules.':'Account requests are not connected yet.';
 document.getElementById('account-status').textContent=alpha&&!lastState?.access_ready?'Private account service is being prepared. Nothing will be sent yet.':'';
});
async function accountRequest(action,payload){
 const output=document.getElementById('account-status');
 document.querySelectorAll('#account-form button').forEach(button=>button.disabled=true);
 try{
  const response=await fetch('api/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const result=await response.json();if(!response.ok)throw Error(result.error);
  output.textContent=result.status==='ready'?'Account ready: '+result.username+'.':('Account request: '+result.status+'. Use Check Account Status to check completion.');
 }catch(error){output.textContent=error.message;}
 finally{document.querySelectorAll('#account-form button').forEach(button=>button.disabled=false);}
}
document.getElementById('account-form').addEventListener('submit',event=>{
 if(lastState?.channel!=='area52'||!lastState?.access_ready)return;
 event.preventDefault();const password=passwordInput.value;passwordInput.value='';
 const key=document.getElementById('account-contact');const invitation=key.value.trim();key.value='';
 accountRequest('enroll',{invitation,username:document.getElementById('account-name').value.trim(),password});
});
statusButton.addEventListener('click',()=>accountRequest('account-status',{}));
