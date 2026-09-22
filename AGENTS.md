# Bear Cave development workflow

- Main and PTR are separate. No Main activation or client changes while developing PTR unless requested.
- At each completed development milestone, run relevant checks, update release notes, review the diff, commit, push and verify the remote branch hash. Normal milestone commits/pushes are authorized by the owner. Never force push.
- If authentication or remote access blocks publication, report "local only" and provide the exact copyable push command. Do not claim activation or local commits imply GitHub is current.
- Publishing client release assets and promoting a channel are separate from source pushes. State explicitly which steps have completed.
- Keep HeroFreePick and More Minions in their own source repositories. Do not put proprietary client archives, personal settings, credentials, database exports or generated binaries into source history.
- Webhook credentials belong only on a future backend. Account requests remain disconnected until the owner configures that service.
- Mock/fixture tests do not prove live-client behavior. Preserve backups and fail closed on mismatched files, unsafe paths or an active game process.
