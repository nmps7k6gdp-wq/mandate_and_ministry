# Censorate implementation tracker

Dev.66 integration: the separately authorized [Justice module](JUSTICE-IMPLEMENTATION.md) adds explicit senior referrals from Censor findings without replacing administrative censure. Actual authored judicial demands/unauthorized actions can be inspected using read-only receipts and existing skill-based detection; a native pardon or hook alone is not corruption. False certifications now record their actual choice date for prospective warrant eligibility. Existing inspections lacking that new date remain administrative records. New criminal grounds require a separate explicit imperial warrant; Censor never automatically convicts from a receipt. See [Justice tests](JUSTICE-TESTING.md); engine acceptance is pending.

Final dev.66 source build passed all ten staged suites, including all 13 Censor tests, 23 Justice contracts and 159 unchanged protected files. Censor output remains 11 files/15 events/110 definitions, with 298 English keys after contextual Justice receipt/referral text. Native original-source pins passed. No engine, visual or AI acceptance is claimed.

2026-10-31, dev.65 (introduced dev.62). The user authorized design and creation of a dynamic Censor system after reviewing the independent-inspection proposal. This replaces the earlier one/two-popup limitation. **Source implementation; CK3 acceptance untested.** Read [current state](MOD-CURRENT-STATE.md), [native audit](CENSOR-VANILLA-AUDIT.md), [historical basis](CENSOR-HISTORICAL-DESIGN.md) and [test checklist](CENSOR-TESTING.md).

## What is authored

- Independent player inspection interaction and a three-person senior agenda; Emperor may request a subject without prescribing guilt.
- AI initiative, actual trait/relationship target priorities and connected ministerial defenders; one institutional inspection at a time.
- Private hearing, formal summons or intimidation. Harsh methods yield Dread but visible social costs and an attributable abuse record.
- Subject cooperation, a lawful scope challenge, explicit obstruction/concealment or an admission tied to actual existing patronage.
- A live certification dilemma: wait/check, state limits, or knowingly sign beyond verified material. Verification may discover a real false return; uncertainty never creates guilt.
- An allied/concerned minister or Chancellor can support scrutiny, defend an official or demand safeguards. Other officials can initiate one additional safeguards petition through Ministry.
- Censor can compare returns, consult Justice, follow the actual appointment payer, demand a coerced confession or propose a private favor-for-silence agreement.
- Native Favor Hook only on explicit agreement; no invented money. A refusal or report to emperor can turn the bargaining attempt against its actual author.
- Findings distinguish supported exchange, explicit obstruction, admitted conduct and detected false attestation from a political objection or a deliberately overstated accusation.
- Closure, correction, supported direct censure, impeachment or remonstrance. Emperor can censure, protect, require more work once, rebuke an abusive investigator or authorize a guarded removal.
- A Censor can accept protection, press the memorial once or offer resignation. Emperor can uphold censure, stand firm, mediate or remove the responsible current Censor through the existing handoff.
- Role-specific result correspondence and ten-year institutional archive. Private settlements do not automatically disclose themselves to emperor/defenders; an emperor who requested scrutiny receives only a neutral closure notice, and known facts are never erased. No register window or new evidence currency.

## Narrative approach

These are choices made during play, not random retrospective crimes. A frightened or deceitful official can obstruct or sign a false return; an honest official can challenge excessive scope. A cruel Censor can use threats even where the original records prove nothing. An ally can defend a useful official despite evidence. Justice can separate sufficiency from suspicion or intervene personally. Emperor may retain an official despite a supported finding, while Censor risks their own position by pressing the issue.

Descriptions reflect actual corroboration, obstruction, false return, methods, defenses and safeguards. Office-specific certification text distinguishes Personnel, Revenue, Works, War, Marshal, Rites, Justice and Chancellor duties. Trait stress previews use native effects and contextual conditions. Names are linked through native UI names; option emphasis uses native bold formatting. Letters handle demands/advice/results; contested multi-option decisions use portraits and character events. Native rendering still needs visual verification.

