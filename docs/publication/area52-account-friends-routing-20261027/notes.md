# Area 52 account-wide friends routing correction

- Friend-list requests now run through the server's world-thread dispatcher, avoiding concurrent access to the shared account friends list.
- Your existing account-wide friends, notes, Added as display and character-specific ignores are preserved. No friendship migration is repeated.
- Existing realm and cross-faction fixes remain included. The separate bot work is unchanged.

No client download or tooltip/status-label update is required. Offline native routing, build/unit, source, source apply/rollback and publication/deployment retry checks passed. Live gameplay acceptance remains with testers.
