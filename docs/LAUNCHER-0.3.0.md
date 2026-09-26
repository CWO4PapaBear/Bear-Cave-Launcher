# Bear Cave Launcher 0.3.0

- Adds automatic launcher update checks at startup, independently of game patch updates.
- Verifies downloaded updates and preserves the previous installation for recovery.
- Preserves private connection settings and the selected client folder.
- Configures native Windows clients for Direct3D 9; keeps Wine/Proton renderer settings unchanged.

Existing testers must receive the owner-distributed configured ZIP once. After that, future launcher updates use the new launcher channel. The public code-only update asset intentionally excludes private connection settings and is not the initial configured installer.

Game client release remains PTR 0.2.13-test.1. No server restart is required.
