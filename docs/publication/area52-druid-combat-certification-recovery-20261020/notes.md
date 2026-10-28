# Area 52 — Druid control abilities and Clearcasting

- **Mass Entanglement:** applies Crippling Vines after damage breaks the roots, natural expiration or dispel. Root duration is capped at six seconds against players before diminishing returns. Its cannot-miss behavior preserves immunity. The follow-up slow uses the owner-approved untouched-client resistance behavior.
- Optional Spreading Roots propagation requires owning the corresponding enchant. Full enchant propagation verification remains separate.
- **Solar Beam** and **Ursol's Vortex:** existing silence, area, ownership and pull-lockout paths reviewed with focused offline engineering checks; their mechanics are preserved.
- These three base abilities move to **VERIFIED** after deployment, with matching tooltip labels and a Crippling Vines parent-certification link delivered through the launcher. Existing Certified records remain unchanged. Certification belongs to live testers.
- No new addon or DLL changes. Close the game and update through the launcher after publication.

Source changes are published as a frozen patch on a feature branch against the qualified deployed baseline. No gameplay/status changes are merged into main. Engineering checks use native functions with mocked engine adapters and source tracing, without gameplay environments.

- **Arcane Concentration:** Clearcasting now consumes its charge on the next eligible resource-cost ability, including Thrust and Thunder Clap. Area 52 only; existing cost, school and proc exclusions remain. This scoped repair does not promote the whole talent to Verified.

- **Dance of Death:** critical strike bonuses now require health below 75% and follow the current 2/4/6% rank. The capstone heals for 200 + 40% Attack Power and resets Intercept on an XP/honor-qualifying kill or use of Siegebreaker, with one shared five-second cooldown. Ordinary attacks and damaging spells no longer trigger it. Original-client tooltip wording restored for all three ranks; existing Certified labels preserved.

- **Backstab and Garrote:** on Area 52, every rank can be used from any direction against enemies that are not players or player-controlled. PvP rear-position requirements and other casting requirements remain in place. Opportunity is not required for this change.
- **Improved Victory Rush:** its parry-granted activation is consumed by the first Victory Rush instead of allowing repeated uses for the entire buff duration.
- **Toggle modes:** clicking an already active, self-owned Warrior stance, Hunter aspect, Paladin aura or Druid form turns it off on Area 52. Existing cancellation restrictions and Rage retention remain in place.
