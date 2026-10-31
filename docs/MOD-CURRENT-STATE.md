# Mandate and Ministry: current gameplay and technical state

**Maintained entry point — 2026-10-31, build `0.4.0-alpha.20-dev.66`.**

Read this before modifying the mod. `descriptor.mod` is the build identifier. This document describes the current source, not a claim that every path has passed an engine playtest. Update it when behavior, dependencies, saved data or verification changes. Older documents retain their original build labels; where they differ, use this current-state guide and the actual source, then investigate the discrepancy.

The mod targets CK3 `1.20.*`. Reference inputs are the locally installed game under `C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game`. Those files and installed Workshop mods are read-only. Native ministry, celestial government and great-project APIs are required; do not invent substitutes for unavailable APIs on other builds.

## 1. Scope and accepted boundaries

| Subsystem | Current state | Change constraint |
|---|---|---|
| Personnel | Revamp accepted at dev.41; subsequent jurisdiction maintenance retained | Preserve the accepted gameplay and its saves during Revenue work |
| Central ministry succession | Native inheritance followed by Chancellor/Emperor approval | Separate from provincial Personnel custody |
| Examination honors | Integrated badges, traits, capped career rewards and sponsorship | Keep vanilla examination eligibility; do not require the standalone Workshop mod |
| Revenue/common fund | Implemented in source, with ongoing in-game bug testing | Use actual native Treasury; retain payroll, claims and payment verification |
| Project contributions | Dev.55 shared project budgets and native invoice executor | New engine acceptance tests are pending |
| Grand Campaign launch finance | Dev.55 explicit imperial approval, Marshal pledge and separate mobilization provision | Funding the pledge can start war; do not treat it as ordinary delegated expenditure |
| Custom Censor–Justice loop | Removed at dev.42 | No investigation, trial, register or automatic prosecution may be reintroduced incidentally |
| New Censorate | Dev.62 independent official inspections, personality-driven responses, ministerial intervention and imperial confrontation | Separate from removed cases; preserve native espionage/Justice and accepted Personnel/Revenue |
| New Justice | Dev.66 senior judicial hearings, native powers, imperial authority, consent, mercy, attributable abuse and Censor referrals | New user-authorized module; exact native costs/effects, prospective explicit warrants, no old register/trial restoration |
| Other ministries | Native gameplay plus shared funding and central succession review | Receiving funds does not imply a complete custom departmental revamp |

The protected-file checks cover 159 pre-existing gameplay/assets outside Revenue. Do not regenerate their baseline hashes to excuse an unrelated edit. Shared functions with historical `mam_cj_` names may be required by Personnel; a historical prefix is not permission to delete them.

**Censor direction authorized for implementation on 2026-10-30:** the user requested dynamic struggles, abusive or just investigators, ministerial resistance, consequences and active AI. [CENSOR-IMPLEMENTATION.md](CENSOR-IMPLEMENTATION.md) is the dev.62 source/runtime contract and status; [CENSOR-TESTING.md](CENSOR-TESTING.md) lists engine checks. The historical proposal is design context, not proof of unimplemented powers such as universal freezes or a new criminal trial. The removed dev.42 register/trial remains removed.

## New Justice: dev.66

The user explicitly approved implementation on 2026-10-31. [JUSTICE-IMPLEMENTATION.md](JUSTICE-IMPLEMENTATION.md) records gameplay, native limitations, state/API contracts and save adoption; [JUSTICE-TESTING.md](JUSTICE-TESTING.md) is the pending engine checklist. `tools/build_justice.py`, `tools/build_justice_events.py` and `tools/templates/justice/` generate the module through the full staged common-fund builder. The tenth suite, `tools/verify_justice.py`, checks actual predicates, native cost/acceptance parity and lifecycle guards; its generated report explicitly does not claim engine/visual/AI acceptance.

`h_china` indexes a bounded institutional queue and one actionable reviewer desk. Actual senior native grounds/detention and explicit Censor referrals initiate hearings. Justice, accused, connected ministers, Chancellor, Emperor and actual custodians/right-holders have distinct decisions. Native Justice tasks and schemes remain; broad senior measures are gated by a two-level Judicial Authority realm law. Native bodies/costs are pinned and compiled, with actual permissions, acceptance, funding and consent rechecked before one execution. The old `mam_cj_*` system remains removed; Personnel and fiscal runtime contracts are not rewritten.

A native pardon clears the affected authority's four current criminal-right categories, rather than an individual charge. Tooltips identify that authority; a changed authority/category invalidates reserved approval. Selective custom clemency only removes this module's own identifiable warrant. Corroborated actual post-adoption misconduct can support an explicit imperial warrant granting an imprisonment reason only. Passive receipts, suspicion, detention and legitimate native pardons/hooks are not automatic crimes. Source identities prevent recycling a spent warrant. Actual judicial solicitation/bypass can feed Censor scrutiny and personal imperial rebuke; a successor inherits work without inheriting guilt or private promises.

No dev.66 engine/visual/observation acceptance is claimed. Restart a backed-up test session for new classes and use the checklist before declaring the module stable. Previously unresolved native crashes remain unresolved absent crash evidence; this implementation is not a claimed crash fix.

Final dev.66 staged verification passed all ten suites: 21 Justice text/localization files, 12 events, 165 parsed definitions, 166 English keys, 14 pinned native definitions and 23 Justice contracts. The 13 Censor tests, all 159 protected files and fiscal/project/scheduler/jurisdiction checks passed. Publication replaced only changed final files and preserved developer hot reload. These are source/contract results, not engine acceptance.

## New Censorate: dev.63 (introduced dev.62)

The new `mam_censor.*` / `mam_cen_*` module runs one major official inspection indexed on `h_china`, with its facts, office/date, personal authors, reviewer lease, replies, defenses, advice and disposition stored in `mam_censor_inspection_story`. It is newly authorized gameplay, not a restoration of the removed `mam_cj_*` trial/register. Native secret revelation, agents, rewards and blackmail remain. The separately authorized dev.66 Justice module adds narrow senior-authority/observation gates to Find Criminal event 8071 and four native interactions, retaining their original acceptance effects and costs; see its native compiler contract above.

A player Censor can select a senior target through **Censor: Begin an Inspection**, or an eligible county-through-empire official through **Censor: Inspect Public Conduct** in Ministry. Emperor can request scrutiny through the same interaction. AI Censors initiate through startup/quarterly sovereign callbacks; weekly story workers advance decisions. Actual traits, rivals, friends, houses, house blocs and shared targeting factions affect target/defender selection and choices. Most stages wait 7–28 days, with a 180-day automatic rest after closure and two-year per-subject selection cooldown.

