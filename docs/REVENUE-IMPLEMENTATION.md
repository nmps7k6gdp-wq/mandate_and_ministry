> Historical dev.44-48 snapshot. Superseded by the dev.49 [common-fund implementation](COMMON-FUND-IMPLEMENTATION.md), [expense audit](COMMON-FUND-EXPENSE-AUDIT.md), and [test checklist](COMMON-FUND-TESTING.md). Earlier runtime statements have not been revalidated for dev.49.

# Revenue implementation guide

Build: **0.4.0-alpha.20-dev.48**. Source implementation complete on **2026-10-28**. The first dev.45 user transfer passed its live treasury balance check; broader behavior and the dev.46-48 changes still require engine verification.

## Player entry points

Presentation should follow the [user-approved native correspondence and grouped-effects reference](EVENT-DESIGN.md). Full conversion of existing Revenue screens to that layout is pending; this design preference does not itself change transaction logic.

| Role | Entry point |
|---|---|
| Revenue | Right-click a beneficiary: **Revenue: Designate a Funding Recipient**. Then right-click a donor ministry: **Revenue: Arrange a Treasury Contribution**. Designation lasts 90 days. |
| Revenue | Right-click an eligible department: **Revenue: Review Departmental Funding**. |
| Revenue | Right-click a senior civilian governor: **Revenue: Settle Provincial Contributions**. |
| Senior civilian governor | Right-click Revenue: **Revenue: Petition for Public Assistance**. Uses the native medium Influence cost; optional usable hook/debt-clearance request. |
| Chancellor | Right-click Revenue: **Revenue: Direct Fiscal Priorities**, when no imperial override prevents it. |
| Chinese emperor | Right-click Revenue: **Revenue: Review Fiscal Authority** or **Revenue: Direct Fiscal Priorities**. Change authority in **Realm > Laws > Fiscal Authority**. |
| Minister whose budget was cut | Use the result event's appeal option, or right-click the Chancellor/emperor: **Revenue: Appeal Departmental Funding**. |
| Official with assigned pending business | **Revenue: Resume Fiscal Business** decision. Other roles do not receive this decision merely because someone else has a case. |

Startup/quarterly maintenance initializes the module. Native title gains wake maintenance after three days. New Revenue officeholders receive a fiscal review through the case queue; real urgent needs can take precedence. Existing saves have a quarterly fallback if the startup callback does not run on load. Restart CK3 before the joint playtest so the full new script database is loaded together.

## Editable amounts and visible outcomes

Revenue can revise a draft before submitting it. The ordinary event editor adjusts by 25/100, uses exact current debt or selects the payer's available surplus. There is no generic free-text input or custom GUI. Selecting an amount moves no money. The final recommendation still obtains consent and the appropriate approval, and a large draft cannot override the reserve.

Default assistance and debt clearance use the emperor's public treasury. Revenue pays only when explicitly selected as donor; another ministry contribution uses that ministry's own public account. The event names the payer and recipient.

Portrait result events replace the title-only success/refusal banners. They distinguish donor consent awaiting approval from actual payment, and report budget changes, refusal, return, uncertain transfers and appeal outcomes. Recipients are deduplicated per notice; AI-only participants receive no informational popups. Acknowledging a result cannot repeat a transaction. Dev.48 selects event-dependent prose with native scripted event descriptions; character-only Custom localization is used only for realm-level facts. An unknown or older result never defaults to a paid message.

## Decisions and authority

A request first goes to Revenue. A contribution then asks the donor for consent; a direct imperial grant skips donor consent. Routine accepted measures can execute under an active mandate. Reserved expenditure and upper/military/self-benefiting matters go to the emperor. An ordinary disputed contribution under delegated authority can go to the Chancellor. Budget recommendations always receive the appropriate superior's decision.

A superior can approve, reduce a payment, return a recommendation or refuse. Fiscal authority is a realm law with native-style icons and effect descriptions. It survives succession; changes cost 150 Prestige, require peace and have a five-year cooldown. The prior variable-based mandate migrates once without a charge or cooldown. The event is informational and cannot enact a competing mandate. Annual delegated imperial spending is preserved on a law change.

