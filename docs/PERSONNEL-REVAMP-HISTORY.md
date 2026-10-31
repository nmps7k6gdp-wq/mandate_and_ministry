# Ministry of Personnel revamp

Historical implementation record. Personnel was officially completed and accepted on 2026-10-27 at dev.41. See [the current Personnel tracker](PERSONNEL-REVAMP.md) for the accepted baseline.

## Historical status

Personnel redesign: advancement, senior death/promotion vacancy custody, candidate refresh, notification queue and standing directions implemented. In-game validation and broader native reassignment coverage remain pending. Censor–Justice runtime: disabled pending a separate simplified revamp. Existing Personnel gameplay remains active.

Update this document after each implementation batch: record changes, verification, limitations, and the next task. Never mark gameplay verified from static checks alone.

## Agreed scope

- Personnel selects candidates for eligible kingdom- and empire-tier public offices. Imperial throne succession is excluded.
- County and duchy appointments retain vanilla order and generate no Personnel vacancy events.
- Unlanded eligible candidates remain recruitable. Future investigations concern public officeholders, including titular ministers.
- Vacancy influence belongs to the office regardless of council assignment.
- Manage Talent enables performance review and advancement endorsements.
- Bestow Royal Favor remains a Personnel task and adds favor-based candidate score.
- Advancement improves prospects for a future vacancy; it does not evict an incumbent or require a manual chain of replacements.
- Marked candidates appear as additional eligible shortlist options, without bypassing eligibility.
- Chancellor oversight influences Personnel through policy, instructions, relationships, and exceptional review. Routine work should not require repeated approvals.

## Intended player experience

### Senior vacancy

Receive one appointment event showing the native default, professional alternatives, political alternatives, and an eligible marked candidate. Explain qualifications and relationships. Select a candidate once; routine appointments proceed under the lawful mandate. Revalidate eligibility before granting office.

Temporary title custody by the emperor is a proposed mechanism, not a proven implementation. Test succession timing, rank rules, liege and vassal preservation, incumbent death, office turnover, timeout, and save/reload. Never silently replace an already installed vanilla successor. Personnel should not personally absorb provincial land as a temporary custodian.

### Manage Talent

Review official → endorse advancement, continue observation, or record poor performance. Endorsement supplies a bounded, temporary appointment-score bonus for eligible higher senior offices. No immediate forced transfer. Score amount, duration, and negative-assessment consequences remain to be balanced.

### Bestow Royal Favor

Personnel administers favor to the selected official. Preserve the existing task benefits and add a bounded appointment-score bonus with a distinct reason. Favor does not manufacture examination credentials or waive qualifications. Chancellor direction influences policy; the Chancellor does not perform this Personnel task.

### Personality and player consequences

| Trait | Intended preference |
|---|---|
| Just | Lawful order and qualifications; resists unfair favoritism |
| Honest | Rejects payments and dishonest assessments |
| Diligent | Performance and relevant competence |
| Lazy / Impatient | Default candidate and less investigation |
| Ambitious | House, allies, and political following |
| Family Hierarch | Eligible family members |
| Vengeful / Forgiving | Stronger / weaker retaliation against rivals |
| Gregarious | Friends and personal connections |
| Paranoid / Trusting | Trusted connections / greater acceptance of endorsements |
| Greedy | Receptive to paid patronage |
| Arbitrary | Greater personal discretion over rankings |
| Loyal | Sovereign's stated priorities |
| Compassionate / Callous | More / less tolerance of struggling officials |

Combine preferences rather than assigning deterministic choices. Use real faction membership separately from the mod's political-client relationship. Do not infer hostility to an entire family without a defined relationship.

Players retain choice. Display contextual stress before committing an out-of-character act; apply it once. Appointing a qualified relative is not automatically corrupt. Do not charge stress for browsing or cancelling.

### Paid patronage

Current implementation records a 100-gold payment, minister, payer, date, and obligation lasting up to three years or one successful sponsored appointment. The current +12 is private mod recommendation preference, not native appointment score. Some records retain only the latest transaction/request.

Revamp target: durable transaction records, nomination linkage, expiry, and exposure evidence. Keep bribery preference private. While Censor–Justice is disabled, Personnel payment bookkeeping continues but judicial case creation does not.

## Decision and interaction policy

Use `Personnel: <Verb> <Object>` for Personnel decisions. Use consistent terminology across titles, descriptions, tooltips, confirmations, and related events. Keep internal IDs stable where possible.

- Show actions only to their responsible officeholder. Law-setting belongs to the emperor.
- Use visibility for role ownership and relevance; show temporary blockers with clear explanations.
- Recheck authority on execution and after office turnover.
- Use character interactions for actions about one person and events for vacancies. Avoid a global decision for each workflow step.
- Keep only necessary global entry points. No mandatory register navigation.
- Keep AI-only scheduling out of the player's decision list.
- QA actions belong in debug mode and remain inaccessible while their feature is disabled.