Ordinary paths can end in a clean closure, correction or supported censure. Other paths include a false return made during the inspection and possibly detected by comparison, concealment of an actual paid-appointment linkage, a minister's defense/call for safeguards, coercive methods, a private favor-for-silence proposal, Justice advisory disagreement, impeachment, imperial protection, one renewed memorial and a resignation/removal confrontation. Procedural delay or a lawful objection is not automatic obstruction. No random past embezzlement is generated from a valid receipt, empty accounts or technical errors.

A supported censure applies -50 Influence, a nonstacking two-year political-standing modifier, resentment and potentially a native rivalry. A measured supported disposition can earn a nonstacking three-year Trusted Inspector modifier; this does not duplicate native secret-scheme currency rewards. Harsh actions record their actual personal author and create Dread plus a three-year Feared Censor modifier with an opinion cost. Emperor can discredit/restrain the recorded abuser. A successor inherits institutional work, not a predecessor's threats, promises or fabricated accusation.

Removal is an explicit imperial choice. Safe central ministries use the existing protected native heir handoff. Supported senior governors use the accepted `mam_senior_capture_effect` so Personnel retains custody, candidate selection and jurisdiction; lower governors use native retirement. Eligibility is conservative, including current inspected office, no war and a family-title safety requirement. A verified departure applies the native three-year appointment timeout. Failed handoff is not reported as success and does not receive an appointment timeout. No arbitrary title grants, new treasury execution, candidate-score edits, criminal secrets or imprisonment reasons are added. Governor/minister removal and all new engine behavior remain acceptance tests.

The module reads existing patronage and contribution records without modifying them. Its own acts (false returns, obstruction, coercion, private settlements, censure and disposition) are distinct future integration records, not a new Justice prosecution API. Every case closes without requiring an unbuilt Justice module. Institutions and future module contracts are detailed in the implementation document.

The final isolated dev.62 build passed all nine source/check suites, including the new Censor verifier and five lifecycle-contract examples. All pre-existing runtime/asset hashes in the initial audit and the 159 protected-file checks remain unchanged. [CENSOR-VERIFICATION.json](CENSOR-VERIFICATION.json) records the generated files and native boundaries. No engine, visual, observer-balance or migration acceptance is claimed.

### Dev.63: skills, wording and tooltip follow-up

Traits already weighted the inspection's choices and stress; dev.63 extends the narrow old Intrigue comparisons. Hidden payment recovery now opposes Censor and subject Intrigue, Stewardship and Learning; false-return comparison uses the same relevant skills and Martial for War/Marshal returns. Justice can perform one independent check with the actual reviewer's Learning/Stewardship/Intrigue. A connected payer's Intrigue/Diplomacy opposes the inspector when denying an uncorroborated linkage. Chances are bounded at 10–90%, previewed in relevant tooltips and recomputed at commitment; they only uncover conduct that actually exists. Already admitted proof is not erased.

Defenders' Diplomacy affects selection and imperial AI response; Censor/memorial-author Diplomacy, subject Diplomacy and emperor Learning/Intrigue affect political weights. A human or AI emperor's Diplomacy also affects mediation: at least 15 gives +10 Opinion from each living party for three years, below 8 leaves -15 Opinion with the living memorial author. Players retain their policy choices.

The refusal response now reads `The Dragon Throne has spoken. I will let the matter rest.` Generic inquiries no longer claim that no paid appointment was found; that wording is limited to an actual uncorroborated appointment linkage. A 2026-10-31 user screenshot confirms the dev.62 refusal event rendered with names/portraits, but not skill probabilities or balanced AI.

The same session's log contained repeated result-variable reads during tooltip building and an uncreated-story preview. Dev.63 guards post-creation and post-result state before traversal, and removes unsupported zero-frequency/no-target declarations from the two manual interactions. These are source fixes for observed log contexts; a fresh engine log is needed to confirm clearance.

At dev.63, native Minister: Find Secrets and scheme discovery remained separate. Dev.64 adds the bounded discovery adapter below without a duplicate search scheme or automatic criminal case.

Dev.63 passed the full isolated build, all nine source/check suites, five lifecycle-contract examples and four actual-source skill tests. [CENSOR-IMPLEMENTATION.md](CENSOR-IMPLEMENTATION.md) records the final result; new gameplay/AI acceptance remains pending.

### Dev.64: useful discoveries and unresolved crash audit

[CENSOR-DISCOVERY.md](CENSOR-DISCOVERY.md) defines the implemented adapter: weekly intake of relevant native secrets actually known to Censor; additive imperial-court plot warnings; a one-attempt opposed-skill trace that must re-find the real live scheme before naming its author; confidential questioning or direct imperial memorial; and six-month targeted protection. Supported discoveries feed the existing struggle, ministerial defense, Justice advice and imperial disposition. One matching discovery can join a pre-imperial inspection and invalidate its old review token. Other leads wait in a bounded eight-entry institutional queue. No automatic native exposure, crime, arrest, rewards or treasury/Personnel edits.

The emperor separately reviews an independently known supported secret against Censor. Unknown-owner plots do not leak their author through portraits or names. See the discovery document for supported types, knowledge boundaries, two-year expiry, succession, callback capacity and polling limitations. Source authors remain the Censor templates/generators; runtime file count remains 11, with new event 101 and no renumbered events.

The observation crash is preserved and audited in [CRASH-2026-10-31.md](CRASH-2026-10-31.md). It is an unsymbolized `ck3.exe` read access violation, occurring within a second of dev.63 publication. Cause is unproven; the bundle's save is an old starting `test4`, not the terminal observation state. No claim of a confirmed crash fix, and no developer hot reload/process changes.

Dev.64 passed the full isolated build and all nine source/check suites: 11 Censor runtime files, 15 events, 95 definitions, 266 English keys, 15 preserved native boundary definitions, five lifecycle-contract tests and five actual-source skill tests. Discovery privacy, live tracing, matching-case, duplicate and review-token contracts passed; the 159 protected-file checks and fiscal/project/scheduler/jurisdiction suites passed. Detailed results are in the Censor tracker/report. All new engine, visual, migration, crash-clearance and observer-balance checks remain pending in [CENSOR-TESTING.md](CENSOR-TESTING.md).

### Dev.65: senior criminal accusations and custody

[CENSOR-PUBLIC-ACCUSATIONS.md](CENSOR-PUBLIC-ACCUSATIONS.md) specifies the new public adapter. Serving kingdom/territorial empire governors and central ministers can reach Censor through public criminal standing with real native grounds, an actual legal-reason holder's formal Ministry referral, or eligible detention in the imperial realm. Additive native trait/prison callbacks and weekly recovery preserve native behavior. Senior public matters are prioritized within the existing bounded queue; lower/unlanded characters do not create mass automatic referrals.

