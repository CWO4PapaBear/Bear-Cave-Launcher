from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[6]
sys.path.insert(0,str(ROOT/'work/regalia/libs'))
from lupa.lua51 import LuaRuntime
l=LuaRuntime()
candidate=ROOT/'outputs/Bear_Cave_Login_Art/AccountLogin.lua'
assert l.eval('function(s)return loadstring(s)~=nil end')(candidate.read_text())
l.execute('''
function object()
 local t={};setmetatable(t,{__index=function(_,key)if key~='bearCaveBackground'then return function()end end end})
 function t:SetTexCoord(...)self.uv={...}end
 return t
end
AccountLoginUI=object();AccountLoginLogo=object();w=1920;h=1080;created=0
function AccountLoginUI:GetWidth()return w end
function AccountLoginUI:GetHeight()return h end
function AccountLoginUI:CreateTexture()created=created+1;return object()end
function AccountLogin_OnLoad()loaded=true end
function AccountLogin_OnShow()shown=true end
''')
l.execute(Path(__file__).with_name('login-art.lua').read_text())
l.execute('''
AccountLogin_OnLoad({});AccountLogin_OnShow({});assert(loaded and shown and created==1)
for _,ratio in ipairs({4/3,16/9,21/9})do
 w=ratio*1000;h=1000;AccountLogin_OnShow({})
 local uv=AccountLoginUI.bearCaveBackground.uv
 assert(uv[1]>=.0625 and uv[2]<=.9375 and uv[3]>=0 and uv[4]<=1)
 assert(math.abs((uv[2]-uv[1])*2048/((uv[4]-uv[3])*1024)-ratio)<.00001)
end
assert(created==1)
''')
print('PASS: Lua 5.1 syntax, retained callbacks, texture reuse and undistorted 4:3/16:9/21:9 cover.')
