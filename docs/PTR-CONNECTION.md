# Automatic PTR connection setup

The launcher configures realmList after Update and before Play. It handles locale Data folders, an existing root realmlist, and an existing WTF/Config.wtf realm override. Other settings are preserved. Originals are retained under .bear-cave-launcher/realm-backups. WoW must be closed; linked paths are rejected.

The owner supplies local/connection.json (ignored by Git):

```json
{"schema": 1, "channel": "ptr", "address": "ptr.example.com"}
```

The build requires and embeds this deployment file. No server address belongs in tracked source. This keeps the address out of Git history, but anyone receiving the package can read it. A hostname is preferable for hosting changes; it does not conceal its destination IP. No credentials belong in this file.

Existing launcher versions do not self-update. Testers must download and extract the newly configured launcher package once, select their PTR client folder, then use Update or Play. No manual realmlist editing is required.

Local automated checks cover fresh clients, non-English locales, saved realm overrides, backups, repeat runs, rollback on an interrupted setup, invalid addresses and an active-game guard. Live external connectivity still requires a real address, reachable auth/game ports and correct server realm advertisement.

Public CI uses --unconfigured and deliberately contains no address. These builds cannot Update or Play until privately configured. Owner-distributed builds embed the ignored deployment file and need no tester setup.
