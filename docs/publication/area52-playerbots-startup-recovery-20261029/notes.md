# Area 52 corrected reusable dungeon bot pilot and Arena 1v1

Prepared release notes. These changes are shipped only after the matching deployment reaches server readiness and publication completes.

- Adds a fixed pool of 20 Hero bots: 10 Alliance and 10 Horde. Each faction has two Mystic Knight tanks, two Naturalist healers and six Hoplite damage dealers. Their initial open-world level is 70.
- Dungeon Finder can use the reusable pool to fill missing roles. Available bots prepare for the human group leader's level, from 15 through 80, and use level-appropriate builds and equipment. Bots already in a group, dungeon, combat or another reservation are not reassigned or relevelled.
- Enables Dungeon Finder content through Wrath of the Lich King, subject to normal dungeon eligibility. The pool stays at 20; no population scaling or automatic bot PvP is enabled.
- Mystic Knight uses the current library build, ID 6404392635807108315 revision 14. Soul Link and final choices are retained. Mark of the Wild is deferred from level 62 to 63 in the bot snapshot to fit the available ability points. The saved library build is unchanged. Naturalist and Hoplite retain their reviewed pilot templates; automatic library synchronization is future work.
- Includes skirmish and rated 1v1 Arena support with Hero eligibility. Rated 1v1 uses the personal 5v5 team slot and refuses to replace an existing multi-member team. Bots do not automatically queue for arenas or battlegrounds.
- No new addon, client download or verification-label changes are included. Existing Certified records remain unchanged.

Engineering validation covers the native build and unit tests, level budgets and transitions, reservation/queue dispatch, account ownership and atomic creation, SQL bootstrap, package hook apply/verification/rollback, and Arena admission/personal-team behavior. Offline checks do not certify live dungeon or arena gameplay.

## Deployment and recovery

This is a server-only package requiring the normal approved restart. It preserves the deployed cross-faction and gameplay corrections. Source publication contains scoped core/module patches and provenance on a feature branch; it does not merge into main.

On activation failure, recovery restores the previous executable, configuration and source. Newly created, owned bot data is retained dormant for safe retry. It does not delete human characters or restore shared character/auth databases. An incomplete schema or newer conflicting edits stop for review.

## Startup recovery

The initial pilot rolled back before publication because its compiled module-configuration directory did not match the realm mount. This candidate corrects the build path and prevents fixed Hero pilots from falling back to generic-class creation when configuration is missing. The 64 incorrect characters on the two package-owned accounts are privately backed up and removed under exact ownership and content guards before the intended 20 Heroes are created. Human accounts and unrelated records are excluded.

Recovery restores removed rows while their scopes are empty, or retains a valid owned replacement Hero pool dormant. Unrecognized newer records stop for reconciliation rather than being overwritten. Original failed deployment artifacts remain unchanged.