## Gameplay controls and limits

| Control | Source behavior |
|---|---|
| Capacity | One active inspection on `h_china`; connected participants share that record |
| Scope | Titled public officials county through territorial empire, plus central ministers; unlanded recorded payer is a witness only |
| AI selection | Senior officials only; traits, real rivals/friends/house and actual shared faction/bloc influence focus and defenders |
| Initiative | Startup and documented quarterly sovereign pulse; only AI Censor auto-starts |
| Progress | Weekly institutional story worker; ordinary stage waits 7?28 days |
| Rest | 180 days after closure for automatic initiation; two-year subject selection cooldown |
| Pending human input | No silent AI choice; current reviewer can recall; 90-day presentation lease permits recovery |
| Exceptional loops | One advisory opinion, one connected-payer hearing, one private proposal, one extra petition, one imperial return and one renewed memorial |
| Outer lifetime | Three years; expires without converting uncertainty into guilt |
| Archive | Ten years after closure; no GUI registry |

There are no automatic blanket policy/appointment/payment vetoes, fund seizure, fabricated criminal grounds, court trials or direct arrests. Existing protected payroll, grants, campaigns, examination honors and appointment scores are untouched.

## Exact consequence contracts

- Supported censure, once per file: -50 Influence; Publicly Censured for 2 years (-15% monthly Influence, -5 General Opinion); -25 Opinion of Censor for 5 years. Vengeful/Wrathful subjects can become native rivals when allowed.
- Corrected fault: Reconciled with Oversight for 1 year (-10% Stress gain), +15 Opinion of the deciding Censor for 3 years. No payment or eviction.
- Fair closure: +15 Opinion for 3 years; no scheme currency/reward farming.
- Measured supported disposition: nonstacking Trusted Inspector for actual author, 3 years (+10% monthly Influence, +5 General Opinion), provided no recorded abuse.
- Threat/coercion: +10 Dread each actual choice; Feared Censor 3 years (+10 Dread baseline, -10 General Opinion). Opening intimidation also causes -25 target Opinion for 5 years. These choices record the actual abuser.
- Imperial rebuke: recorded abuser loses 75 Influence; Discredited for 3 years (-20% monthly Influence, -10 General Opinion), Restrained for 2 years (-10% monthly Influence; harsh methods/custom private demand blocked).
- Official defense: target +20 Opinion of defender for 5 years, Censor -15 Opinion of defender for 3 years. Friend/family/bloc/faction influence AI behavior; no connection proves guilt.
- Imperial protection: target +20 Opinion of emperor for 5 years; three-year exclusion from automatic inspection selection. It does not erase evidence.
- Native retirement: only after verified handoff, native 3-year appointment timeout. Removal without a supported finding produces 10 imperial Tyranny only after a confirmed departure.
- Stress is applied only for the actual choosing character and current applicable condition; native trait/stress modifiers determine final values.

Modifiers refresh without stacking. Institutional sanctions do not repeat on a stale event. This source does not promise engine acceptance of native retirement or relation callbacks before testing.

## State, author identity and review lease

`mam_censor_inspection_story` belongs to the sovereign and is indexed by `title:h_china.var:mam_cen_active`. It retains actor/office/date, stage, sequence, current reviewer, due/lease dates, reply, admitted evidence, legal advice, defense, personal authors and disposition.

Every actionable event binds a story, subject, expected stage and sequence token. Options repeat these guards at commitment, including the recipient's current relevant role. A changed reviewer increments the sequence; another stage/closed file invalidates an old option. Reviewers are recomputed weekly from actual offices. An active story survives Censor/Emperor succession via institutional ownership. The actual abuser, fabricator, bargainer, memorial author and resigner are separate personal references; later holders are not their substitutes.

