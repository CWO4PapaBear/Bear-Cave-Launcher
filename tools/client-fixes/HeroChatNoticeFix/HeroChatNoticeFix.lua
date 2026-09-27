-- Preserve normal channel handling; provide text only for unknown notice types.
HeroChatNoticeDiagnostics=HeroChatNoticeDiagnostics or {}
ChatFrame_AddMessageEventFilter('CHAT_MSG_CHANNEL_NOTICE',function(self,event,notice)
 if type(notice)~='string' then return false end
 local key='CHAT_'..notice..'_NOTICE'
 if type(_G[key..'_BN'])~='string' and type(_G[key])~='string' then
  HeroChatNoticeDiagnostics[notice]=true
  -- Two placeholders match the stock handler's channel number and channel name.
  _G[key]='Channel notice: |Hchannel:%d|h[%s]|h'
 end
 return false
end)
