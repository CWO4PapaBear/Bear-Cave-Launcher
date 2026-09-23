# 🐾 The Bear Cave PTR — 0.2.1-test.1

Close WoW, open the Bear Cave Launcher, select **PTR → Check / Repair → Update PTR**, then Play. This release brings the published client up to date with the local test fixes.

## 📖 Spellbook
- Keep individual learned class/talent-tree tabs, with Previous/Next controls when more than eight are needed.
- Separate custom tab buttons from stock refreshes so the normal spellbook does not overwrite them. Press **P** as usual.
- Dual Wield appears under **General**, avoiding an unnecessary Warrior tab.
- Classic and pet spellbooks retain their normal behavior.

## 🖼️ Player and pet portraits
- Restore the portrait-control addon loading and saved positions.
- Shorter resource bars and a default player position near the top-left corner.
- Hide leftover stock Death Knight runes while the custom player frame is active.
- Right-click the player or target portrait to lock/unlock; move it out of combat. Drag the player's name header to move the player frame.
- Primary pet gets its normal right-click menu. Secondary companion gets its own attack, follow, stay, stance and dismiss menu. Pet happiness remains visible.

## 🧟 Minions
- Includes the client spell definitions for the activated Abomination loadout: **Strike, Cleave, Disease Cloud (pet level 30), Scourge Hook (pet level 40)**.
- Captured Ghouls also unlock Disease Cloud at pet level 30.
- Disease Cloud lasts 12 seconds, costs 30 energy, has a 30-second cooldown, and deals Nature damage every 3 seconds equal to half the pet's level plus 5% of its attack power.
- The server name-save fix is activated: oversized captured NPC names use a family name. Borgoth the Bloodletter should save as **Abomination**. Capture/relog confirmation is still needed.
- The earlier Demon/Undead mappings are active. Elemental/Dragonkin work is not part of this release.

## 🧪 Please test
- Hybrid spellbook trees, page navigation, spell dragging/casting, and highest-rank filtering.
- Portrait position persistence after relog, right-click pet menus, rune visibility and pet happiness.
- Abomination capture, dismiss/recall, stable storage, relog persistence and skill unlock levels. Scourge Hook and Disease Cloud effects still need gameplay testing.

If a previously changed creature still displays its old type, close WoW and remove only **Cache/WDB/enUS/creaturecache.wdb** (use your locale folder if different), then relaunch. No class-label cache procedure is required.

**PTR only.** Main Server is unchanged. This publishes client files, not a new launcher executable. Personal settings and unrelated addons are preserved. The local fixes now belong to the published PTR package, so updating should retain them.
