# Area 52 Prestige and specialization corrections

- Prestige now becomes available at the realm's configured maximum level (currently level 80), with no class restriction. Chromie's UI uses that same realm level cap.
- Prestige clears only the active unlocked build and the independently active unlocked Mystic Enchant specialization. Inactive builds, other enchant setups, specialization unlocks and the account's enchant collection remain intact.
- The active build's saved abilities, talents, primary-stat choice, action bars, historical ranks and archetype association are reset. Automatic build learning is paused; ordinary level-1 grants are restored by the existing level-change flow.
- Unlocking build specializations with a Tome also exposes the corresponding enchant presets. Existing unlocks are recognized at login without spending another Tome. Unlocking does not switch or overwrite the current enchant setup.
- Enchant presets can be selected independently. Locked presets and unsafe-state changes are rejected.
- Ordinary ability unlearning now discards unowned historical spell ranks on Area 52, while retaining legitimate ownership by other specializations. This repair remains separately tracked from Prestige.
- Existing Demonic Leap, blessing and replacement-interaction fixes are preserved. No verification labels, tester certifications, enchant collections or DLLs are changed.

Close the game and update through the launcher after deployment. This package includes its matching client asset/feed update. Offline engineering checks passed; live gameplay certification remains with testers.

Upstream draft: https://github.com/jealous-sound/azerothcore-wotlk-coa/pull/8380
Independent specialization branch: https://github.com/CWO4PapaBear/azerothcore-wotlk-coa/tree/fix/area52-tome-specialization
The Area 52 backend is not imported into upstream. Source patches apply to the recorded Area 52 baseline; apply Tome before Prestige. No realm is activated by the upstream draft.
