# Area 52 creature cleanup correction

Fixes progressive server slowdown caused by expired creature corpses remaining on loaded maps. The shared creature lifecycle now keeps corpse cleanup and respawn timers updating even when players leave the area, and schedules dormant creatures when their death state changes. This applies across creature entries, including the heavily affected Northrend encounters.

Normal corpse, loot-roll, skinning and respawn timing is preserved. The activation restart clears the previously stranded runtime objects; no spawn records or player data are deleted. No client update is required.

Offline qualification reproduced the defect before correction, passed the corrected lifecycle checks and a one-hour fixture of 120 consecutive dynamic respawns, compiled the server and passed the unit-test runner. Live performance recovery remains to be observed after activation. Ability, talent and Mystic Enchant verification/certification labels are unchanged.

Source is published as a scoped patch against the previously deployed Area 52 candidate on a feature branch; this is not a merge into main. The patch includes its focused native-method harness changes.
