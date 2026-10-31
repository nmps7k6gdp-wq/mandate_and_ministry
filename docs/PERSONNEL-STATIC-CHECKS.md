# Personnel and ministerial static verification - dev.41

Passed source checks:

- Balanced script blocks across 223 script files; unique database keys (additive on_actions excluded).
- Custom scripted effect/trigger/value references and the new ministerial/senior event targets resolve.
- New ministerial event, decision, interaction, opinion and custom-localization references resolve. Script files and new English localization retain UTF-8 BOM.
- All nine ministry-to-council-position mappings match installed vanilla definitions. Vanilla files were read only.
- Exactly three active custom laws remain, all in senior territorial appointment authority. Twelve retired compatibility keys cannot be adopted, kept or started and have no policy effects; their groups are hidden and have no defaults.
- No script can pass any retired law. Cleanup covers all twelve saved law choices and their cooldowns while preserving appointment-authority selections.
- The custom recruitment score bonus and current senior examination gate are removed. Existing examination qualification/distinction assessment values remain.
- Death markers precede deferred ministerial capture. Installed holders, exact title/file identity, current authority and displayed incumbent are rechecked before committing a choice.
- Upper and lower reviews use separate FIFO leases on h_china, with live-lease preparation and duplicate-presentation guards. Marked nominees are explicitly scanned and deduplicated from automatic alternatives.
- Native ministry title/council handoff and synchronization fallback precede success credit. A changed holder after partial failure can remain under review. Unanswered reviews have no automatic approval deadline.
- Opinion and stress previews are conditional, and custom success consequences are applied only after title/seat postconditions pass.
- Previous senior territorial capture/queue/vassal snapshot code remains in place; Censor-Justice runtime remains disabled and the register remains unregistered.

These checks do not execute CK3. They cannot verify callback order, native title/council transactions, source-office side effects, save migration, UI layout or final stress scaling. The combined engine test remains pending.

Use [the ministerial succession test matrix](MINISTERIAL-SUCCESSION-REVAMP.md) for the nine offices, marked alternatives, simultaneous deaths and authority changes. Retain the dev.35 territorial tests: simultaneous independent governor deaths, lateral-source vacancy, empire-plus-kingdom bundles, vassal death during custody, and imperial confirmation. Test vassal snapshots from a save before the deaths; older completed grants cannot be reconstructed from the new data.

Additional dev.37 checks:

- Three custom law icon filenames match the law database keys. Each is a valid 96 by 96 native DDS mask, byte-for-byte identical to its selected imperial-bureaucracy source.
- All three law `_effects` keys exist, with resolved shared description references; these are the strings the native tooltip displays.
- Imperial-confirmation portrait scopes have initialization and a current-minister/emperor fallback. Approve/return/pending labels and their tooltip keys resolve.
- Approval tooltip conditions follow eligibility/source-readiness guards; opinion is bound to the actual sponsor/candidate, and stress previews run on the actual Personnel recommender.
- New and edited English localization values are well-formed single-line UTF-8 BOM entries.

In-game visual verification of law icons, hover descriptions and the two-person imperial audience remains pending after restart.

Additional dev.38 localization check:

- All three active law effects expand to four native bullet lines with matching hanging-indent tags and closing format tags.
- Every linked concept resolves to an installed native concept or alias.
- Edited localization syntax and UTF-8 BOM pass. This patch changes tooltip formatting only; existing script behavior and native icon assets are unchanged.

Additional dev.39 source checks:

- Structure, unique keys, helper/value references and UTF-8 BOM pass across 223 scripts.
- Native civilian appointment type is preserved exactly apart from one career-score term; shared military/Grand-Marshal scoring is no longer overridden.
- Royal Favor has an independent documented on_monthly effect on the Personnel clone; the old child callback below the native side-effect gate is removed.
- Initial/resumed observation and annual evaluation order are explicit; AI commendation clears the prior adverse modifier.
- Chancellor AI policy has an annual term, current-authority checks, quarterly wake-up and protections for imperial/manual instructions.
- New nomination weights, actual personal-connection conditions and ownership guards resolve. New diagnostic logs record choices, refreshed favor, service awards and priority selection.

The latest existing runtime log proves the old dead-owner error, not execution of the new fixes. Task effects and balance remain unverified until the dev.39 in-game run in the linked audit checklist.

Additional dev.40 examination integration checks:

- Balanced script/GUI blocks and script/localization BOM across 224 common/event scripts.
- All three current-native examination bridges retain exact native bodies except the MAM recorder calls.
- Four read-only honor GUI queries and their tooltip keys resolve; highest-honor states are mutually exclusive.
- Three 120 by 120 DDS badge files match the installed Workshop originals byte for byte; decoded artwork inspected.
- No old activity override, lowborn restriction or recurring reward modifier introduced.
- Palace recorder consumes native finalized placement variables with guarded optional second/third places.

The shared native palace widget registration, engine reward callbacks and final tooltip layout still need the [examination test checklist](EXAM-DISTINCTIONS.md). No in-game validation is claimed.

Additional dev.41 examination recognition checks:

- Structure and required BOM pass across 231 common/event scripts; GUI blocks are balanced.
- New event, scripted helper, GUI query, trait icon/name/description and localization expansion references resolve.
- Current native Merit-tooltip body has exact source parity apart from the always-visible honors-row insertion; three native examination bridges retain their native bodies.
- Laureate is one permanent fame trait with dynamic grades, zero generation weight and +5 shared opinion. No recurring Merit or Diplomacy is added.
- Trait restoration cannot pay awards. Actual completion uses upgrade-only payment ledgers; the player receipt records actual paid Merit/Prestige differences.
- Sponsorship checks current authority and sufficient Prestige; all audience effects recheck living status, realm membership and unacknowledged grade.
- Favored-candidate snapshots run before title transfer and their opinion effects are inside successful grant/synchronization branches. All four call sites supply required template parameters.
- The three copied honor textures retain their existing verified source hashes and dimensions.

These checks do not verify engine event/root semantics, final badge/trait rendering, active-mod GUI conflicts or transaction callback order. Use the updated [honors test matrix](EXAM-DISTINCTIONS.md) after restart.

A limited source evaluator also passed 256 mixed MAM/legacy flag and pass-evidence combinations, all three payment ceilings, upgrade differences, repeated completion, persisted-state replay and trait-only restoration. This evaluates the flag/ledger subset of the source; it does not execute CK3 scheduling, UI, native callbacks or title transactions. Sponsorship's native score line is conditional so unendorsed candidates do not receive a zero-value sponsorship entry.

Live-log follow-up: CK3 prefixes trait-icon filenames with `gfx/interface/icons/traits/`. The initial full-path trait entries produced an invalid doubled path during live reload; corrected to relative filenames with three exact local copies in that directory. The badge-row textures keep their full GUI paths. The same live-edit log contains missing dependency/localization/namespace messages from intermediate files (including the now-removed `is_valid` option field). A clean restart is required to distinguish resolved hot-reload messages from new runtime failures; the finished patch is not claimed engine-verified.
