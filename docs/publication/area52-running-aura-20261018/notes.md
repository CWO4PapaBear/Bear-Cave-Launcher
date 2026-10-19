# Area 52 — 15% running-speed aura

- Enabled the original Ascension 15% running-speed passive for Area 52 characters.
- Ordinary unmounted forward running is now 8.05 yards/second instead of 7, before other effects.
- Stronger ordinary running-speed bonuses, such as Sprint, take precedence. This is not an additional multiplicative base-speed increase.
- Mounted movement, swimming, flying and backward movement keep their existing rules. Slows and movement restrictions still apply normally.
- The passive is supplied on login and restored on resurrection when needed. No client download is required.

Engineering checks cover native registration, the original spell data, lifecycle callbacks, duplicate prevention, speed selection and configuration rollback. This does not claim live tester certification; no catalog statuses changed.

Upstream preparation is a standalone opt-in change. Other realms retain their existing behavior with Ascension.RunSpeedAura.Enable = 0. Area 52 explicitly enables it with 1; changing the setting requires a worldserver restart.