An accusation or detention is **not** a supported misconduct fact. A separate legal-ground review by Censor, Justice or emperor can justify an explicitly administrative fitness recommendation only while positive native grounds remain current. Original-crime truth, native conviction, pardon, arrest and release remain separate. Prisoners can answer the hearing letter without gaining freedom; their retirement remains blocked. A guarded removal captures its justification before the native handoff to avoid spurious post-retirement Tyranny. Public matters and independent discoveries occupy separate slots in the same inspection.

Institutional stories retain actual authority, office/date, charge, reviewer and disposition. Durable public-episode markers prevent repeated intake after archiving; withdrawal of grounds/end of custody permits a later episode after prior work closes. The maintained tracker/checklist records staged source verification and pending engine acceptance. Existing Personnel, fiscal execution, native criminal rights and the removed trial/register boundaries are preserved.

Dev.65 passed the full staged build and all nine suites: 11 Censor files, 15 events, 110 definitions, 293 English keys, 19 preserved native definitions and 13 Censor tests. All 159 protected files and fiscal/project/scheduler/jurisdiction checks passed. No new engine, visual, actual native callback, migration, balance or crash-clearance acceptance is claimed.

## 2. Personnel gameplay to preserve

Personnel controls **kingdom and territorial empire civilian offices**, including supported kingdoms nested beneath a civilian territorial empire governor. County and duchy succession remains native. Military jurisdictions, the imperial throne, central ministries and ambiguous multi-jurisdiction bundles are excluded from provincial custody. Eligible unlanded candidates remain recruitable.

Supported vacancies enter independent FIFO custody files on the realm title. The throne temporarily holds the recorded jurisdiction. Personnel receives one file at a time; simultaneous vacancies must remain separate. Candidate choices distinguish native order, lateral transfer, promotion, first office, personal preference and a qualified marked person. Marks do not waive qualifications. An open option must keep the character it displayed.

The handoff preserves the exact recorded acquired component titles and direct vassals; it must not donate unrelated imperial holdings. Parent/jurisdiction helpers handle a supported nested kingdom's proper territorial empire liege. A serving candidate's old posting uses native succession or a separate supported senior custody file; never overwrite the destination file with the source vacancy.

Appointment authority is its own realm-law group: delegate senior appointments; reserve empire nominations; confirm all senior appointments. A reserved nomination enters a separate imperial queue. Deferring snoozes for 30 days. At 90 days a refreshed fallback is considered, still subject to reservation law; an unanswered imperial recommendation is not automatic consent.

**Manage Talent** follows the native assignment, observing comparable service for three years. A favorable assessment gives a non-stacking three-year +20 higher-senior appointment endorsement. Evidenced decline without recorded war disruption can give -10 and remove the endorsement. Observation gaps invalidate comparison baselines. Reviews do not evict current governors or force a promotion chain.

**Bestow Royal Favor** retains native task effects and adds a refreshed 90-day +10 senior appointment score for an eligible target in the sponsoring realm. It is not a service-performance finding. Lower-tier native order stays unchanged.

Personality weights professional choices, continuity, family/friends, actual faction/house-bloc connections, clients, rivals and patronage. Eligibility is still mandatory. Stress is applied after the relevant successful action, with contextual tooltip previews: e.g. Just/Honest each receive 15 base Stress for a materially weaker personal appointment; Vengeful receives 15 for appointing a personal rival; Honest/Just each receive 25 for taking a bribe. Native stress modifiers can alter final values.

Personnel private patronage has durable passive payer/minister/payment/date records and bounded obligations. It is distinct from public appointment score and from Revenue receipts. Do not revive the removed court-case pipeline when recording misconduct.

Detailed contracts: [PERSONNEL-REVAMP.md](PERSONNEL-REVAMP.md), [PERSONNEL-JURISDICTION-FIX.md](PERSONNEL-JURISDICTION-FIX.md), [PERSONNEL-AI-AND-TASK-AUDIT.md](PERSONNEL-AI-AND-TASK-AUDIT.md).

## 3. Central ministerial succession and honors

For a minister's death, native inheritance installs the successor first. **Chancellor reviews the six lower departments:** Personnel, War, Rites, Works, Revenue, Justice. **Emperor reviews the three upper offices:** Chancellor, Censor, Grand Marshal. The successor remains in office while review is pending.

The event confirms that successor or offers qualified professional, personal and marked alternatives. Emperor and Chancellor have independent central-ministry endorsements, separate from Personnel's provincial mark. Replacement uses native council/title handoff and must verify both office and seat before applying success consequences. Native manual hiring/dismissal is not a provincial vacancy event. See [MINISTERIAL-SUCCESSION-REVAMP.md](MINISTERIAL-SUCCESSION-REVAMP.md).

Examination honors use native completion callbacks. Provincial/metropolitan firsts and palace placements affect MAM assessment by the highest distinction, without summing all levels. Palace top three, champion and threefold laureate have badges and a dynamic permanent fame trait. A dedicated Merit-tooltip honors row shows unearned badges dimmed and earned badges stamped. Career Merit/Prestige payments have separate lifetime ledgers; repeats pay no new distinction currency. Loading a save or viewing credentials must not award money or fabricate an imperial audience. Genuine new higher honors can create recognition/sponsorship. The user retained vanilla lowborn eligibility. See [EXAM-DISTINCTIONS.md](EXAM-DISTINCTIONS.md) for reward ceilings and original artwork attribution.

## 4. Revenue: what the common fund actually is

The common fund is **Revenue's native, title-linked public treasury**, not a new currency or a tenth treasury title. Other ministries retain small native public operating accounts. The nine pooled offices are Chancellor, Censor, Grand Marshal, Personnel, War, Rites, Works, Revenue and Justice. An office must have a qualified current holder synchronized with its native council seat. Vacant/unsynchronized accounts are not silently merged with the Emperor's account.

There are four distinct resources/account boundaries:

| Account | Use |
|---|---|
| Imperial Treasury | Emperor's own funds and explicitly approved common-fund top-ups |
| Revenue Treasury/common fund | Custody of pooled ministerial cash and authorized public payments |
| Department native Treasury | Operating buffer, paid starting/project advances and time-limited special provision |
| Governor Treasury / personal Gold | Provincial funds remain provincial; personal Gold is separate from all public accounts |

Native overall salary/ministry/military percentage budgets still distribute real income. Supported individual minister-budget contracts normalize to Medium; Grand Marshal's distinct military contract/income is preserved. The mod pools actual departmental surplus; it does not copy budget income or charge the Emperor twice.

