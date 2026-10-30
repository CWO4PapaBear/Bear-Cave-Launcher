# The Bear Cave - Updates

## Bot companion readiness repair

- Fixed a bot-login appearance initialization failure that left companions stuck at “Preparing” instead of reaching recruitment and Dungeon Finder readiness.
- Fixed Mystic Enchant setup commands truncating bot names at the space before “Bot,” preventing their assigned enchant loadouts from completing.
- Connected the Naturalist loadout’s Blessing of the Eternals enchant to its existing Earthliving behavior: its low-health bonus now participates in the native proc calculation on Area 52. Existing talent behavior remains intact.
- Recruitment messages now show the complete invitation command, for example `/invite Nicarlo Bot`. Wait for the ready whisper and include the “Bot” suffix.
- Preserved the existing 20-bot pool, archetypes, permanent heirloom equipment, Vanity sets, level matching, dungeon reservations and duel/release behavior. Bots are not recreated.

The October30 Worldforged verification, tester collection access and published client update are preserved. No client update or addon is required. No Verification or Certification labels change. These notes are prepared for publication only after successful activation and server readiness.
