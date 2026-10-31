# Censor-Justice case system removed

Build: **0.4.0-alpha.20-dev.42**. Removed on 2026-10-27 at the user's request. Personnel remains the accepted **dev.41** baseline.

## Scope completed

Removed **145 old files**: 88 under `common`, 20 event files, two GUI files, and 35 localization files. This includes the investigation/audit/case pipeline, evidence gathering and hearings, Justice review and sentencing, imperial/chancellery case disposition, custody/enforcement timers, ministerial misconduct oversight, procedural returns/rebuttals/remands, the register and its scripted GUIs, case interactions/decisions, case-law screens, and the q204-q211 debug fixtures.

The case startup/pulse hooks and the secret-exposure interception are removed. The native secret notification behavior is supplied by the game again. No script can create an old case or oversight story. No new Censor/Justice gameplay is introduced; a future revamp starts with a fresh design.

## Personnel protection

All **155 pre-existing files outside the removal set and build descriptor are byte-for-byte unchanged**. This covers Personnel's appointments and jurisdiction/vassal handling, queues, marks, tasks, AI, laws, service records/reviews, private patronage/bribery, examination honors, traits/assets, localization, and existing documentation. The shared Ministry interaction category and all nine central ministerial succession approvals are preserved, including approval of Censor and Justice officeholders. Vanilla offices and their native behavior remain available.

The protection audit is in [CENSOR-JUSTICE-REMOVAL-AUDIT.json](CENSOR-JUSTICE-REMOVAL-AUDIT.json). It lists the removed paths and SHA-256 hashes of all 155 unchanged files. The only modified existing non-removal file is `descriptor.mod`, to identify dev.42.

## Minimal dependencies retained

These are required to preserve Personnel and existing saves. They contain no investigation/trial workflow:

- **Shared office predicates:** `mam_shared_office_eligibility_triggers.txt` contains three definitions extracted verbatim: office eligibility, current Chancellor identification, and native ministry candidate qualification. Historical function names remain stable so no Personnel caller is edited. Existing read-only legacy office-bar checks are retained exactly; nothing in this build can create a new judicial bar.
- **Native qualification and ministry handoffs:** `zz_mam_shared_native_eligibility.txt` and `zz_mam_shared_minister_handoffs.txt` are byte-identical relocations of the prior shared bridges. They continue to support Personnel's appointment and central minister approval routines.
- **Three inert former record hooks:** `mam_removed_case_compat_effects.txt` provides empty payment/offer/appointment hooks called by unchanged Personnel patronage code. They were already disabled before removal and now have no case dependencies at all.
- **Retired saved-law identifiers:** five already-inert laws and two hidden groups remain under neutral filenames because Personnel's existing retired-law cleanup references them. They cannot start, be adopted, kept or passed. Their localization describes only retirement; old policy descriptions and decisions are removed.
- **One-shot saved-story retirement:** `mam_removed_case_cleanup_story.txt` retains only the two old story identifiers. Their sole action is `end_story`: on setup, owner death, or the next one-day maintenance interval. No case handlers, variables, evidence, judgments, UI or new-creation paths remain.

Historical title transfers, imprisonment and saved eligibility bars are not reversed. Reversing past judgments would alter the accepted Personnel/realm state and is outside this source-removal task. Existing Personnel documentation is preserved as historical evidence, so references there to the formerly disabled system describe the earlier build; this document records its removal.

## Verification

Passed source checks:

- All 145 removed paths are absent; all 155 protected hashes still match.
- Three extracted shared predicates match their original bodies. Three relocated files (two bridges and the hidden law definitions) were verified byte-identical before the old paths were deleted.
- Balanced blocks, unique database keys and required UTF-8 BOM across **130 remaining common/event scripts**; GUI blocks are balanced.
- Remaining custom effect/trigger references and custom event targets resolve.
- All remaining `mam_cj_` definitions are on an explicit allowlist of shared APIs, inert compatibility hooks, hidden saved-law keys or one-shot saved-story teardown.
- No old case creation, case/oversight tick function, runtime toggle, startup handler, secret-exposure interception, register GUI, or q204-q211 test code remains.
- The cleanup stories can only end themselves. Retired laws/groups remain unavailable and their localization keys resolve.

These checks do not run CK3. Native game files and installed Workshop mods were not edited.

## In-game smoke check

Fully restart CK3 so the engine unloads removed scripts. In a separate save, check that no old case/register decisions or interactions appear and that ordinary Censor/Justice offices still exist. Any already-saved old story should end after unpausing; no new cases can be created by this build.

For Personnel, smoke-test one senior vacancy/appointment and one central minister approval, confirm the Manage Talent/Royal Favor assignments remain present, and check the honors row. Those features were preserved rather than redesigned. A fresh log should contain no missing custom helper or case-event caller errors from the remaining source. Save-specific queued events from removed content and story-retirement timing still require engine confirmation.
