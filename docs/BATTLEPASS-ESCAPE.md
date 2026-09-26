# Battle Pass Escape-close repair

Register `BattlePassFrame` in the stock `UISpecialFrames` list when BattlePass finishes ADDON_LOADED, after its XML frame exists. Keep the registration idempotent and preserve other menus. This uses the normal Escape handler rather than intercepting keyboard input.

`tools/battlepass_escape.py` stages the change against the current addon without overwriting it. Lua 5.1 syntax and duplicate-registration checks passed. The owner client was installed with a hash-verified backup in `outputs/BattlePass_Escape/before.lua`; in-game review is pending. The launcher game channel remains 0.2.13-test.1 and does not yet include this local addon change. Carry it into the next cumulative release after review.

Lootboot investigation is separate: saved Lua accepts only entry 34587 and starts collection via the give-XP hook. Live snapshot requested before changing server behavior. No Lootboot server repair or restart has been performed.
