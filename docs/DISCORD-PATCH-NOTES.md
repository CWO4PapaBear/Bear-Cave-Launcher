# Discord PTR patch notes

In repository Settings → Secrets and variables → Actions → New repository secret, create `DISCORD_PATCH_NOTES_WEBHOOK` with the complete existing Discord webhook URL. Confirm in Discord that this webhook belongs to the Patch Notes channel. Do not put it in a repository file or launcher configuration.

The PTR Discord patch notes workflow runs after a push changing channels/ptr.json on main. It checks that the pointer is publicly current, verifies the pinned manifest, checks the release is published, and sends the release PATCH-NOTES.md as a gold Discord embed with update instructions. Long notes are shortened and linked to the full release. Mentions are disabled. Ordinary source pushes, draft uploads and Main changes do not trigger announcements.

For the already published first release, open Actions → PTR Discord patch notes → Run workflow after adding the secret. Manual runs and reruns can post again; inspect the channel before retrying an uncertain delivery. There are no automatic delivery retries. A failed notification does not undo a client release.

Local preview (no webhook used or message sent):

```powershell
python tools/announce_ptr.py --dry-run
```

This webhook is only for public patch announcements. Account requests remain disconnected and require a separate private backend/channel.