On first adoption, a **35-day transition** lets native accounts settle. Opening and settled recurring expense observations establish provision. Existing adopted saves do not repeat adoption. Startup and delayed title-gain callbacks maintain the system. Dev.59 uses the self-scheduled weekly sovereign lease to perform due reconciliation, with the documented native quarterly pulse as a recovery entry. There is no assumed native monthly character callback.

**Monthly:** reconcile actual cash, collect surplus above protected departmental needs, advance authorized operating shortfalls, preserve earmarks and record statement totals. **Weekly essential checks:** cover deficits and two months of the greater of approved/current observed recurring bills, using real common cash. Existing payroll is not blocked by an exhausted discretionary cap. Observation of a new bill is not a new project/recruitment authorization.

Here “monthly” means the existing 25-day due gate checked by the weekly worker: normally a settlement every **28 days**, with startup/title-gain/recovery calls able to settle when already due. The weekly and monthly gates each prevent duplicate execution. An overdue adopted save performs one current reconciliation on the next valid worker, without backdating transfers or replaying missed months. Missing custody or the first-adoption delay still pauses settlement; uncertain-payment holds remain enforced by the payment boundary. Realm `mam_cf_diag_reconciled` and its last date count actual completed statements, not scheduler checks.

An ordinary target is two months of service cost, approved discretionary headroom, separate special provision and protected paid project money. Campaign mobilization adds its own temporary reserve. Only discretionary advances consume quarterly headroom; the period resets after 90 days. Native court salaries and raised/unraised/reinforcing MaA costs are real bills. Native regiment slots/size limits remain separate from cash.

Revenue's own operating protection is a reservation within the common account, never a payment to itself. Census insurance and additional native debt-purge liabilities are earned claims; a shortfall waits for real cash rather than creating an alternative payment. See [COMMON-FUND-EXPENSE-AUDIT.md](COMMON-FUND-EXPENSE-AUDIT.md) for native expenses and what was retained/retired.

### Roles and authority

| Role | Current controls |
|---|---|
| Emperor | Fiscal realm law, imperial top-ups, reserved/sensitive approvals, overriding programme instructions |
| Chancellor | Spending programme and superior review where law permits; departmental appeals |
| Revenue | Propose/recommend provision and grants; hold common cash; release authorized payments; protect commitments |
| Ministers | Request operations/supplements/project starts, contribute to eligible projects, appeal material cuts once |
| Civilian governors | Petition for justified public relief/debt assistance; consent to affordable provincial remittances; native project participation |

The law group is displayed as **Revenue Fiscal Authority**. Its levels display 1–3: **Imperial Fiscal Control**, **Supervised Fiscal Administration**, **Delegated Fiscal Administration** (saved reserved/limited/expanded IDs and source indices 0–2 are unchanged). Passing costs 150 Prestige, requires peace and a five-year cooldown. Reserved measures reach the Emperor. Limited authority uses Chancellor review for eligible routine measures. Expanded authority allows bounded Revenue execution when the programme/law allows it. Self-benefiting and sensitive offices remain superior matters; Chancellor, Censor, Marshal and War are reserved roles. Grand Campaign launch is explicitly imperial under every level.

Current programmes are Balanced Administration, reserve-building and provincial recovery. They affect reserves/proposal eligibility; they are not a second budget percentage. Expanded delegated project envelopes require Balanced, no suspension, ordinary non-Revenue contributor and a cumulative ceiling at most 500. Previously superior-authorized project commitments remain institutional; lower-level permissions are rechecked when spent.

The live common-fund queue uses `mam_fund.*`, `mam_cf_*` and `mam_revenue_fund_story`. Older `mam_revenue.*`/`mam_rv_*` definitions and retired UI still exist for compatibility and reused law/eligibility helpers. Do not reconnect their retired decisions/interactions as an alternative payment system.

## 5. Project starts, contributions and campaign launch

**Dev.61 follow-up to test4:** missionary type 17 uses the same approved external-border boundary as type 1; native faith/site requirements still apply. Existing unexpired paid grants can retry without another advance. Historical expired grants are not recreated. Wall completion follows the native remove-old/set-new upgrade pattern for known Wall levels 1–3, skips an existing level 4 or higher, and preserves unrelated great buildings. No free retroactive upgrade is applied to already-completed projects.

Campaigns retain native multi-war behavior. A funded pledge with an ended war link is not an unpaid launch. The project worker records the current living Marshal and active/between-war/waiting-for-command phase; it never restarts a war, pays a second pledge or refunds the original. If a funded campaign has no active war and every county of its nonempty native target list is already imperial, it can finish through native completion. A missing/dead current Marshal blocks new native campaign contributions before payment. Narrow pinned native overrides skip titleless declaration entries, omit missing target/leader portraits and apply personal completion rewards only to living actual contributors/leaders. Cultural project personal completion rewards receive the same living-actor guard. Original native conquest, living rewards, project prices and saved identities remain checked. These dev.61 changes have source verification; engine acceptance remains pending.

**Starting a project and contributing to an existing project are distinct.** Starting grants still use the existing typed, jurisdiction-bound office slot and native project planning UI. A matching unexpired grant is required; ordinary operating money is not approval. Native cost is quoted in the actual founder's character scope before entering the title that stores the grant. Capital projects use the imperial realm/capital context; provincial grants retain their approved jurisdiction.

Dev.57 adds an explicit AI continuation. One day after a paid starting grant, and during the weekly ministerial check, a qualified AI holder rechecks the existing grant, native `can_plan_great_project`, current Treasury, native site conditions and authorized jurisdiction. It selects a valid location and calls native `plan_great_project`; it does not request another grant. The generated 17-type dispatcher uses native location bodies, geographical filter targets, the imperial capital for global/capital work, and an adjacent foreign county for exterior-border projects. Human founders retain their native planning UI. Proposals preflight sites for AI, and an AI Marshal's unsolicited proposal chooses a frontier jurisdiction. An old inland campaign grant is not silently repurposed to an unrelated border.

If a valid site or native permission is missing, funds remain protected and the AI retries in seven days. A created project requires matching grant-instance receipt and observed native charge before being reported successful. A created project with uncertain payment is held without replay. The office records `mam_cf_start_before/after/price/on`, retry and blocked state; logs distinguish waiting, success and uncertain creation. Starting a campaign project still does not authorize its war-launch pledge.

Dev.60 corrects Wall types **10–12** to imperial jurisdiction, matching their native absence of a provincial location filter and the capital-based AI planning path. New requests record `h_china` as the work target; older paid Wall grants with a provincial target use the corrected global location rule without another payment. Types with provincial/geographical/native border filters keep their existing location boundaries. Final starting-grant commitment now reuses the native type/site preflight and current character-priced quote before any cash transfer. A changed site/type/price returns the request with outcome 4 and an explanatory result, rather than paying an unusable grant. It does not waive Influence or other native engine requirements.

