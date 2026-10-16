# Shared talent rank restoration repaired

Unlearning a Free Pick talent now forgets its removed ranks. Relearning one point no longer restores previously learned higher-rank bonuses. The repair uses the talent catalog and covers ranked talents generally, including Arcane Fortitude, Arcane Mind, Mind Mastery, Reckoning and Raze.

Existing excess talent ranks are reconciled against current investment on login and selection synchronization. This corrects both stale higher-rank spells and their passive effects. Log out and back in after deployment to reconcile an existing character.

Ordinary ability rank history is preserved; this change does not alter Prestige or level-reset handling. No client download is required. Existing Certified labels and verification totals are unchanged.

Engineering validation: production build, 22 source checks, unit check, and focused offline regression covering 1,639 multi-rank catalog records and 4,675 purchased-rank cases. Player/aura storage is mocked in the focused regression; live tester certification remains separate.