Changing holders or accounts invalidates old consent/approval and sends the file back for reconsideration. An annual Revenue review may recommend a policy change; it cannot write the Chancellor's policy directly. The emperor owns the spending mandate and any imperial priority override.

The first implementation deliberately does not provide a custom regency system. Unsupported office portfolios or unavailable authorities do not gain new fiscal powers. Supported public accounts require adult officeholders; native handling remains for requests outside the module's supported route.

## Payments and outcomes

- Payments use `pay_short_term_treasury` once, with the donor as payer. No unmatched `add_treasury`, personal-gold debit, title grant or vassal transfer is used.
- The helper checks live holders, primary accounts, government, mandate, consent/approval, balance, cooldown and protected reserve before committing.
- The file is marked non-pending before the native payment. Actual payer/payee identities and both before/after balances are retained. The calculated donor debit and recipient credit must both be positive and match the approved amount within 0.01. Only then are success consequences and a paid receipt produced. The receipt shows the account balances at payment time, rather than their potentially changed values when the notice is read.
- An uncertain result is closed without an automatic retry or success rewards; an explanatory notice and one-year protective cooldown prevent an immediate second attempt. This diagnostic behavior must be checked in the engine, since native budget buckets and balance-update timing have not been tested.
- The beneficiary gains +15 opinion of Revenue and +10 of the actual payer for three years. Non-imperial donors gain -10 opinion of Revenue for three years; forced donors additionally gain -15 of the approving superior. Individual modifiers are refreshed rather than stacked.
- Voluntary funding/approval of a personal rival can give Vengeful decision makers 15 base Stress. Knowingly favouring Revenue's personal connection while severe cases wait can give Just/Honest decision makers 15 each. Explicitly forcing a disputed contribution gives Compassionate authorizers 10. Compassionate refusal of an affordable severe funding need gives 10. Tooltips are conditional; deferred/stale/failed actions receive no success stress.
- A native-route accepted petition awards its deferred native Influence credit only after payment. A hook is consumed only on success. A debt-clearance hook/catalyst requires the actual payment to leave the applicant out of treasury debt; a partial grant is not labelled a completed debt clearance.

Recovery is a public grant plus bounded low-control county support. It is not a tax-remission switch. County effects apply to the nearest supported senior jurisdiction and do not stack across a parent empire and nested kingdom. A provincial remittance is a negotiated one-time public contribution, not an allegation of unpaid taxes.

A project appropriation pays its responsible public office and marks the existing native project funded for one year. Native ownership, construction, contributions and completion remain unchanged. It does not guarantee how every treasury unit will subsequently be spent or complete a project automatically.

## Budget appeals

An actual Revenue-recommended cut creates one appeal opportunity for its affected minister, lasting 180 days. A successor cannot inherit it, and a later contract edit invalidates it. An ordinary appeal goes to the Chancellor; an imperial/sensitive decision can only be overturned by the emperor. The reduced budget stays in force pending a decision. A successful appeal restores the exact pre-cut level, gives +10 opinion of the deciding superior for three years and removes the specific Revenue-cut opinion penalty. A refusal keeps the budget and gives -10 opinion of the superior for two years. Neither outcome transfers treasury.

AI ministers lodge their one appeal if financially distressed or Ambitious/Arrogant/Greedy. Superior AI weighs financial need against reserve-building policy. No appeal chain is created.

## Recurring AI

The Chinese realm runs a cadence-guarded quarterly scan, independently of Revenue's council assignment. Real financial distress/recovery/project needs are ranked with bounded political bias. At most two new funding cases are created per scan. Reserve-building policy can also propose one appropriate provincial contribution; one eligible department can receive a budget review.

The annual review and policy ownership are separate from native annual/random-annual budget maintenance. AI uses the same financial cases, options and authority gates as players. There is one active Revenue case per recipient, with priority/aging, 30-day deferral, 180-day ordinary petition cooldown and one-year proposal expiry. No answer is never consent. Native requests and player Ministry petitions share records, payment safeguards and aid cooldowns; unsupported native requests keep their own costs, cooldowns and consequences.

