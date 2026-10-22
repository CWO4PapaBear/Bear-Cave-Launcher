# Area 52 quest corrections — expanded Batch 4

## Quests and interactions

- **A Humble Duty:** adds graveyard and Invincible's Gravestone map areas. Graves remain present after use and have a shared 30-second reuse cooldown. This is a temporary per-object cooldown, not permanent per-character tracking; another player may need to wait for a used grave.
- **Egg Hunt:** Silithid Protectors are hostile to Alliance and Horde, matching neighboring silithids. Egg loot, spawns and creature statistics are preserved.
- **Deaths in the Family:** Coleman Farthing plays his two existing dialogue lines after turn-in. His questgiver flag is temporarily hidden during the sequence and restored afterward. No new dialogue or rewards are added.
- **Goldshire's Generosity:** each produce container stops highlighting when you have enough of that particular produce, even while other produce is still needed.

## Quest map corrections

- Adds missing objective markers for **Dar'Khan's Lieutenants**, **The Master's Orders**, **King's Justice**, **Supply Run** and **Termites in Teldrassil**.
- **Defias Disruption:** narrows objective areas to Bandit's Bastion, as directed by the quest. The turn-in marker is preserved.
- **Infiltrating the Castle** and **An Old History Book:** correct their turn-in pins to Tyrion and Milton Sheaf's current positions.
- **The Sacred Flame:** connects the moonwell area to its actual item objective and places it around the moonwell. These are map-marker fixes; separate in-world navigation-arrow streaming is not included.

## Quest access and item hints

- Opens ten general Sunstrider quests to Horde races instead of only Blood Elves: **Reclaiming Sunstrider Isle**, **Unfortunate Measures**, **Report to Lanthan Perilon**, **Solanian's Belongings**, **Aggression**, **Felendren the Banished**, **A Fistful of Slivers**, **Tainted Arcane Sliver**, **The Shrine of Dath'Remar** and **Aiding the Outrunners**. Other prerequisites remain unchanged. **Thirst Unending** remains Blood Elf restricted because it explicitly requires the Arcane Torrent racial ability.
- **Lost Thunderbrew Recipe:** restores the Horde race gate; its Alliance counterpart remains unchanged.
- Adds 32 missing creature quest-item hints for **Pie for Billy**, **Stocking Jetsteam** and **Seasoned Wolf Kabobs**, matching existing loot sources. Existing hints, drop chances and rewards are preserved.

## Engineering scope

This batch covers 27 quests through ten SQL migrations. The previously prepared Batch 4 fixes are retained. Offline qualification uses exact deployed table schemas and snapshots, actual SQL migrations and the packaged guarded hook: backup, repeated apply, exact rollback, repeated rollback, conflicting edits and unrelated-state preservation across seven tables. Focused extracted native checks cover grave reuse and faction hostility, race eligibility, produce highlighting, and the dialogue reward filter/action-list progression. These checks are not live gameplay certification or full quest playthroughs.

All prior Area 52 fixes, character data, rewards and certification records are preserved. No server binary, client assets, DLL or launcher-feed changes are required. Source publication stays on a feature branch. Missing quest-chain prerequisites, narrative/terrain restorations and navigation-arrow infrastructure remain separate work.