Current code does not auto-select an unanswered human response. Dead/departed subject or unavailable sovereign/outer timeout closes without new punishment. A missing Censor pauses ordinary presentation; serious imperial decisions can still finish. Engine tests must verify these transitions and native story-owner timing.

## Evidence adapters and future departments

Personnel adapter is read-only: `mam_personnel_patronage_story`, exact minister and payer, actual payment/date and successful `mam_patron_appointment`/`mam_patron_appointed`. It admits a linkage rather than treating any qualified relative as corrupt. Source identities reviewed by this new module are indexed in its own realm list; the original story is never edited.

Revenue adapter is read-only: `mam_pc_receipts` can establish the presence of a legitimate contribution. It is expressly not an embezzlement detector. No assumption of a finished unauthorized-payment ledger or complete native fiscal history. `mam_cen_imperial_seen` records presentation to the sovereign; private bargaining is unavailable after that presentation. Settlement details are restricted to its parties, with outsider correspondence redacted and one result per actual human recipient.

New certification/obstruction/threat/bargaining acts belong to this module. Hidden actual false attestation and discovered false attestation are separate fields. A random verification outcome controls detection, not whether the subject actually chose to falsify.

Future modules should publish narrow immutable official-act identity, actor/office/time, source and authorization facts. Censor owns scrutiny and findings, not their underlying action. Future Justice may consume a closed factual referral and return a legal assessment through an explicitly versioned adapter; no such criminal-trial API is claimed now. No current matter waits indefinitely for future Justice.

## Removal boundary

Only emperor can authorize a removal. Recheck current subject identity, exact inspected office, family-title safety, peace, native ministry successor eligibility and supported jurisdiction. Central ministries call existing `fired_minister_position_effect`; the protected handoff checks candidates. Supported senior governors call accepted `mam_senior_capture_effect` so exact jurisdiction, custody and Personnel queue remain owned by Personnel. Lower governors use the native `force_step_down_landed_titles` retirement operation.

Verify the departure and, for senior governors, a real pending custody file before recording success/timeout. An unconfirmed handoff returns to the imperial decision with that removal option blocked for this file, preserving other dispositions. It cannot automatically retry a possibly partial native operation. There is no fallback arbitrary title grant, timeout or false success. Native operation and edge-case vassal preservation require engine acceptance. A private favor can be accepted only while its actual proposer still holds the Censorate; a later Censor cannot inherit that personal bargain. A subject who becomes Censor is recused to imperial review; a subject who becomes emperor or leaves public office is closed without a new sanction. Do not alter Personnel implementation to make this module easier.

## Generation and verification

Source: `tools/build_censor.py` and `tools/templates/censor/`. The full staged `tools/build_common_fund.py` invokes Censor generation after unchanged dev.61 fiscal upgrades, assigns dev.62 metadata and runs `tools/verify_censor.py` alongside existing checks. Calling `build_censor.py` directly redirects to that staged full build. Do not generate inside watched folders or edit generated files alone.

Runtime has 11 new files across scripted triggers/effects/values, story cycles, on_actions, modifiers, opinions, interactions, decisions, events and English localization. There are no new native overrides. All game outputs use UTF-8 BOM. Staging publishes only final changed files and preserves developer hot reload.

Verification completed: full isolated build and all nine source/check suites passed, including five new lifecycle-contract examples and four pinned native definitions. Report: [CENSOR-VERIFICATION.json](CENSOR-VERIFICATION.json). The 11 generated files contain 14 events and 221 English localization keys. All 227 pre-existing game/runtime asset files in the initial audit remain byte-for-byte unchanged; the 159 protected-file checks also pass. Existing protected/native hashes are unchanged; they must never be refreshed to excuse a Censor edit. Four inspected native definitions are pinned in `CENSOR-NATIVE-BOUNDARIES.json`; a source change requires deliberate comparison, not an automatic baseline refresh. The new verifier checks syntax structure, macro arguments, references, stage routing, localization data syntax, reviewer/sequence guards and absence of a second cash/criminal executor, plus five executable lifecycle-contract examples. Model/source checks are not CK3 execution, visual, AI, performance or save-migration acceptance.

