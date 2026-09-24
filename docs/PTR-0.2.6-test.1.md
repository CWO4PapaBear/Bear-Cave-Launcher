# Combat preparation and Auto-Attack Forever — PTR 0.2.6-test.1

Close WoW completely, select PTR in Bear Cave Launcher, and update. No new launcher executable or server restart is required.

- Hero Advancement automatically closes when combat begins. Your pending selections remain saved: reopen after combat to continue. Nothing is automatically accepted or discarded. Combat also dismisses review and mode-choice overlays, even when a primary stat has not yet been selected.
- Auto-Attack Forever now falls back to melee when no usable ranged weapon is equipped. Characters without ranged proficiency no longer receive bow/equipment errors from distant right-click attacks. Melee still requires melee range.
- Disable automatic ranged attacks in Interface > AddOns > Auto-Attack Forever, through /aaf, or using the new draggable AAF minimap button. The preference is saved per character.
- Melee-only attacks preserve bear/cat form. Feral melee no longer forces a humanoid weapon-ready stance. Auto Ranged highlights only an actual ranged repeat; the standard melee pulse still indicates an armed attack while out of range.
- Includes the reviewed healing-tooltip data corrections and all prior PTR client updates, including bag sorting, pet/portrait fixes and Martial Fluidity.

Testing focus: please check bear-form animation consistency when approaching from range, sustaining melee and following targets out of reach with automatic ranged disabled. Report animation gaps and whether damage continues. Owner attack tests passed; broader animation testing remains open. Combat draft preservation passed Lua tests across Classic, Class+, Hybrid and Hero; please verify it in game.

Cumulative PTR update. Personal settings are preserved. Main Server unchanged.