Dev.55 replaces the old contribution entry point with **Revenue: Contribute to an Imperial Project**, available through the minister's Decisions and the Ministry interaction on Revenue. Choose an existing project, then an eligible native contribution. Costs and names come from native definitions. The common fund finances the real contributor; it does not turn every pledge into Revenue's participation.

### A shared project budget

1. Discover an eligible unfunded native Treasury contribution without requiring a prior contribution allowance or spare departmental cash. Native non-cash eligibility remains; engine affordability is checked after advance.
2. Bind actual contributor, project, owner/founder/location, native slot and price. Current mapping covers 152 Treasury contributions across 19 overridden project definitions.
3. If the project needs money or higher authority, queue one **kind 13** budget request on that project. Quote the requesting actor's eligible required costs plus an optional cushion of two native base-contribution prices, at least the selected invoice/current remaining budget. This is not an estimate of every possible future contributor's total bill; later amendments may be necessary.
4. The lawful reviewer approves a **remaining** budget. Cash stays in Revenue custody. An amendment replaces the remaining ceiling, rather than adding the same allocation again. `spent + remaining` forms the cumulative ceiling, preventing splitting into smaller delegated requests.
5. Covered invoices receive the exact native price and execute the exact native contribution immediately. Native code charges the price and awards native credit/rewards. Revenue's own pledge reserves/spends in place.
6. Verify funded state, callback identity and actual Treasury change. Reduce the shared remaining budget once. A failed unfunded native action returns the unused advance; uncertain cash or an already-funded action without matching proof puts the account on hold and never blindly retries.

One project's remaining budget is shared by all its eligible ministries. Two projects have separate budgets and pending-request identities. Contributions do not wait behind the 90-day **new-project** gate. A still-valid paid legacy contribution allowance is consumed without another common-fund grant. Legacy initial grants/case kinds remain supported.

Required AI invoices have priority. Every seven days the sovereign driver dispatches a hidden contributor-root check to each synchronized ministry. Optional AI contributions use native willingness, capped comparison scores and a 30-day per-actor successful-optional cooldown. Required slots do not depend on the optional cooldown. Human optional contributions need a selected intent. Unsuccessful native execution retries after seven days; refused/invalid project requests delay new requests by 30 days. Reviewer events retain their normal one-case lease, defer and resume controls.

Dev.56 explicitly separates authorization shortage from execution failure. Only a valid unfunded, uncovered invoice outside an execution lock may open a budget request. A covered pending duplicate is retired during queue resolution or commit, retaining the existing authorization without paying again. An already recorded campaign mandate is not presented as a fresh launch approval; genuine uncovered costs use a financial amendment. Failed native receipt verification keeps its account hold and records project-specific attempt actor/key/price/before/after/date for diagnosis.

Dev.58 makes pending approval quiet. A scheduled worker explicitly sets `mam_cf_manual_invoice_action = 0`; contribution choices/manual inspection set it to 1. Only the gated status helper may open `mam_fund.34`. Background work skips a project with a pending request and resumes after lawful approval. This fixes a human minister's stored contribution intent reopening “The Contribution Must Wait” on every weekly retry. Actual reviewer decisions, queue resumption, payment checks and explicit manual status remain available. Menu offsets are initialized before the status UI; grant-dependent native UI predicates guard existence before dereferencing saved variables.

Dev.60 distinguishes recoverable native invoice refusal from financial uncertainty. A native check refusal is logged explicitly. An unfunded invoice with **any unexpected native Treasury delta** is held without an optimistic full refund; an unfunded no-charge attempt retains the exact advance-return path. The old nonfinancial `mam_pc_blocked` display marker can clear after seven days only when its saved native before/after are equal, receipt key is zero, no execution is active and the recorded living actor has no account hold. Attempt history and all financial holds remain. `test3`'s Wall attempt key 30 maps to `walls_19`, which another contributor subsequently funded; it was not an unpaid grant or a cancelled Wall project.

Governors' voluntary native contributions remain their own expense and native AI behavior. Non-Treasury native contributions remain in native controls. The module does not automatically fund every governor or waive Influence, native contribution caps, site rules or cooldowns.

### Grand Campaign launch package

The native required slot is `attack_1`, and the contributor must be the Grand Marshal. Funding it can invoke `grand_campaign_contribution_effect` and `tgp_china_ministry.0001`, whose immediate effects can begin war. Optional campaign pledges normally wait for this required pledge.

An existing unlaunched campaign therefore generates a priority **imperial** launch-budget request. The request says it can start war, quotes the pledge and a mobilization provision. Mobilization uses the native major-Treasury quote less existing disposable funds. If the Emperor cuts the budget, mobilization is bounded by the amount left after the mandatory pledge. This is a bounded initial provision, not a promise to purchase every possible army regiment.

After authorization an AI Marshal executes the required pledge; a human Marshal receives an explicit launch choice. The approved mobilization provision must be paid before the pledge runs. Mobilization pays once and is protected locally for 90 days, separately from other supplements. Expiry/cancellation/completion returns only actual unspent surplus above ordinary protected needs, up to that provision. Current maintenance stays serviced separately. Deferred human launch returns after 30 days and can be resumed manually from the contribution action.

Native contributor/war leader, targets, casus belli, participation and rewards remain native. The executor rechecks native conditions; it does not start a parallel custom war. A missing Marshal, unavailable common cash, stale office or native-invalid contribution must wait rather than duplicate a pledge. Save/reload and target-change behavior still require engine tests.

The campaign war is led by the Marshal, even for an Emperor-founded project. Dev.58 gives a human Emperor one nonmodal notice when the project links to a real war and its required contributor is known; the project flag prevents repeated notices. It does not recreate a project or war. In `test1` the allegedly vanished campaign is present and in progress, its Marshal pledge is funded, and the linked native war exists. Do not create a replacement campaign based solely on an empty Emperor-facing view.

Dev.60 prepends a scope-only helper to all **20** native campaign funded-contribution callbacks, including governor contributions: clear an inherited `grand_campaign_war` alias and bind it from this project's existing live saved war. The native participant helper then receives the scope it expects. It never creates/recreates a war or changes pledges/mandates. Campaign completion notifications require a funded contribution and a living recipient. Native project replacements are stored with old/new text and reason in `COMMON-FUND-NATIVE-PROJECTS.json`; dev.61 event/CB guards additionally use the pinned `COMMON-FUND-CAMPAIGN-SAFETY-MANIFEST.json`. Original native hashes, costs and living rewards remain source-checked. Test4 exercises the dev.60 callbacks without their original errors; dev.61 completion safety still needs focused engine testing.