## Dev.63 follow-up: participating skills and current evidence

User requested that statistics of all participating roles matter, and corrected the first option after an imperial refusal. The label now acknowledges the sovereign: **The Dragon Throne has spoken. I will let the matter rest.** Generic no-proof narrative now concerns misconduct, not a nonexistent appointment allegation.

| Role | Relevant skills and actual source effect |
|---|---|
| Censor | Intrigue, Stewardship, Learning oppose concealment/false attestations. Martial contributes for War/Marshal returns. Diplomacy affects imperial AI reception of the memorial. |
| Subject | Intrigue, Stewardship, Learning oppose discovery; Deceitful and meticulous concealment affect recovery. Diplomacy influences political protection. An honest record never becomes false because of a roll. |
| Chancellor / defending minister | Diplomacy affects selection as an advocate and the imperial AI's inclination to protect. Relationships, traits, actual blocs/factions remain relevant. |
| Justice / unconflicted imperial fallback | New independent-comparison choice uses that actual reviewer's Learning, Stewardship and Intrigue against the subject. It can discover an existing concealed linkage/false return, never invent a crime. |
| Connected payer | Intrigue and Diplomacy oppose Censor Intrigue/Learning when denying an uncorroborated actual linkage. Confirmed documents are not erased by a persuasive denial. |
| Emperor | Learning/Intrigue help weight evidence/framing in AI responses. Diplomacy affects practical mediation for both players and AI, with native opinion consequences. |

All four discovery chances use actual ScriptValues with a 10% floor and 90% ceiling. Preview scopes bind on presentation; checks recalculate and record the actual chance when committed. A stat change while a window is open can therefore change the later roll; recalling the stage refreshes the preview. Cooperation with an actual readable record need not roll. This system changes detection and political choices, not the truth of acts.

Original dev.62 traits continue to shape methods, responses, investigation focus, advice, support, stress and imperial confrontation. No skill forces a human emperor's choice. Physical prowess is not used to decide documentary truth.

The 2026-10-31 screenshot supplies limited engine evidence that the refusal event reaches the screen with portraits/names. Error-log review found 33,230 repeated result-variable preview errors at the same close-helper context, plus uncreated-story preview reads and two manual interaction AI-frequency warnings. The update guards the real created story and completed result state before using them, and removes the unused manual frequency declaration while retaining `ai_potential = no`. Passive diagnostic/history fields may still produce the engine's unused-variable warnings; they are retained for institutional evidence rather than deleted to silence the log.

At dev.63, secrets and plots remained separate native systems without an automatic MAM intake. Dev.64 now adds the adapter below; it preserves native exposure, rewards and criminal rules.

Verification: the full isolated dev.63 build and all nine source/check suites passed, including five lifecycle-contract examples and four actual-source arithmetic tests. New actual-source arithmetic tests cover opposed skills, independent reviewer identity, witness courtcraft, military relevance, traits and chance bounds. CK3 execution, tooltip-log clearance, presentation and AI balance for these changes still require testing.

## Dev.64 discovery bridge and crash audit

See [CENSOR-DISCOVERY.md](CENSOR-DISCOVERY.md) for the full implemented contract. Relevant actually-known secrets now create confidential referrals. Public plot discovery at the imperial court creates an unidentified warning, not a named guilty party. An opposed seven-day trace must re-find the actual live exposed scheme by this module's source identity; success names its real author. A Censor can question an identified official, send a direct supported memorial, protect an intended victim, defer or bury their report. The same inspection chain provides ministerial resistance, Justice advice, imperial protection/removal and personal consequences. Emperor independently known allegations against the current Censor route directly to emperor.

