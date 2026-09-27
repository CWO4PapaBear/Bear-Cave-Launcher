BattlePassSpin = BattlePassSpin or {}
local deliver
local asset='Interface\\AddOns\\BattlePass\\SpinAssets\\'
local rewards={
 {930004,'Rune of Retreat',2,'Interface\\Icons\\INV_Misc_Rune_01'},
 {930003,'Rune of Return',2,'Interface\\Icons\\INV_Misc_Rune_01'},
 {930001,'Inherited Mark',3,'Interface\\Icons\\INV_Misc_Token_ArgentDawn'},
 {930002,'Legacy Mount Token',4,'Interface\\Icons\\INV_Misc_Coin_13'},
}
local byID={}; for _,r in ipairs(rewards) do byID[r[1]]=r end

local busy,pending,elapsed,winner,token,lastToken,claimed,hideAt,announced
function BattlePassSpin.IsBusy() return busy end
local frame=CreateFrame('Frame','BattlePassRewardSpinFrame',UIParent)
frame:SetFrameStrata('DIALOG'); frame:SetHeight(280); frame:EnableMouse(false)
local function layout()
 frame:ClearAllPoints(); frame:SetWidth(UIParent:GetWidth())
 frame:SetPoint('CENTER',UIParent,'TOP',0,-UIParent:GetHeight()/3)
end
layout(); frame:Hide()
local label=frame:CreateFontString(nil,'OVERLAY','GameFontNormalLarge')
label:SetFont(STANDARD_TEXT_FONT,28,'OUTLINE'); label:SetPoint('CENTER',0,-95); label:SetWidth(800)
local dice=frame:CreateTexture(nil,'OVERLAY'); dice:SetPoint('CENTER'); dice:SetSize(120,120)
local diceLeft=frame:CreateTexture(nil,'OVERLAY')
local diceRight=frame:CreateTexture(nil,'OVERLAY')
diceLeft:Hide(); diceRight:Hide()
local icons={}
for i=1,40 do icons[i]=frame:CreateTexture(nil,'ARTWORK'); icons[i]:SetSize(52,52) end
local glow=frame:CreateTexture(nil,'OVERLAY')
glow:SetTexture(asset..'wildcardAtlas'); glow:SetTexCoord(0.560547,0.840820,0.278809,0.557617)
glow:SetSize(190,190); glow:SetPoint('CENTER'); glow:SetBlendMode('ADD'); glow:Hide()
local function hideIcons() for _,icon in ipairs(icons) do icon:Hide() end end
local function iconFor(r)
 local _,_,_,_,_,_,_,_,_,icon=GetItemInfo(r[1]); return icon or r[4]
end
local function flip(name,index,cols,w,h,width)
 if width and w>h then
  -- Move the two halves apart instead of widening the artwork.
  dice:Hide()
  local halfWidth=120*w/h/2
  for side,texture in ipairs({diceLeft,diceRight}) do
   texture:SetTexture(asset..name)
   texture:SetTexCoord((side-1)*w/2/2048,side*w/2/2048,index*h/2048,(index+1)*h/2048)
   texture:SetSize(halfWidth,120)
   texture:ClearAllPoints()
   texture:SetPoint('CENTER',frame,'CENTER',(side==1 and -1 or 1)*(width/2-halfWidth/2),0)
   texture:Show()
  end
  return
 end
 diceLeft:Hide(); diceRight:Hide()
 dice:SetTexture(asset..name); local x=index%cols; local y=math.floor(index/cols)
 dice:SetTexCoord(x*w/2048,(x+1)*w/2048,y*h/2048,(y+1)*h/2048)
 dice:SetSize(width or 120,120); dice:Show()
end
local function positionIcons(offset,spread,grow)
 for i,icon in ipairs(icons) do
  local x=(i-1)*64-offset
  -- Fade whole icons at the dice openings; no ScrollFrame clips their edges.
  local alpha=math.max(0,math.min(1,(310-math.abs(x))/45))
  if i~=28 then x=x+(x<0 and -1 or 1)*spread end
  icon:ClearAllPoints(); icon:SetPoint('CENTER',frame,'CENTER',x,0)
  local size=i==28 and (52+52*grow) or 52
  icon:SetSize(size,size); icon:SetAlpha(alpha)
  if alpha>0 then icon:Show() else icon:Hide() end
 end
end
local function showError(message)
 busy=false; pending=nil; lastToken=nil; frame:Hide()
 DEFAULT_CHAT_FRAME:AddMessage('|cffff8080Reward spin: '..tostring(message)..'|r')