Initial personality weights and event-volume targets are provisional. No observer test has been performed. Relevant debug messages begin `MAM_REVENUE:`. Realm-title counters include `mam_rv_scan_count`, `mam_rv_last_need_count`, `mam_rv_payment_count`, `mam_rv_refusal_count`, `mam_rv_uncertain_count`, `mam_rv_rejected_commit_count`, `mam_rv_year_spent` and `mam_rv_serial`.

## File ownership

| File group | Responsibility |
|---|---|
| `common/scripted_triggers/mam_revenue_triggers.txt` | Supported roles/accounts, live-file identity, authority, eligibility and offer/payment gates |
| `common/script_values/mam_revenue_values.txt` | Reserves, native budget-level query, urgency and bounded relationship bias |
| `mam_revenue_records_effects.txt` | Create/deduplicate/close records and bind displayed scopes |
| `mam_revenue_queue_effects.txt` | Actor selection, priority queue, presentation generation and succession revalidation |
| `mam_revenue_transaction_effects.txt` | Authorization, one native payment, exact-result guard, contract commit and success consequences |
| `mam_revenue_choice_effects.txt` | Player/AI option actions and conditional previews |
| `mam_revenue_policy_effects.txt` | Mandate, policy ownership/recommendations and native budget-event scope contract |
| `mam_revenue_initiative_effects.txt` | Initialization, recurring scans, proactive cases, donor search and refusals |
| `mam_revenue_bridges_effects.txt` | Existing project/recovery connection and native-request intake |
| `common/character_interactions/mam_revenue_interactions.txt` | Role-owned Ministry entry points |
| `common/character_interactions/zz_mam_revenue_native_requests.txt` | Single native definition override; supported players see the Ministry petition, native AI routes into the same queue, other branches retain native behavior |
| `common/on_action/mam_revenue_on_actions.txt` | Additive startup, quarterly/yearly and title-gain callbacks |
| `common/story_cycles/mam_revenue_story.txt` | Persistent cases, owner succession, pending maintenance and finite outcome retention |
| `events/mam_revenue_events.txt` | Ten visible event types and two hidden dispatchers |
| Revenue modifiers, opinions, contextual localization and English localization | Presentation and bounded outcomes |
| `mam_revenue_amount_effects.txt`, `mam_revenue_feedback_effects.txt`, `mam_revenue_appeal_effects.txt` | Draft editing, frozen outcome data and guarded budget appeals |
| Revenue laws and law group | Persistent fiscal authority, costs, cooldown and AI preferences |
| `common/decisions/mam_revenue_decisions.txt` | One actor-owned resume control |

Effect files in this table live in `common/scripted_effects/`. All new definitions use Revenue's prefix. Realm state is stored on `h_china`; financial snapshots use the actual current public primary account. Records use separate funding/budget/settlement/annual/mandate/priority/appeal slots. Financial kinds are aid, contribution, remittance, budget, recovery and project funding; control kinds are provincial review, annual review, mandate, priority and priority recommendation.

The existing ministry-seat synchronization helper is a read-only shared dependency. Personnel appointment/service/score files, title custody and the removed judicial runtime are not rewritten.

## Verification record

Run `tools/verify_revenue_source.py` with the bundled Python to repeat read-only checks. Current result: 24 files, 126 custom definitions, 15 events, 230 English keys; identifiers, macros, trigger/effect placement, native bridge parity, payment guard and module-boundary checks passed.

The native bridge's provenance is recorded in [REVENUE-NATIVE-BRIDGE.json](REVENUE-NATIVE-BRIDGE.json). The verifier checks the installed original definition hash and exact preservation of its unsupported acceptance body, costs, cooldowns, availability, AI and decline sections. A future game update must review this bridge rather than blindly copying it forward.

The first live contribution and its errors are recorded in the [playtest log](REVENUE-PLAYTEST-LOG.md). Dev.46 fixes the first source issues; dev.47 adds presentation/gameplay feedback; dev.48 fixes the event-scope localization and misleading notice selection found in the next session. The current log reports one dev.47 payment at 20:17:46, but its account identity and amount are absent. The user identified Grand Chancellor as the donor; no fresh post-payment save is available to inspect that transaction. Broader engine proofs, UI QA and multi-year AI balance remain pending in the [main tracker](REVENUE-REVAMP.md). The dev.45 success diagnostic proves that one transfer passed its balance check; it does not validate every transaction branch or the subsequent patch.
