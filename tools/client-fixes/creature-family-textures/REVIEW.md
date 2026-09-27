# Creature family texture repair — local test candidate

Reports: Gnarl (entry 17310/display 16975), Hamhock (1717/3250), Wooly Kodo (3237/10914). IDs traced from the exported PTR creature_template and creature_template_model tables.

The recurring defect is replacement meshes retaining stock display texture slots. Ascension's display rows retain these same assignments, so blindly copying its rows does not solve this pack's replacements.

Candidate: 64 display changes: 14 Ancient of War displays gain matching foliage/body layers; 44 OgreMage displays use the replacement Mage armor atlas for their body color; six wooly kodo displays use existing dedicated model 4005 with its body/fur textures. Both cumulative archives preserve all other files, including Grappling Hook.

Two exact OgreHighmaulKing reflection dependencies come from their original source paths. Two Kodo reflection paths alias the modern Kodo mount reflection map (recorded source and hash), rather than substituting a body texture. These need visual acceptance along with the main repairs.

Ogre display 6168 (noncanonical OgreSkinYellow512) is deferred. Broad scan findings are candidates, not confirmed visible defects: unused texture slots and runtime-selected skins can appear missing. No global basename substitution or bulk DBC replacement is authorized by this plan.

Checks: all selected textures decode; selected model/skin files exist; each output archive is read back completely; only planned display fields change. Installed locally with verified backups; in-game verification remains pending. No launcher client release.

Run from the original workspace with the bundled Python:

```powershell
& 'C:/Users/danie/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' outputs/Creature_Texture_Family_Repair/Audit.py
```

```powershell
& 'C:/Users/danie/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' outputs/Creature_Texture_Family_Repair/Build.py
```

```powershell
& 'C:/Users/danie/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' outputs/Creature_Texture_Family_Repair/Sweep.py
```

Close WoW before Install.py. It verifies source/candidate hashes, backs up both live archives, checks the process again, and rolls back on copy failure. No server restart is necessary. Check all three reported creatures plus another ogre mage, a snow/diseased ancient, and a wooly kodo variant before launcher publication.

Scripts use the existing original MPQ library at outputs/Adaptive_Auto_Attack/mod-adaptive-autoattack/tools/lib/mpq.py and the established precedence/DBC helpers in outputs/Replacement_Model_Audit/Scan.py. Proprietary archives, atlases, database exports and generated candidates remain local.

Broader sweep: 19,027 replacement displays checked. 58 additional missing BLP dependencies (1,780,728 source bytes) restored using exact paths and unique source hashes across the reference archives. They add to the four family dependencies above (62 total). No body skin guesses or ambiguous source versions are applied. The 2,363 original heuristic flags were not all confirmed defects; the report remains a review queue.

Publication snapshot: copy this directory to outputs/Creature_Texture_Family_Repair in the documented workspace to replay. The included dependency manifests use archive basenames resolved under the reference Data directory by Build.py; generated archives, backups, atlases and database dumps are excluded from Git. Build first uses the reviewed manifests; run Sweep and Discover-Dependencies for a fresh follow-up audit rather than assuming all new findings are approved.