end
local function startResult(id,resultToken)
 if resultToken==lastToken then return end
 winner=byID[id]; if not winner then showError('Unknown reward from server.'); return end
 lastToken=resultToken; token=resultToken; pending=nil; elapsed=0; busy=true; claimed=false; announced=false; hideAt=nil
 layout(); frame:SetAlpha(1); frame:Show(); hideIcons(); glow:Hide(); label:SetText(''); label:SetAlpha(1)
 for i=1,40 do icons[i]:SetTexture(iconFor(rewards[math.random(1,4)])) end
 icons[28]:SetTexture(iconFor(winner))
end
function BattlePassSpin.Play(id, resultToken, onDelivered)
 if busy then return token==resultToken end
 if not byID[id] or type(resultToken)~='string' or type(onDelivered)~='function' then return false end
 lastToken=nil; deliver=onDelivered
 startResult(id,resultToken)
 return true
end
local events=CreateFrame('Frame')
events:RegisterEvent('DISPLAY_SIZE_CHANGED')
events:SetScript('OnEvent',function() layout() end)
events:SetScript('OnUpdate',function(_,dt)
 if hideAt then
  local remaining=hideAt-GetTime()
  frame:SetAlpha(math.max(0,math.min(1,remaining)))
  if remaining<=0 then frame:Hide(); hideAt=nil end
 end
 if not busy or not winner then return end
 elapsed=elapsed+dt
 if elapsed<1.25 then
  local n=math.min(74,math.floor(elapsed*60)); flip('anim_constant_final_'..(math.floor(n/25)+1),n%25,5,371,375)
 elseif elapsed<1.52 then
  flip('crack_1',math.min(15,math.floor((elapsed-1.25)/0.27*16)),4,371,375)
 elseif elapsed<1.66 then
  flip('crack_2',math.min(4,math.floor((elapsed-1.52)/0.14*5)),1,1484,375,860)
 elseif elapsed<1.8 then
  flip('crack_3',math.min(4,math.floor((elapsed-1.66)/0.14*5)),1,1484,375,860)
 else
  local p=math.min(1,(elapsed-1.8)/4)
  local spread=math.min(1,math.max(0,(elapsed-5.8)/0.4))
  local grow=math.min(1,math.max(0,(elapsed-6.2)/0.45))
  flip('crack_3',4,1,1484,375,860+120*spread)
  positionIcons(27*64*(1-(1-p)^3),60*spread,grow)
  if grow>0 then
   local c=ITEM_QUALITY_COLORS[winner[3]]; glow:SetVertexColor(c.r,c.g,c.b); glow:SetAlpha(grow); glow:Show()
  end
  if elapsed>=6.65 and not announced then
   announced=true
   local c=ITEM_QUALITY_COLORS[winner[3]]
   label:SetText('You won a '..c.hex..winner[2]..'|r!')
   PlaySoundFile(asset..(winner[3]==4 and 'epic' or winner[3]==3 and 'rare' or 'uncommon')..'.ogg')

  end
  if elapsed>=11.65 then
   local fly=math.min(1,(elapsed-11.65)/0.7)
   local sx,sy=frame:GetCenter()
   local tx,ty
   if MainMenuBarBackpackButton and MainMenuBarBackpackButton:IsShown() then tx,ty=MainMenuBarBackpackButton:GetCenter() end
   tx,ty=tx or UIParent:GetWidth()-35,ty or 35
   -- Coordinates are expressed in UIParent units, including differing bag scale.
   if MainMenuBarBackpackButton and MainMenuBarBackpackButton:IsShown() then
    local ratio=MainMenuBarBackpackButton:GetEffectiveScale()/UIParent:GetEffectiveScale(); tx,ty=tx*ratio,ty*ratio
   end
   for i,icon in ipairs(icons) do if i~=28 then icon:Hide() end end
   local prize=icons[28]; prize:ClearAllPoints(); prize:SetPoint('CENTER',UIParent,'BOTTOMLEFT',sx+(tx-sx)*fly,sy+(ty-sy)*fly)
   prize:SetSize(104-78*fly,104-78*fly); prize:SetAlpha(1-fly*0.5)
   glow:Hide(); label:SetAlpha(1-fly)
   local closeProgress=math.min(1,(elapsed-11.65)/0.7)
   local n=math.min(9,math.floor(closeProgress*10))
   flip(n<5 and 'crack_3' or 'crack_2',4-(n%5),1,1484,375,980-120*closeProgress)
   if fly>=1 then
    prize:Hide()
    if not claimed then claimed=true; deliver() end
   end
  end
  if elapsed>=12.35 then
   hideIcons()
   local n=74-math.min(74,math.floor((elapsed-12.35)*60))
   flip('anim_constant_final_'..(math.floor(n/25)+1),n%25,5,371,375)
  end
  if elapsed>=13.6 then frame:Hide(); busy=false end
 end
end)