The added sovereign-owned intelligence service/lead stories share the existing story runtime file. Own variables are prefixed `mam_cen_`. The live queue is capped at eight, with one brief or inspection, 30-day deferral, two-year pending expiry and ten-year closed snapshots. Matching early leads can join an inspection and invalidate its old findings token. Native Secret/Scheme pointers are not retained in leads. Supported known facts are not relabelled as paid appointments. No source deletes knowledge, exposes secrets, creates criminal reasons, duplicates discovery rewards or edits accepted Personnel/Revenue modules.

`tools/templates/censor/intelligence.txt` supplies additive runtime sources; `tools/build_censor_intelligence.py` supplies guarded presentation through the existing staged generator. New event 101; old IDs and the 11-file footprint remain. The source verifier checks the knowledge filter, exact supported types, no unknown-author name/portrait leak, current-investigator/live-scheme tracing, matching-case attachment, imperial recusal, queue/modal bounds and source-to-runtime consistency. Actual tracing ScriptValue arithmetic receives a fifth skill-evaluator test. Full staged checks are required before publication; engine acceptance remains unchecked.

The latest observation crash is a separate unresolved native access violation. Bundle and final logs were preserved/read; timing coincides with the previous build's publication, but no symbolized stack proves a cause. Its attached save predates the observation's Censor work. [CRASH-2026-10-31.md](CRASH-2026-10-31.md) records evidence and next reproduction checks. Developer hot reload is preserved, not disabled.

Final dev.64 verification: full isolated build and all nine suites passed. Censor checks cover 11 runtime files, 15 events, 95 definitions, 266 English localization keys and 15 pinned native definitions. Five lifecycle-contract tests and five actual-source skill arithmetic tests passed, plus discovery source/privacy/duplicate contracts. The 159 protected-file checks and all existing fiscal, project, scheduler and jurisdiction checks passed. Publication replaced only final changed files; unchanged files were not rewritten. **No dev.64 engine execution, visual, save-migration, crash-clearance or AI-balance acceptance is claimed.**

## Dev.65 public criminal matters

See [CENSOR-PUBLIC-ACCUSATIONS.md](CENSOR-PUBLIC-ACCUSATIONS.md). Public native criminal standing plus actual legal grounds, formal filing by a native-reason holder, and eligible senior detention now feed the same inspection chain. Automatic targets are kingdom/territorial empire governors and central ministers. The source authority is named, the accused can answer from custody, and ministerial defense/Justice advice/imperial intervention remain available. One public matter and one independent discovery can coexist without treating the accusation as proof.

Separate current-ground checks can support an explicitly administrative fitness censure or guarded removal, not a criminal conviction. The grounds are revalidated at commitment. Missing/consumed grounds do not prove innocence or abusive detention. Public-status-only censure grants no discovery reward and is not repeated while the existing censure modifier remains. Retirement justification is captured before a native handoff, with unsupported-removal Tyranny only after confirmed departure. No prisoner is released or retired by this adapter.

Source `tools/templates/censor/public_crime.txt` is appended by the staged generator; no extra runtime file or event ID. Durable episode markers, queue bounds and old-token guards remain. Four native boundaries were deliberately appended, retaining the previous 15 hashes. Three new source-predicate tests check accusation/proof separation and loss/unverified legal grounds; they do not simulate the engine. Staged results are recorded after verification; all new engine acceptance remains pending.

Final dev.65 verification: the complete isolated build and all nine check suites passed. Censor runtime: 11 files, 15 events, 110 definitions, 293 English keys and 19 pinned native definitions. All 13 Censor tests passed (five lifecycle contracts, five actual-source skill tests, three public-ground source-predicate tests). The 159 protected-file checks and existing fiscal/project/scheduler/jurisdiction suites passed. Final-only publication preserved hot reload and did not rewrite unchanged files. **Engine execution, event layout, actual crime/custody callback timing, migration, observer balance and crash clearance remain untested.**
