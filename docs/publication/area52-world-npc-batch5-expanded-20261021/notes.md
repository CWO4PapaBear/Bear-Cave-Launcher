# The Bear Cave - Updates

## Expanded Batch 5: world, vendors and NPC corrections

- Thermal Anvil now uses its normal item-use behavior and creates the missing forge/anvil workstations with a five-yard working range. Removed its invalid cache association.
- Blackpaw Gnolls and Scavengers display their intended flee warnings.
- Guard Slip'kik uses Shield Wall at 30% health or lower, once per encounter reset, rather than repeatedly on a zero timer.
- Added 1,098 missing food and drink listings to 78 existing vendors. Existing goods, prices and ordering are preserved; new listings are appended.
- Portable Sawmill and Compact Portable Sawmill use a five-minute cooldown. The Portable Sawmill item's one-hour override is corrected too.
- Gorn Axefist offers his existing riding-training list through a restored training menu. Existing riding level, skill and price requirements are unchanged.
- Corrected the explicit upstream live scales for Lil' Chromaggus, Baby Kodo, Night Web Spider Hatchling, Lootbot 3000 and Fix-o-Tron 5000. Their models and combat statistics are unchanged.

This is a server-data update. No client download, ability verification-status changes or certification changes are included. Existing Area 52 fixes are preserved.

Engineering qualification uses exact-schema isolated SQL apply/reapply/rollback and conflict guards, plus focused native source fixtures. Gameplay certification remains with testers.
