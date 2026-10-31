# Dev.60 observer follow-up: test4

Inspected 2026-10-30. **The two targeted campaign errors are absent after exercised callbacks; reconciliation and representative funded AI starts remain active.** The longer run exposes additional native completion and project-boundary cases. This is an audit, not another runtime patch.

## Scope and evidence

The saved interval is `test3` **1103.3.4** → `test4` **1128.1.9**: **9,071 game days**, approximately 24 years and ten months. [Hashed extraction](PLAYTEST-test4-2026-10-30.json); [prior baseline](PLAYTEST-test3-2026-10-30.json). Save hash verified unchanged. Current source build is `0.4.0-alpha.20-dev.60`.

Saved diagnostic deltas match the new debug-log markers. Eventstats belongs to this session, but its snapshot precedes the final save by about two minutes: its 37 paid-start callbacks are fewer than the 42 actual planning successes in final logs/counters. Treat its positive callback counts as an **earlier partial snapshot**, not complete run totals. The auditor now flags this distinction and records native project founder/start/construction data. Historical baseline reports are unchanged.

Endpoint policy remains **Supervised Fiscal Administration**, with **Balanced Administration**. This long lifecycle run is not a matched vanilla control or a promise that policy stayed constant throughout.

## Reconciliation, transfers and end stocks

| Evidence | Result since test3 |
|---|---:|
| Completed reconciliations | **324** |
| Latest statement age at save | **4 days** |
| Additional verified native transfers | **3,267** (counter 869 → 4,136) |
| Current account payment holds | **0** |
| Pending financial files | **3**, aged **3–4 days** |

The 324 statements are consistent with four-week accounting over 9,071 days. The last transfer is an **8-Treasury Justice-to-Revenue sweep**, with debit and credit both 8 and receipt state 2. These are actual public-Treasury diagnostics, not personal Gold.

| Account | test3 | test4 |
|---|---:|---:|
| Emperor | 1,608.24 | **16,382.56** |
| Revenue/common fund | 34,223.80 | **43,021.14** |
| Chancellor | 77.59 | 85.39 |
| Censor | 83.73 | 79.93 |
| Grand Marshal | 76.47 | **44.33** |
| Personnel | 80.62 | 79.57 |
| War | 82.89 | 131.47 |
| Rites | 81.18 | **168.62** |
| Works | 83.45 | 85.49 |
| Justice | 78.89 | 79.16 |

All nine ministries end positive. This does not establish the absence of every temporary deficit. The common bank has 4,437.50 of active project commitments and a 412.43 recorded reserve, so large available wealth remains. Its net increase includes native income, expenses, sweeps and grants; do not equate the increase to a failure to pay projects.

The three pending files concern a 1,200 War supplement, a 500 Revenue census start and an operating review. They were created only three or four days before the save. Their presence is not evidence of a stuck queue. Native check refusals occurred 296 times and recoverable wait markers elapsed 91 times; these are refusal/retry observations, not 296 successful pledges or lost payments.

## Project activity

| Saved diagnostic delta | Count |
|---|---:|
| Proposal cycles / dispatched ministries / supported targets found | 324 / 324 / 324 |
| Native-valid project choices | **75** |
| No valid choice | **249** |
| Submitted starting requests | **75** |
| Successful starting authorizations | **43** |
| Refused starts | **30** |
| Obsolete request returned before transfer | **1** |
| Confirmed native AI planning successes | **42** |
| Native waiting / positive advance expiry | **1 / 1** |
| Successful / refused contribution-budget case closures | **68 / 41** |

One further starting request is still pending; 43 successful + 30 refused + one returned + one pending accounts for all 75 submissions. A case closure or request is not an additional project or payment.

The one obsolete request was returned through dev.60's new pre-payment path. Both approvals and refusals continue to occur. Current projects include control, culture, capital, development, religion and a campaign; many earlier projects have retired, so the final database is not a complete start/completion ledger.

### Wall findings

The old Wall record and its stale attempt marker are no longer active. Wall completion callbacks actually executed. The former Wall-specific location wait was not the new failed grant: the new wait follows **type 17**, the missionary project. Nine type-10 Wall funding requests occurred, but not every request is an approval or a successful start; do not infer nine Walls from that count.

**New completion issue:** there are **28 `set_great_building` errors** in Wall contribution completion callbacks, each saying the province already has a great building. The installed native callback also uses that setter for existing Wall sections. This needs a valid upgrade/replacement-path audit before claiming the completed sections received their intended level. Do not blindly delete existing great buildings or assume every collision is an already-correct level. The funding-jurisdiction fix does not fix this native completion operation.

### Missionary grant boundary

The lone new `start_waiting_native` event follows a type-17 request/advance in the log chronology. Its native `province_filter` is `top_liege_border_outer`, and the automatic planner searches foreign neighboring counties. However, `mam_revenue_fund_project_location_trigger` grants that foreign-border exception only to campaign type 1; type 17 falls through to the ordinary provincial holder/vassal check. These requirements conflict. The advance later expired. This is a separate location-boundary defect, not evidence that the corrected global Wall rule failed. A future repair should share the supported border-jurisdiction logic while preserving the missionary project's native faith/site conditions.

## Campaign callbacks and lifecycle

The old **undefined `grand_campaign_war`** errors are **absent**. The old `.0008` notifications to missing/unfunded contributor characters are also **absent**. This is not merely a quiet callback-free test: the earlier eventstats snapshot already records **five owner completion events** `.0005` and **18 contributor completion events** `.0008`, plus 11 native war-start events. These counts are lower bounds for the full session and do not establish victory for each campaign.

The original `test3` campaign project 16777236 is no longer in the active project database. The final campaign is a different project, **50331673**, founded by Marshal **16826837**, with its required pledge paid, imperial launch authorization, paid mobilization and a verified 250 native pledge charge. It began construction on **1125.6.2**. Its saved war link **436207746 is not in the current active wars database**. The recorded founder/mandatory contributor died on **1127.7.7**; the project still says `in_progress` and retains long native construction time. The campaign's native duration is 25 years, so its age alone is not proof of a frozen construction clock.

This is an **ended-war/Marshal-succession lifecycle case to investigate**, not grounds to recreate or refund the campaign automatically. Existing native campaign logic can continue through separate targets/wars; that intent and its authorization boundaries must be understood before changing it. The paid pledge, mobilization and mandate must not be replayed.

Additional native-path errors remain:

- **Three** title-holder context failures in `grand_campaign_kingdom_invasion_cb:on_declaration`, during common-funded pledge execution. Its native target-title list can encounter a title without a usable holder.
- **Three** dead-character variable-write failures in `tgp_china_ministry.0005`, involving old Marshal/contributor records.
- **One** culture-project completion tries to change a dead contributor's Influence.

The dev.60 scope binder and notification recipient filter address the original errors, but do not guard every separate native reward or lifecycle path.

## Protected-module findings and next work

The existing central-succession death/liege context error repeats **2,447** times. Shared eligibility has six unsuitable variable-scope errors, and the passive Personnel patronage story has two dead-owner transfers. These remain separate protected-module maintenance; the fiscal audit did not rewrite them or restore Censor–Justice gameplay.

Next targeted corrections should cover the missionary border exception, Wall great-building completion upgrades, and campaign dead-contributor/titleless-target/Marshal-death lifecycle handling. Keep the scheduler and financial safeguards, and use focused before/after saves rather than another 25-year run merely to prove cadence. Human UI/wording and controlled authority-law balance tests remain separate.

No game, save, vanilla or runtime script was edited during this inspection. The audit tool and maintained documentation were updated; no new build was published.