The older starting-project grant and new campaign contribution budget are separate records. There is not yet one unified screen that plans the site, pays every stage and starts every project. Do not describe approval alone as proof that native planning/construction has happened.

Dev.57 repairs the generated lifecycle structure: a project/contribution may have only one of each callback, and a contribution's receipt effect must be inside `on_contribution_funded`. Earlier generation dropped that wrapper when vanilla had no callback, and duplicated `on_cancel` when the base generator had already supplied it. Project cleanup and starting-grant identity now use explicitly saved great-project scopes rather than an event `root` which may be a character. Contribution execution explicitly enables native charging/eligibility checks; callback invoice keys come from a title-stored execution token, not an assumed forwarded event value. No manual second Treasury charge is added.

## 6. Technical ownership and save contracts

| State/API | Owner and meaning |
|---|---|
| `h_china.mam_cf_cases`, serial, reserve, programme, claims, statements | Realm; persistent queue and consolidated accounting |
| `mam_revenue_fund_story` | Pending financial case, amount, subject snapshot, requester, stage, reviewer lease/generation and outcome |
| Office title `mam_cf_cost/headroom/remaining/project_*` | Recurring authorization, quarterly discretion, protected legacy/starting advances |
| Character `mam_cf_open` | Temporary reviewer lease; not the institutional account |
| `mam_revenue_fund_transfer_effect` | Single guarded native transfer boundary; bind payer/payee/amount/floor first |
| `h_china.mam_cf_last_*`, before/after/debit/credit/state | Latest actual native transfer diagnostic; not a full transaction history |
| Project `mam_pc_budget/spent/ceiling/level/approver/approved_on` | Shared remaining authorization, gross executed expenditure, cumulative ceiling and approving institution |
| Project `mam_pc_pending/retry_after` | Per-project kind-13 deduplication and rejection retry |
| Project `mam_pc_launch_authorized/mobilization_reserved/paid` | Separate military mandate and one-time mobilization release |
| Project `mam_pc_executing/native_actor/native_key/last_*` | In-flight lock and native execution proof; not a second invoice charge |
| Office `mam_pc_executing_project/executing_legacy` | Temporary native contribution access token; removed after execution |
| Office `mam_pc_executing_key` | Stable invoice key forwarded through native callback using institutional state; removed with the token |
| Character `mam_pc_wanted_project/wanted_key` | Explicit player intent; revalidated against current holder/eligibility |
| Office `mam_pc_mobilization_*` | Separately protected 90-day initial campaign provision |
| `mam_revenue_project_receipt_story`, `h_china.mam_pc_receipts` | Passive five-year records of verified native pledges: actor, office, project, stable key, amount/date, approver when present, legacy-paid flag |
| `h_china.mam_pc_commitments` | Recomputed sum of active shared project reservations, subtracted from ordinary available cash |

Project completion/cancellation callbacks release unspent envelopes. A callback during execution marks closure, then clears remaining budget after execution cleanup. Mobilization is an advance, so project `spent` includes its gross release; do not infer net final expense from that value alone. The old monthly statement does not list every individual contribution. Use actual balances, project state and receipts together.

All transfers require correct native public accounts, real cash above the chosen protected floor and no payment hold. Verify both debit and credit. AI transfers may require movement between native short/long-term Treasury buckets for an authorized project; that is an internal reallocation, not income. Failed/uncertain transfers must never fall back to `add_gold`, repeated optimistic payment or a forged success notice.

Institutional authorization persists across succession, but pending requests/displayed events are revalidated. Kind 13 remembers its requesting office and holder. A new holder can discover the unpaid invoice; a stale request cannot pay as the old holder. Receipt story ownership migrates to a living Emperor/current heir. Never renumber contribution keys or reuse a released slot's identity for another pledge.

## 7. File map and generation

| Area | Primary source files |
|---|---|
| Provincial appointments | `mam_senior_*` triggers/effects/events/story/decisions; `mam_senior_jurisdiction_*`, `mam_senior_parent_effects.txt`, source-custody helpers |
| Candidate scoring/tasks | `zz_mam_personnel_appointment_values.txt`, `zz_mam_personnel_tasks.txt`, `mam_personnel_assignment_effects.txt`, Personnel AI/service review/direction helpers |
| Native appointment bridges | `zz_mam_civil_governor_appointments.txt`, `zz_mam_senior_native_eligibility.txt`, resignation bridge; preserve existing native parity |
| Central succession | `mam_ministry_review_*`, shared office eligibility, `zz_mam_shared_minister_handoffs.txt` |
| Honors | `mam_exam_*`, `zz_mam_native_exam_bridges.txt`, `gui/zzz_mam_exam_honors.gui`, `gfx/interface/icons/mam_exam/` |
| Common funding | `mam_revenue_common_cash/queue/choice/claims/initiative/returns/preview_*`, common triggers/values/events/story/decisions/interactions |
| New contribution module | `mam_revenue_common_project_orders.txt` under effects/triggers/events/interactions; invoice bindings, eligibility, weights and receipt story |
| Native fiscal/project bridges | `zz_mam_revenue_common_native_spending.txt`, native obligation effect, `zz_mam_revenue_common_*.txt` in great-project types |
| Explicit AI planning | `mam_revenue_common_auto_start.txt`, `mam_revenue_common_start_locations.txt`, hidden `mam_fund.36`; native site audit in `COMMON-FUND-AI-START-MANIFEST.json` |
| Shared UI/policies | `interaction_category_ministry`, `mam_ministries` decision group, Personnel authority laws, `mam_revenue_laws.txt`, English localization |
| Removed case compatibility | Shared qualification/handoff APIs, `mam_removed_case_compat_effects.txt`, one-shot old-story teardown and unavailable retired laws |

Names in the table are relative to their normal `common/...`, `events/`, `gui/` or localization directories. Search the actual definitions before changing a similarly named legacy file.

**Authoring workflow:** edit `tools/build_common_fund.py` and the relevant upgrade/template, then run the full builder. It creates the base and sequentially applies dev.50–61. Contribution authoring lives in `tools/upgrade_common_fund_dev55.py` plus `tools/templates/revenue_projects_*`; dev.56 adds queue deduplication and shorter letters; dev.57 generates explicit AI planning and repairs logged scope/callback errors; dev.58 gates background UI and reports existing Marshal-led wars; dev.59 repairs reconciliation scheduling; dev.60 rechecks grants and campaign scope; dev.61 handles missionary borders, Wall upgrades and living campaign rewards/lifecycle. Running an upgrade alone against already-upgraded output is unsupported. Generated output edits will otherwise be lost.

