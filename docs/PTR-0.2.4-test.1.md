# The Bear Cave PTR — 0.2.4-test.1

Close WoW, open Bear Cave Launcher, select PTR, then Check / Repair and Update PTR.

## CleanupBags: backpack sort button

- Adds a broom button to the top-right of the open backpack.
- Click to sort and combine bag stacks. Ctrl-click sorts the bank; Shift-click sorts bags and bank. Use bank actions while at a banker.
- Uses the existing PTR AutoSort server module. No chat command needs to be typed.
- After updating, enable CleanupBags in the character-selection AddOns list if necessary. Restart WoW to discover the new addon.

CleanupBags by silviu20092: https://github.com/silviu20092/CleanupBags
Upstream revision: d5543616cd5e67a359bf966743b431722aaea41c. Installed unchanged; in-game button testing remains pending.

## Current PTR balance experiment — rollback candidate

The server now uses shared base attributes and health/mana progression for Hero and Hybrid. Hero starts at level 1; Hybrid adopts the shared values when selected at level 10 or later. Class+ keeps its class progression. Existing Hero/Hybrid characters recalculate at login.

Every base attribute is 20 + level, before racial modifiers and bonuses. Base health/mana is 115/190 at level 10 and 7,350/4,050 at level 80, with faster growth after level 50. Please report poor survivability, excessive mana availability, or unexpected spell costs. This is an experimental server change that may be rolled back; the launcher does not install the server change.

This cumulative release retains all previous PTR client updates, including Auto-Attack Forever, portraits, spellbook, tooltips, Hybrid equipment, and More Minions stables. Personal settings and unrelated addons are preserved. No cache deletion or new launcher executable is required. PTR only; Main is unchanged.
