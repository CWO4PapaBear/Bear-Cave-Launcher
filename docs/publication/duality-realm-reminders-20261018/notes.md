# Area 52 — Primary stat choices and reminders

Path of Duality is hidden only on Area 52, with Strength, Agility, Intellect and Spirit evenly spaced. Season 10 Free Pick and other realms retain Duality; its backend support is unchanged.

On Area 52, opening Character Advancement hides the primary-stat popup. Closing Advancement without selecting a primary stat prompts again. Missing-stat reminders also run after entering a dungeon or raid, accepting a quest, and leaving combat. Routine reminders have a 60-second cooldown; closing Advancement intentionally checks again. Combat defers that close-menu reminder until combat ends. Existing Manastorm/PvP checks are retained. These checks use client events and local stat state, with no polling or added server requests. Season 10's existing popup selection inside its Advancement menu is preserved.

This package updates the owner's local client only; tester launcher distribution is not included. Close the game for activation and reopen it afterward. No DLL, server, SQL, ability, talent, enchant or verification-status changes. Existing unrelated client fixes remain intact. Offline Lua checks pass; live visual acceptance remains with testers.
