# Area 52 quest corrections - expanded Batch 3

- Those Who Fell: the Unremarkable Stone can target Uneasy Citizens after removing their incorrect player-immunity flag. Their existing quest-item award and NPC immunity are preserved. Citizens receive their cowering animation and fear visual, and the map shows their search area.
- Bring the End: the objective marker points to Razorfen Downs, where the required skull drops, instead of Tirisfal Glades.
- The Balnirs' Rest: objective markers identify Jorum, Vara and Jarim Balnir at their existing spawns.
- Eighteen additional quests receive 32 objective areas, reconciled against this realm's objective targets and existing spawns. The Brill Stay a While turn-in uses the Tirisfal Glades map.

## Additional quest markers

- The Nature of Freedom (254064)
- Unexpected Results (254107)
- A Promising Path (1660007)
- Deciphering Radiation (1660010)
- Soaking the Masses (1660011)
- The Sister Who Never Returned (1660013)
- Transsubstantiating the Flesh (1660015)
- A Trail of Petals (1660017)
- The Way is Shut (1660019)
- So That He May Hear Again (1660021)
- Unease Makes Tongues Wag (1660037)
- Stay a While (1660054)
- Stay a While (1660065)
- The Aid of Theren-Dion (1660072)
- Stay a While (1660075)
- Thunderbrew's Hop (1660077)
- Stay a While (1660080)
- Elydna's Heirloom (1660085)

## Preservation and verification

Existing turn-ins, quest requirements, rewards, unrelated creature fields and previous Area 52 fixes are preserved. No ability, talent, Mystic Enchant or certification labels change. CoA class starting quests, the absent replacement Killing Fields chain and the absent Yak Dung NPC are not imported.

Offline verification passed against the exact deployed table schemas: actual production-hook backup, atomic four-table apply/reapply, exact rollback/repeat rollback, unrelated-row preservation and refusal to overwrite conflicting changes. Citizen quest-item, target condition, SmartAI chain and visual DBC records were checked. Marker checks validate existing targets within each proposed area; they do not certify live rendering or every underlying quest mechanic.

This is a server SQL correction. No client download, DLL change or server binary replacement is required. Source publication stays on a feature branch; no merge into main.