| Existing decision | Owner | Disposition |
|---|---|---|
| Review Talent Register | Personnel | Retain temporarily; optional reference in final design |
| Review Ministry Laws | Emperor | Retain; emperor-only visibility |
| Start / Pause Service Records | Personnel | Retain until task-based observation replaces toggles |
| Enable / Suspend Routine Reviews | Emperor | Retain temporarily; retire old automatic replacement workflow when replacement is ready |
| Clear Marked Candidate | Personnel | Retain; later place beside candidate selection if convenient |
| AI review / policy / bribe decisions | Eligible AI actors | Keep hidden from human players; adapt during implementation |
| Judicial policy, cases, archive, conduct, Chancellery judicial mandate | Relevant judicial actors | Disabled with Censor–Justice runtime |
| QA 204–211 controls | Debug testers | Debug-only and disabled with judicial runtime |

Do not remove functioning Personnel entry points before their replacements exist. New decision additions must justify why an event or character interaction is insufficient.

## Censor–Justice suspension

User requested temporary disablement, not deletion. Preserve scripts and case records for later simplification. Hide decisions, inquiry interaction, register access, and judicial events; stop new cases and normal case/oversight progression. Preserve already imposed outcomes and essential custody-release cleanup. Vanilla council assignments are not removed.

The scope-independent switch is `mam_cj_runtime_enabled_trigger` in `common/scripted_triggers/mam_cj_runtime_triggers.txt`. It currently returns `always = no`. Re-enabling requires an explicit migration review: saved absolute deadlines keep advancing while progression is suspended.

Future simplified judicial design is deferred. Its basic responsibility chain is report → investigation → defense → judgment → authorization → enforcement. Do not expand evidence menus or procedural subsystems during Personnel work.

## Implementation tracker

- [x] Inventory current Personnel decisions and authority checks.
- [x] Hide ten QA decisions outside debug mode.
- [x] Restrict Personnel law decision to emperor; standardize Personnel decision names.
- [x] Add temporary Censor–Justice runtime suspension and preserve release cleanup.
- [ ] Verify decision visibility and judicial suspension in a running game.
- [ ] Prototype senior vacancy interception and emperor custody on a disposable save.
- [x] Implement eligibility, native default, marked candidate, and concise shortlist (scripted; awaiting playtest).
- [x] Replace forced performance transfers with appointment-score endorsements (scripted; awaiting playtest).
- [x] Connect reviews to Manage Talent and favor bonuses to Bestow Royal Favor (scripted; awaiting playtest).
- [ ] Implement expanded personality preferences and contextual player stress.
- [x] Add durable patronage history and nomination linkage (scripted; awaiting playtest).
- [x] Integrate bounded Chancellor oversight through standing priorities and binding imperial orders (scripted; awaiting playtest).
- [ ] Retire superseded Personnel decisions, events, and replacement workflows.
- [ ] Verify AI, succession, timeout, office turnover, and save/reload behavior.

## Validation and change log

2026-10-27: Created this specification. Applied initial decision cleanup and runtime suspension. Static verification is tracked in the accompanying chat; in-game behavior is not yet certified. Core Personnel redesign remains unimplemented.

Next task: reload scripts/game and verify suspension, then prototype one senior vacancy before building the full appointment system.

### Personnel implementation batch 1

- Added Personnel: Review Official, available to Personnel during Manage Talent.
- Earned three-year endorsement adds +20 native score for eligible higher senior civilian offices; mature improving service and no current concern required. AI commendations use the same criteria.
- Bestow Royal Favor adds a refreshed 90-day +10 senior civilian appointment-score bonus.
- Score bridge excludes county/duchy appointments, the imperial primary title, and foreign sponsorship. Native scoring body is preserved from installed game scripts and must be reviewed after updates.
- Expanded trait preferences for family, friends, rivals, political clients, endorsements and paid obligations. Added Honest/Just stress for accepted bribes.
- Disabled legacy manual/AI forced-replacement routes and obsolete automation decisions.
- Static source structure and top-level-definition checks passed. In-game behavior is unverified.
- Pending: vacancy event and custody prototype, marked shortlist integration, remaining personality behavior, stress previews, durable patronage history, Chancellor integration, and migration of pending proposals. Do not treat the revamp as finished.

### Personnel implementation batch 2

Implemented 2026-10-27; static checks only. In-game testing deferred at the user's request.

