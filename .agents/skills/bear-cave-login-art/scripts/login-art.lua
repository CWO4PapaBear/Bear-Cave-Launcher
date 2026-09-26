-- Presentation only; retain stock login behavior.
local function BearCaveLoginArt()
 local p=AccountLoginUI
 if not p or not AccountLoginLogo then return end
 if not p.bearCaveBackground then
  local t=p:CreateTexture(nil,'BACKGROUND');t:SetTexture('Interface\\Glues\\BearCave\\Background');t:SetAllPoints(p);p.bearCaveBackground=t
 end
 local w,h=p:GetWidth(),p:GetHeight()
 if w>0 and h>0 then
  local left,right,top,bottom=.0625,.9375,0,1
  local aspect=1792/1024;local screen=w/h
  if screen>aspect then local visible=aspect/screen;top=(1-visible)/2;bottom=1-top
  else local visible=(right-left)*screen/aspect;left=.5-visible/2;right=.5+visible/2 end
  p.bearCaveBackground:SetTexCoord(left,right,top,bottom)
 end
 AccountLoginLogo:SetTexture('Interface\\Glues\\BearCave\\Logo');AccountLoginLogo:SetTexCoord(0,1,0,1)
 AccountLoginLogo:ClearAllPoints();AccountLoginLogo:SetPoint('TOPLEFT',p,'TOPLEFT',20,-20)
 AccountLoginLogo:SetWidth(320);AccountLoginLogo:SetHeight(160)
 p.bearCaveBackground:Show();AccountLoginLogo:Show()
end
local originalShow=AccountLogin_OnShow
function AccountLogin_OnShow(self,...)originalShow(self,...);BearCaveLoginArt()end
local originalLoad=AccountLogin_OnLoad
function AccountLogin_OnLoad(self,...)
 originalLoad(self,...);AccountLoginUI:HookScript('OnSizeChanged',BearCaveLoginArt);BearCaveLoginArt()
end
