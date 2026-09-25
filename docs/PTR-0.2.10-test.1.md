# PTR client update 0.2.10-test.1

- Learned-area search now finds ability and talent names, including passive talents.
- Added tooltip-text search between Summary and the talent-tree tabs. Search follows Overview, selected class/tree, rarity, and ownership filters.
- Hybrid second-class selection uses circular class portraits with character-creation descriptions.
- Hero no longer highlights an original/selected class with the class-choice glow.
- Fixed the Battle Pass scrollbar's optional API call for stock 3.3.5 clients.
- Added the missing Swift White Hawkstrider saddle texture assignment while retaining the replacement model and earlier boar repair.

This release updates client files only and uses the existing PTR server build. No new launcher executable is required.

Not included: the unfinished Hero initial-selection path, Poisons Mastery/application changes, and custom-mode Charge/Thunder Clap stance changes. Classic stance rules remain unchanged. The private reward-spin experiment remains excluded.

Search/filter logic and Lua 5.1 syntax passed offline tests. The new UI still needs in-game visual testing; the Hawkstrider repair needs tester confirmation.