- Added an additive pre-death callback using the installed native on_death contract (character is about to die, before succession).
- For a clean, directly governed senior civilian jurisdiction with a valid Personnel minister and eligible candidates, record the default, professional, minister-preferred and marked candidates. Keep county/duchy deaths and the imperial throne outside this callback.
- Create a durable appointment story, then move that jurisdiction to temporary imperial custody. Persist the acquired component-title list so the final grant cannot collect unrelated pre-existing imperial land.
- Personnel receives one event with named candidate tooltips, live authority checks, recruitment checks and refreshed candidate availability. Minister personality and Chancellor priorities weight AI choices.
- Promotion attempts automatically supply the old posting's native successor, subject to native validity and an unlanded replacement. No manual replacement menus.
- After 90 days, try the stored default, professional and preferred candidates. If none can currently serve, retain custody, log the issue, reset the review period and allow a new notification. Do not grant to an invalid candidate.
- Added contextual Just/Honest stress for personal choices materially below the professional shortlist; no automatic stress for the default or a qualified relative. Added accepted-bribe stress preview.
- Added a passive story ledger for each accepted payment and linked successful senior appointments where the obligation concerns the selecting minister. No Censor?Justice cases are created while disabled.
- Added Personnel: Direct Ministry Priorities, a character interaction for the emperor/Chancellor with Personnel. Professional administration, continuity and discretion influence AI appointment options without new global decisions.
- Static structure, top-level duplicate definitions, custom effect/trigger references and new appointment localization BOM checks passed across 183 script files.

#### Known coverage limits before playtesting

- Initial interception covers deaths, not every native reassignment/resignation route. Old-office succession during a promotion currently uses the native successor, including a senior source office; extending Personnel choice to that route remains pending.
- Ambiguous or indirect jurisdictions, military offices, central titular ministries and offices without eligible candidates remain on vanilla succession. Supporting more office categories requires dedicated handling.
- Lists are captured before custody. If every stored candidate becomes unavailable, the file remains pending rather than inventing a replacement. A refresh-candidates action remains to be implemented.
- The prototype does not yet implement event batching, a global one-popup queue, full house-faction membership preference, complete trait coverage, emperor-reserved appointment laws, or an enforceable hierarchy between emperor and Chancellor directions.
- Existing legacy pending proposals have not yet been migrated. Do not mix an old pending forced-transfer proposal with a custody test.
- Native succession timing, candidate merit checks under imperial custody, title/liege/vassal transfer behavior, death/office turnover and save/reload must be tested together. No engine-level pass is claimed.

#### Joint test order

1. Confirm Personnel alone sees nomination/marking actions and that review requires Manage Talent.
2. Compare native county/duchy succession before and after the mod changes: unchanged.
3. Trigger one clean kingdom governor death; verify temporary emperor custody, exact acquired titles, original lower vassals and the candidate event.
4. Choose an unlanded eligible candidate; inspect government, liege, vassals and titles.
5. Repeat with a serving candidate and a valid native source replacement.
6. Test the marked candidate, expired/invalid candidates, Personnel replacement, emperor succession, 90-day fallback and save/reload.
7. Compare AI selections under traits and priorities; check contextual stress, endorsement/favor score and the private payment ledger.
8. Check fresh error/debug logs before extending coverage or balancing numbers.

### Personnel implementation batch 3 ? dev.21

In-game testing remains deferred by user instruction. Static checks passed across all script files; no engine-level verification is claimed.

- Added a shared, expiring realm queue lease bound to the current Personnel minister. Capture and monthly story callbacks use the queue instead of independently scheduling each appointment. Office turnover or stale custody releases invalid leases.
- Added Personnel: Resume Senior Appointments, visible only to the responsible player minister with pending work. Deferring a file snoozes it for 30 days; the resume action brings pending work back for review.
- Added candidate-pool refresh during event preparation, explicit Refresh action and timeout processing. This incorporates newly eligible and newly marked candidates. Native qualification checks are adapted specifically for an existing file's temporary imperial custody; the native holder-primary-tier equality cannot be used unchanged under custody.
- Event choices now retain their displayed character snapshot instead of silently selecting a different person if a later pool refresh changes the story's shortlist.
- Promotions made through this workflow route a clean senior source governorship into its own custody/Personnel file. County and duchy source replacements continue through native successor selection. Outside native reassignment/resignation routes are still not intercepted.
- Service records now follow Manage Talent. Retired the manual Start/Pause decisions. Task cancellation marks an observation gap; resumption invalidates baselines so unobserved time is not credited. Maintenance uses verified task callbacks and the existing yearly pulse, not an assumed monthly engine hook.
- Explicit imperial professional/continuity orders bind the Chancellor; imperial discretion delegates standing direction back to the Chancellor. The interaction is hidden when the actor lacks authority.
- The emperor's remaining Personnel law decision opens recruitment standards directly, removing the obsolete duchy-jurisdiction/manual-transfer mandate hub from normal navigation.
- Added one-time migration invalidating legacy forced-transfer proposal locks during maintenance/startup. Old completed appointment records are retained.

#### Current remaining work

- Engine verification of custody, native qualification under custody, source-office transfers, queue save/reload and task cancellation scope.
- Broader native reassignment/resignation interception, indirect/ambiguous jurisdictions and central titular office support.
- Full personality coverage, real shared-faction/house-bloc preferences, and more informative comparison/stress presentation.
- An actual imperial law for reserving particular appointments, beyond the current standing-priority interaction.
- In-game checks that no old forced-transfer route remains reachable and that all retired descriptions are replaced consistently.

Supersession note: batch 3 replaces batch 2's fixed-list, no-queue and native-senior-source-succession limitations for the flows described above. Earlier log entries remain as implementation history.