**Hot-reload publication:** the canonical builder now generates and validates in an isolated temporary copy through `tools/stage_common_fund.py`. Only final changed runtime files are atomically replaced, once per file; unchanged files do not trigger reload. This preserves the user's developer hot reload while avoiding base/intermediate versions in watched folders. Validation failure or detected concurrent edits prevents publication. The raw generation environment flag is internal to that temporary tree. Do not invoke upgrade scripts directly against the live mod. Whole-batch engine atomicity and crash immunity are not claimed.

The staging parent defaults to the OS temporary directory. In a restricted desktop sandbox, set `MAM_BUILD_STAGING_DIR` to an authorized writable scratch directory outside the mod; staging inside the live mod is rejected. The validated trial published **zero runtime files** because the existing dev.58 output was unchanged. Source/tests/build instructions were updated without changing gameplay or the user's launch settings.

The [20:36 crash investigation](CRASH-2026-10-29-203638.md) records an unsymbolized pure-virtual call while opening a character after live rebuild reloads. Its precise cause is unconfirmed. `test1` is byte-identical to the crash bundle's last save and remains intact. Staging is a tooling correction, not evidence of a fixed portrait/engine bug; no gameplay/save rewrite was made for the crash.

Native manifests record original files/hashes and explicit insertions. Reconstruct overrides from native originals plus insertions; do not copy an entire newly updated game file over the audited bridge. The builder refuses source hash drift. A CK3 update requires an explicit native compatibility audit. `COMMON-FUND-CONTRIBUTIONS-MANIFEST.json` audits copied eligibility/prices/AI rules; `COMMON-FUND-CONTRIBUTION-KEYS.json` is the append-only saved-key registry.

Protected hashes in `COMMON-FUND-BASELINE.json` and `REVENUE-IMPLEMENTATION-AUDIT.json` intentionally constrain Revenue changes. `CENSOR-JUSTICE-REMOVAL-AUDIT.json` documents removal-era protection and is historical evidence, not a current whole-tree hash claim.

**Known syntax pitfalls:** localization uses `[saved_scope.GetName]` or numeric `[saved_value|0]`, never `[scope:saved_scope...]`. Event-dependent data must retain event scope; character `Custom()` selectors previously lost that data. Use numeric `ai_chance.base`, supported `custom_tooltip` predicates, atomic scripted-effect parameters, explicit character/title scopes and known native commands. Character-priced project values must be evaluated in character scope. Never invent a command because its name sounds plausible.

## 8. Verification and outstanding work

Run from the mod root with Python 3:

```text
python tools/build_common_fund.py
python tools/verify_revenue_source.py
python tools/verify_common_fund.py
python tools/verify_project_contributions.py
python tools/verify_auto_projects.py
python tools/verify_common_fund_scheduler.py
python tools/verify_project_edge_cases.py
python tools/verify_completion_safety.py
python tools/verify_senior_jurisdiction.py
python tools/verify_staged_publish.py
```

