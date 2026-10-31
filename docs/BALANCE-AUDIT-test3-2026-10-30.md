# Observer follow-up: test3, dev.59

Inspected 2026-10-30. **The reconciliation fix has engine evidence, and AI ministries now initiate funded native projects.** Remaining project/campaign edge cases prevent marking the whole fiscal module complete. This audit changed no runtime scripts or saves.

## Period and evidence

`test2` ends **1098.10.14**; `test3` ends **1103.3.4**: **1,601 game days**, about four years and four months, rather than the planned two years. Evidence comes from title balances, institutional diagnostics, native projects/war records and the new session's debug/error logs. [Hashed extraction](PLAYTEST-test3-2026-10-30.json); [prior baseline](PLAYTEST-test2-2026-10-29.json). The save hash was unchanged after extraction.

**Do not use this folder's eventstats for the new run:** its timestamp predates the new debug/error logs by approximately twelve hours and its counters belong to the prior session. The auditor now flags this explicitly. Current conclusions use saved dev.59 diagnostic counters and matching debug markers, not stale eventstats query/execution totals.

The endpoint law is **Supervised Fiscal Administration** (limited), and the programme is **Balanced Administration**. `test2` had reserved authority and Recovery. This is an observer lifecycle test, not a controlled comparison holding law/programme constant. Their changes do not invalidate the direct reconciliation evidence, but prevent attributing every spending change exclusively to the scheduler.

## Accounting and solvency

| Evidence | Result |
|---|---|
| Completed reconciliations | **58**, with matching saved counter and debug markers |
| Latest statement age | **2 days**, versus 67 in test2 |
| Proposal cycles / dispatched actors / senior targets found | **58 / 58 / 58** |
| Verified transfer counter | 208 → 869: **661 additional verified native transfers** |
| Pending fiscal cases at endpoint | **0** |
| Account payment-hold markers | **0** |

The count is consistent with the intended approximately four-week cadence over 1,601 days. No historical arrears were replayed as hundreds of instant reconciliations on adoption. This confirms the regular driver and statement freshness in this run; it does not independently time every essential payment or prove no transient deficit between checks.

| Public account | test2 | test3 |
|---|---:|---:|
| Emperor | 3,809.38 | 1,608.24 |
| Revenue/common fund | 41,908.86 | **34,223.80** |
| Chancellor | 166.35 | 77.59 |
| Censor | 109.84 | 83.73 |
| Grand Marshal | 83.32 | **76.47** |
| Personnel | 666.32 | 80.62 |
| War | 1,358.21 | 82.89 |
| Rites | 123.10 | **81.18** |
| Works | 200.87 | **83.45** |
| Justice | 174.24 | 78.89 |

All nine departments end positive, with local cash generally near their operating provisions. War's old 1,200 supplement is no longer outstanding. The latest transfer is a **20-Treasury Justice-to-Revenue surplus sweep**: Justice 98.89365 → 78.89365; Revenue 34,203.80181 → 34,223.80181; debit and credit both 20, receipt state 2.

The common balance declined by **7,685.06**. That is net cash change including native income, expenses, sweeps and grants, **not** a measured project-spending total. Revenue still has ample cash: recorded programme reserve 273.36 and shared project commitments 4,000. Do not drain the remaining bank artificially to make balances look busier.

## Project activity

| Saved diagnostics | Count |
|---|---:|
| Proposal opportunities with at least one native-valid project/site | **21** |
| Opportunities with no valid choice | **37** |
| Actual submitted starting requests | **21** |
| Successful starting advance authorizations / case closures | **13** |
| Refused starting requests | **8** |
| Confirmed native AI planning successes | **12** |
| Entered native waiting state | **1** |
| Positive project advance expired | **1** |
| Successful contribution-budget case closures | **26** |
| Refused contribution-budget cases | **14** |

Success and refusal are both exercised. A budget closure is not a new project or necessarily a fresh transfer; the contribution module can retire already-covered duplicate requests. The 12 native planning success logs match the saved `start_planned` counter. The old “AI never starts after funding” symptom is no longer generally true.

The final save contains supported native work including Strengthen Capital (6/6 funded slots), Census (5/5), several Establish Control projects (4/4 each), religious uniformity (4/4), culture projects (4/4), Grand Canals (6/6), Great Wall (20/36), and Develop Communities (2/3). Native provincial/imperial participants are included in these counts; they are not all common-fund payments. Existing project records cannot reconstruct every completed historical project.

**Remaining start case:** a type-10 **Great Wall** request is followed in the debug chronology by successful advance authorization and the one native-wait diagnostic. The unused advance later expires. This is consistent with the 13-authorizations/12-starts gap. The record does not identify which exact native permission, affordability or site check changed. Do not waive native rules or call the grant successful merely because money was authorized. Review preflight-to-commit revalidation and the safe early return/revision path before increasing approval weights.

**Remaining contribution case:** the active wall retains `mam_pc_blocked = 1`. Its last attempted 500 invoice records **584.22575 before and after** and native receipt key 0, indicating that attempt did not charge. It did not create an account payment hold. Twenty wall slots are funded and other slots remain unfunded. The next audit must distinguish ordinary native eligibility/cooldown/slot limits from executor failure; do not blindly replay the failed invoice or infer that the entire wall project was cancelled.

37 no-choice opportunities are useful evidence: the driver is active while native type/site restrictions prevent some new proposals. Long-running projects and native uniqueness rules can legitimately limit further initiation. This is not a reason to force a fresh project every reconciliation.

## Grand Campaign evidence and errors

Project **16777236** is in progress. Its mandatory **attack_1** pledge is funded by Grand Marshal **37616**, with `mam_pc_launch_authorized = 1` and `mam_pc_mobilization_paid = 1`. The native pledge records a verified 250 charge (529.39403 → 279.39403). Initial mobilization is separately recorded as 224.59102.

Linked war **335544354** exists, uses `grand_campaign_kingdom_invasion_cb`, and is led by Marshal 37616 against 16839763. All four funded project contributors—37616, 36972, 65698 and 35506—appear among its actual attacking participants. Thus this campaign's launch and representative participant joining are confirmed; it has not vanished.

The session still reports **14 missing `grand_campaign_war` scope errors**, each accompanied by unset-scope/comparison errors, in native `grand_campaign_update_war_participants_effect` called through the overridden contribution callback. These need a scoped callback investigation. The top frame being native does not make them irrelevant, and the errors do not prove the currently linked campaign failed: its saved participants show otherwise.

Other retained issues: **17** campaign-completion notifications to absent contributor characters, and **472** unsuitable `top_liege` death contexts in central ministerial succession. The latter remains in the protected module; this audit did not modify it. The previous unset **`mam_rv_priority` error is absent**, and there are no runtime-error primary frames in the new diagnostic or common-cash scripts. This is not a zero-errors claim for the game or all enabled mods.

## Next work

1. Keep the scheduler fix. Its regular accounting cadence and representative native planning now have engine evidence.
2. Investigate the Great Wall advance/failed invoice and native campaign callback scopes before another long observer run. Preserve native site rules, actual financial receipts and Personnel boundaries.
3. After those targeted repairs, test a shorter reproducible case with an immediate save before/after approval. Then assess fiscal-law balance from a matched starting save; this run is not a fixed-law comparison.
4. Later test Revenue as a human for wording, correspondence, law labels and tooltips. An observer run cannot visually validate them.

No runtime changes or new build were made during this inspection. The read-only audit tool was improved to flag stale eventstats and retain native errors whose call stacks reach mod callbacks, plus actual campaign war participants. Historical test2 evidence remains unchanged.
