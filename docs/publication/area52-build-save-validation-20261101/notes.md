# Build Architect: clearer validation before saving

- Save Build now stays disabled whenever the complete build validation fails, including invalid learning order, missing required information and rarity gem overruns.
- Hover the disabled Save button to see the reported problem. Rarity errors include the rarity, level, gems used and allowance. Learning-order diagnostics show available level, point-budget and spell/rank details.
- Checks cover the entire planned build, and run again when confirming Save. Correcting the build restores Save when all checks pass.
- Featured Draft assignments, existing builds, Mystic Enchants and tester certification records are preserved. No verification totals change from this UI correction.
