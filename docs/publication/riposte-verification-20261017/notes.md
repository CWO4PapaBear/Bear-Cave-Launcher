# Area 52 Riposte correction

Riposte now becomes available after a successful parry when your character knows the ability. Its five-second opportunity clears correctly when it expires or reactive states reset; dodges and blocks do not open it.

Riposte's 20% melee attack-speed reduction now belongs to the shared exclusive slow group. Comparable slows use the strongest applicable effect instead of stacking together.

Its intended values remain unchanged: 150% weapon damage, one combo point, 10 energy, a six-second cooldown and a 30-second slow. The conditional Blademaster effect remains intact. No client update is needed.

Engineering qualification covers production reactive dispatch and cleanup, weapon-percent calculation, combo/slow handlers, acquisition, conditional Blademaster behavior, compilation and unit tests. The SQL change passed disposable-database backup/apply/verification/rollback and retry checks. Live gameplay certification belongs to testers. Existing VERIFIED and CERTIFIED labels are preserved; this repair does not increase progress totals.

Source publication is a scoped patch against the deployed Area 52 source candidate on a feature branch, not a merge into main. This announcement is published only after successful owner activation and server readiness.