The bundled Python on this machine is `C:\Users\atngu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.

The user-supplied mod illustration is referenced as root `thumbnail.png`. Following a confirmed publisher rejection for its 2.8 MB size, the active preview is now a 512-square PNG below 1 MB; root `thumbnail-original.png` preserves the original bytes. Both are tracked by staging, and the safety check preserves the original hash while checking the upload image's size/dimensions. [MOD-ARTWORK.md](MOD-ARTWORK.md) records the failure and correction. The existing published ID is retained; a local file change does not upload the corrected preview to Steam. The local launcher's null thumbnail registration/rendering remains unverified after refresh; its database/cache was not modified.

The separate `workshop/` description kit includes a generated banner, three section dividers, BBCode copy, text-only fallback and reproduction prompts. Per the user's instruction, its description never uses the main mod image. The four upload graphics use JPEG exports under 250 KB each; large source PNGs are excluded from the ZIP. The kit includes the small main preview separately. The user's uploaded artwork-page links inside `[img]` were repaired to direct image URLs; all four are verified anonymous JPEG responses matching the local exports. `workshop/steam-image-links.json` records the evidence, and the BBCode file is ready to paste with no placeholders. No remote description or main preview was updated, and no gameplay/build version changed. The separate main mod page still showed Steam's default preview during inspection. See [the kit instructions](../workshop/README.md).

The later user-requested transparent revision is separate under `workshop/transparent/`: four alpha PNGs with no background panels, a new placeholder description, prompts and a manifest. All four are below 1 MB; alpha/corners, foreground detail, spelling, hashes and dimensions were checked. The existing verified description still references the older hosted images until the new transparent uploads have real URLs. Neither the main cover nor gameplay changed for this revision.

Checks cover syntax/identifiers/localization regressions, 159 protected files, exact native-plus-insertions parity for 19 project definitions and 152 Treasury contribution prices, 29 general accounting examples, 30 contribution/UI examples, stable native invoice bindings and 28 limited jurisdiction source/graph scenarios. Repeated builds are checked for identical gameplay output. These tests are not CK3 or an emulator.

**Engine acceptance remains partial:** [PLAYTEST-test1-2026-10-29.json](PLAYTEST-test1-2026-10-29.json) records a read-only inspection of `test1.ck3`, game date 1069.2.26. Strengthen Capital is in progress with six funded contributions; one saved Treasury reading verifies a 375 native charge. Grand Campaign project 3 is in progress with `attack_1` funded by Marshal character 30031, 250 recorded spent and 500 remaining in its shared budget. Native war 16777258 exists, uses `grand_campaign_kingdom_invasion_cb`, is led by 30031 and links back to project 3. The save was not modified. The log also confirms one successful paid AI planning continuation. These observations establish representative successes, not all project types or long-run balance.

The same session confirms repeated pending-status popups and unset type/instance/menu-offset reads, addressed in dev.58 source. Its quiet UI/notice retest remains pending. Earlier dev.56 callback/scope failures remain historical regressions. Multi-project interruption, succession, scarce funds, all native bucket timings and observer balance still need testing. Never clear uncertain-payment holds without inspecting their actual records. Use `python tools/inspect_common_fund_save.py <save> --report <report.json>` to extract project/pledge/linked-war evidence without editing a save.

**Later dev.58 observer evidence (`test2`, 1066–1098):** see [the balance audit](BALANCE-AUDIT-test2-2026-10-29.md) and [hashed save/log extraction](PLAYTEST-test2-2026-10-29.json). All nine final ministry stocks are positive; Revenue holds 41,908.86, there are no pending fiscal cases or payment holds, and the latest 1,200 payment has matching debit/credit. Weekly payroll/invoice workers execute, one explicit funded AI start and two native campaign war-start events are recorded, and the former `mam_fund.34` status popup has no execution row. These facts do not validate every project type, prove no earlier deficits or constitute a full transfer history.

**Scheduling defect found in that dev.58 audit, corrected in dev.59 source:** `monthly_playable_pulse` was absent from installed vanilla callback documentation/definitions/invocations. Startup/title gains could reconcile incidentally, while the weekly lease never ran the monthly path. `test2`'s statement was 67 days old and its due gate 42 days overdue. Dev.59 routes due reconciliation through the weekly lease and uses the documented quarterly pulse for recovery. Relief ranking now reads guarded current `mam_cf_programme`, replacing the obsolete unset `mam_rv_priority`. Eight source/model lease scenarios are verified before publication; new engine evidence remains pending. The separate central-succession/Personnel-ledger errors remain documented and those protected modules unchanged. No AI spending weights, amounts or laws were rebalanced.

**Observer diagnostics (dev.59):** `mam_revenue_common_diagnostics.txt` increments compact `h_china.mam_cf_diag_<key>` counters and `mam_cf_diag_last_<key>` dates only from actual effects, with matching `MAM_FUND_DIAG` debug markers. Keys cover reconciliation, proposal cycle/dispatch/no-dispatch, jurisdiction found/missing, valid/no-valid project choices, submitted starting requests, actual starting advance authorization, start-case/budget-case closure result, AI planning/wait/uncertainty and expired unused advances. Closure result 1 is a successful case outcome, not necessarily a new payment (a covered budget duplicate can close successfully). Existing payment/project receipts remain the financial evidence. A no-dispatch result covers role/cash/cooldown/slot eligibility generally; no-valid-choice also covers native type/site restrictions. Diagnostics do not waive requirements, clear holds, change approvals or open player popups. Use the two-year [dev.59 checklist](COMMON-FUND-TESTING.md) before further AI tuning.

**Dev.59 engine follow-up (`test3`, 1098.10.14–1103.3.4):** [audit](BALANCE-AUDIT-test3-2026-10-30.md), [hashed extraction](PLAYTEST-test3-2026-10-30.json). The user's observer run lasted 1,601 days. It records 58 completed statements with matching diagnostics, the latest two days old; 21 actual starting requests, 13 successful starting authorizations, eight refusals and 12 confirmed AI native starts. One Great Wall starting advance entered native waiting and later expired. All nine final ministry balances are positive, Revenue holds 34,223.80, and there are no pending fiscal cases or account payment holds. The verified transfer counter increased by 661; the last 20-Treasury sweep has equal debit/credit. `mam_rv_priority` errors are absent. The scheduler and representative AI initiation now have engine evidence; the remaining Wall start/failed-invoice case and native campaign war-scope errors are not cleared. Grand Campaign project 16777236 has imperial launch authorization, a funded Marshal pledge and a real linked war whose attacker list includes all four funded contributors. Current endpoint authority/programme differ from test2, so this is not a controlled balance comparison. `eventstats.csv` is stale from the prior session and was excluded from current-run conclusions. The audit tool now flags stale stats and captures native primary errors with mod call context. No runtime patch or build bump was made by this inspection.

**Dev.60 engine follow-up (`test4`, through 1128.1.9):** [audit](BALANCE-AUDIT-test4-2026-10-30.md), [hashed extraction](PLAYTEST-test4-2026-10-30.json). Another 9,071 days show 324 reconciliations, latest age four days, 3,267 additional verified transfers and 42 confirmed AI starts. All nine final departments are positive; Revenue 43,021.14, Emperor 16,382.56, zero current account holds, three pending files aged three to four days. The original campaign missing-war-alias and invalid completion-recipient errors are absent after exercised completion callbacks. The earlier eventstats snapshot is partial, not full-run totals. Remaining cases are 28 native Wall `set_great_building` collisions, a paid type-17 missionary grant blocked by the provincial fallback despite its foreign-border native filter, titleless campaign target contexts and dead contributor reward writes. The final different campaign project 50331673 retains paid/authorized pledge state but its war is no longer active after its recorded Marshal died; native campaign duration is 25 years. Investigate that lifecycle before assuming it should be recreated or refunded. Protected central-death and Personnel-ledger errors remain. No runtime fix or build bump was made in this audit; the read-only auditor now flags partial stats and records native project founder/start/construction fields. The native missionary border exception is still only implemented for type 1 in the custom location rule, not type 17; do not mark every project type passed from the successful general AI-start count.

Do not promise these broader design items as finished:

- A general common-Treasury payment interaction to any eligible public account and a deliberate unlawful-approval bypass remain broader redesign work. Vanilla personal gifts remain personal Gold.
- The full conversion of every Revenue screen to native interaction correspondence is incomplete; contribution choice and campaign launch use native character-event layouts.
- Explicit AI site selection/start is implemented in dev.57 source, but native execution and charging remain engine tests. Current initial-grant storage is still one typed slot per office; the contribution envelope is per project. A native-invalid site, changed holder, expired grant, shortage or payment hold must wait rather than bypass restrictions.
- The prior top-resource-bar versus character-window Treasury discrepancy is not proven fixed by source inspection alone.
- No new Censor/Justice investigation or prosecution follows financial receipts. Do not create one while fixing funding.

### Required impact review for future changes

Before changing a feature, identify its institutional owner, current holder rules, payer/currency, approval route, queue identity, native callback, saved IDs and failure/return path. Then check effects on existing commitments and other modules.

| Change | Required compatibility checks |
|---|---|
| Candidate score, qualification or political preference | Personnel and central ministry alternatives; marks; task bonuses; honors; vanilla lower tiers |
| Title transfer, succession or vassal order | Exact jurisdiction components, nested lieges, source custody, simultaneous files, stale displays |
| Treasury/provision | Debit=credit, self-account handling, payroll first, earmarks, claims, optional commitments, AI buckets, no Gold fallback |
| Project cost/eligibility/callback | Installed-source drift, actual actor scope, native rewards, old paid grants, exact project/slot keys, cancellation |
| Fiscal law/programme | Current reviewer, outstanding leases, role sensitivity, cumulative ceilings, imperial military launch |
| Startup or pulses | Single due-date lease, save adoption, succession rescheduling, bounded scans/popups, idempotent reconciliation |
| GUI/localization | Current event scopes, real names/amounts, short prose, only relevant consequences, no unexplained blanks/errors |
| Saved variables or generated identifiers | Append-only migration; no replay, key reuse or baseline reset; rebuild consistency |

After editing, update this document's build/date, the relevant implementation tracker and tests. Report source implementation, user-confirmed gameplay and remaining uncertainty separately.
