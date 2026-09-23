# 🐾 The Bear Cave PTR — 0.2.2-test.1

**Close WoW → Open Bear Cave Launcher → Check / Repair → Update PTR → Play.**
No new launcher executable is required. This release includes both Patch-Z files and the current managed addons.

## 🖼️ Portraits and pet menus
- Correct the primary pet right-click menu.
- Move the unlocked player frame using the portrait/resource area, not only the name.
- Target and focus portraits support lock/unlock and dragging from their portrait areas.
- Keep the integrated resource display, pet happiness and existing portrait improvements.

## 📖 Hero Advancement tooltips
- **Tap Shift** to toggle expanded details on or off.
- Spell IDs, advancement IDs, Mastery inclusion and click instructions move into expanded details.
- Remove the obsolete blanket “server committing is unavailable” notice and internal browse-grouping notes.
- Improve paragraph spacing. Resolved numerical values are **light blue**; unresolved descriptions remain **yellow**.
- Resolve 110 affected spell/rank descriptions using PTR spell data and supported formulas, including Serpent Sting’s total damage over 15 seconds. 65 unresolved descriptions remain highlighted for review.

## ⚔️ Hybrid equipment and combat
- Hybrid characters receive the weapon and armor proficiencies available to either selected class. Existing Hybrids reconcile at login; normal level gates remain and trained weapon skill is preserved.
- Equipment class requirements now display as satisfied for the confirmed second class. Unmet level and other requirements stay red.
- Server fix: ranged spell openers no longer disrupt Auto Attack Forever’s ranged/melee switching.
- Server fix: stop withheld original-class starter spells from returning during login and producing repeated unlearned alerts. Verified across two logins and a full client restart.

## 🧪 Please test
- Both classes’ equipment, relog persistence, and level-40 mail/plate unlocks.
- Secondary-class item tooltips in bags, chat links and comparisons.
- Pet right-click menus; player, target and focus movement and saved locks.
- Tap-Shift tooltips, resolved damage/duration values, and yellow unresolved descriptions.
- Ranged spell openers and repeat attacks; report any starter-spell removal messages after reconnecting.

## 🔄 Cache refresh
Close WoW before updating. If a previously changed creature still shows an old type, remove only **Cache/WDB/enUS/creaturecache.wdb** (use your locale folder if different), then relaunch. No per-character class-label cache procedure is required. Keep your WTF settings.

**PTR only; Main is unchanged.** Personal layouts, account settings and unrelated addons are preserved. This update replaces managed client files with the reviewed current testing versions. Existing Abomination/Ghoul, pet-control and spellbook updates remain included; unfinished Elemental/Dragonkin work is not newly activated by this release.
