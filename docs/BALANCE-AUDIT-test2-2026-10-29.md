# 32-year observer audit: test2

Inspected 2026-10-29, source build `0.4.0-alpha.20-dev.58`, installed CK3 `1.20.1.2`. This is an audit, not a balance patch. No game, save, vanilla, Personnel or runtime files were changed. The new read-only extractor and this report are development artifacts.

**Assessment:** the final departments are solvent and representative transfers/projects/campaigns execute. Revenue accumulates a very large common balance while unsolicited project activity is sparse. A scheduling defect must be resolved before interpreting this as merely conservative AI personality or adjusting prices/weights.

## Evidence and limits

Sources: the user's `test2.ck3`, `debug.log`, `error.log`, `eventstats.csv`, current mod scripts and installed vanilla reference scripts. The final save is dated **1098.10.14**; the session starts in 1066. The JSON report records input hashes and a verified unchanged save. Console use of personal `gold 5000` and `influence 1000` appears near the start; this is not a pristine matched vanilla control and does not establish a direct common-Treasury injection.

Reproduce from the mod root:

```text
python tools/audit_common_fund_run.py "../../save games/test2.ck3" --logs "../../logs" --report docs/PLAYTEST-test2-2026-10-29.json
```

See [machine-readable evidence](PLAYTEST-test2-2026-10-29.json). Eventstats eligibility-query counts must not be presented as executed events. Hidden worker runs are checks, not successful payments. Final stocks cannot prove there were no temporary deficits earlier. Expired stories/receipts and completed projects are not a complete historical ledger. Selective success logging cannot establish total project spending or an approval/refusal rate.

## Final public Treasury stocks

These are title treasury balances, not personal Gold or cached monthly income.

| Account | Treasury |
|---|---:|
| Emperor | 3,809.38 |
| Revenue / common fund | 41,908.86 |
| Chancellor | 166.35 |
| Censor | 109.84 |
| Grand Marshal | 83.32 |
| Personnel | 666.32 |
| War | 1,358.21 |
| Rites | 123.10 |
| Works | 200.87 |
| Justice | 174.24 |

The final law is **Reserved Fiscal Authority**; the programme is **Provincial Recovery**. The common reserve record is 754.48, recurring authorization 127.24/month, and active project commitments 375. A bank balance of 41,908.86 is therefore not explained by that protected reserve alone. It is about eleven times the Emperor's public Treasury. Without a matching opening-state snapshot, do not report a precise annual accumulation rate or attribute all of it to pooled ministry income.

War has a separately protected **1,200** operating supplement, explaining most of its larger balance. Grand Marshal has six owned MaA regiment references. Cash, regiment count, regiment size and native maintenance limits remain separate; the save does not establish that the Marshal has built an optimal army.

The realm's verified native-transfer counter is **208**. The last transfer is Revenue to War for **1,200**, receipt state 2: Revenue 43,075.49839 → 41,875.49839; War 84.59775 → 1,284.59775. Both account movements match. This is a single retained diagnostic, not a full list of 208 transactions or 208 grants.

There are **zero pending fiscal stories** among six retained fiscal cases; all six are closed. There are **zero payment-hold markers** in the save. This is evidence against a currently wedged approval queue, not proof that no earlier interruption occurred.

## The main defect: monthly work is not reliably scheduled

`common/on_action/mam_revenue_on_actions.txt` attaches the recurring startup/reconciliation driver to **`monthly_playable_pulse`**. No vanilla definition, script invocation or documented engine callback with that name was found in the installed game. The installed `common/on_action/_on_actions.info` documents yearly and quarterly character pulses, and permits explicitly scheduled custom on-actions; it does not document this monthly callback.

The self-scheduled weekly `mam_fund.95` payroll worker runs, but it does **not** call `mam_revenue_fund_month_effect`. Startup and office-title gains call the broader startup effect, incidentally running a due reconciliation. This produces irregular activity around handoffs rather than a dependable monthly administrative cycle.

Corroborating saved evidence: `mam_cf_statement_date = 400989`, versus current day 401056: the statement is **67 days old**. `mam_cf_next_month = 401014` is already **42 days overdue**. Revenue's current title/council holder is synchronized; task 746 belongs to the current minister. There is no pending fiscal queue or payment hold explaining the overdue statement.

Consequences likely include irregular surplus collection, discretionary refills, fiscal programmes, provincial relief generation and new-project proposals. The 35-day adoption and seven-day essential worker are separate paths, so positive balances and active weekly checks do not validate the monthly loop.

**Recommended first correction:** execute due monthly reconciliation from a reliable institution-owned scheduled driver, retaining its due-date/idempotence guard. The existing weekly sovereign lease could dispatch due monthly work; a documented quarterly pulse can be a recovery check. Preserve one live lease through succession, the adoption delay, reserve/approval rules and existing commitments. Add engine-visible reconciliation counts/dates so a two-year test proves monthly cadence. Do not compensate for a broken clock by increasing AI spending probability.

## Observed gameplay activity

| Evidence | Count / result | Interpretation |
|---|---:|---|
| Weekly payroll worker `mam_fund.95` immediate effects | 1,528 | Essential scheduler is active |
| Ministry contribution workers `mam_fund.31` | 13,742 | Invoice scans run; these are not paid pledges |
| AI project-site proposal worker `mam_fund.96` | 14 | Sparse unsolicited initiation over the run |
| Project choice events `mam_fund.5` | 13 | One site-proposal worker did not reach the menu |
| Explicit paid-AI start continuation `mam_fund.36` | 1 | One confirmed mod-funded native planning success |
| Logged shared-project budget approvals | 4 | Contribution envelopes; not four starting grants |
| Native Grand Campaign war-start events `.0001` | 2 | Campaign execution is possible |
| Native campaign owner completion events `.0005` | 2 | Completion callbacks executed; not proof both wars were won |
| Pending contribution-status event `mam_fund.34` | No row | No recorded execution of the former repeated status popup in this run |
| Department operating-review events `mam_fund.2` | 24 | Operating reviews happen |
| Programme events `mam_fund.4` | 12 | Too little evidence to compare programme balance |
| AI appeal callbacks `mam_fund.97` | 4 | Appeals are being considered |

The last save retains a funded culture project, ID 16, in progress, founded in 1081, with four funded contributions and a common envelope of **625 total, 250 spent, 375 remaining**. One retained invoice demonstrates **62.5** Treasury charged exactly once (217.64608 → 154.64608). Do not label it stalled just because it is old: vanilla's base construction time is 1,825 days, and this type multiplies it by seven before further conditions/modifiers. A separate progress/availability comparison is needed to diagnose a genuine construction freeze.

Personnel is active: **49** logged successful provincial destination grants, comprising **19 promotions, 17 lateral transfers, 13 first-office grants**. Chancellor direction logs show professional nominations 21 times, ministerial discretion eight, continuity four. Service logs record 289 endorsement applications/refreshes and 39 poor assessments; these are not distinct people or promotions. Central ministry handoff logs show 13 verified succession approvals. These observations do not warrant rewriting accepted Personnel gameplay to make Revenue busier.

Payroll plus ministry invoice-worker timing is approximately 1.9% of the eventstats accumulated measured event time. This is not a percentage of total game CPU time, a frame-rate benchmark or proof that all scans are optimal.

## Runtime errors to track separately from balance

| Count | Location / finding | Assessment |
|---|---|---|
| 2,356 | `mam_ministry_review_on_actions.txt:6`, `top_liege` context switch on death | Existing central-succession callback checks a liege context on unsuitable death roots. Scope/ordering maintenance is needed; do not interpret this as 2,356 failed real minister appointments. |
| 36 | `zz_mam_revenue_common_00_ministry_projects.txt:253`, campaign completion sends an event to a missing contributor | The unconditional contributor iteration also exists in the installed native source. Needs a funded/living recipient audit rather than automatic attribution to the funding executor. |
| 5 | `mam_personnel_patronage_story.txt:4`, story ownership transfer targets a dead character | Existing passive Personnel-ledger succession issue. Reported only; protected Personnel was not edited. |
| 3 | `mam_revenue_values.txt:24`, unset `mam_rv_priority` | Current relief ranking still calls a legacy priority reader. It should use the current programme or explicitly guard compatibility state. This weakens the promised Recovery priority. |
| 6 | `mam_shared_office_eligibility_triggers.txt:4–5`, unsupported variables scope | Shared eligibility is reached with unsuitable context in an old Personnel path. Preserve accepted module boundaries when repairing. |
| 1 | Development-project native location tooltip | Missing dynamic `title_capital_county_equal` localization form; presentation issue, not direct payment evidence. |

The earlier large common-fund event-localization failures do not appear among these session's mod runtime error locations. Startup used/never-set compatibility warnings and other enabled mods' errors still exist; zero errors overall is not claimed. No new crash diagnosis follows from this balance audit.

## Next balance work, in order

1. Repair and measure the monthly cadence. Retest two years before another 32-year run. Statements, collections and bounded proposal attempts should advance regularly without duplicate payment.
2. Remove the legacy priority read from current relief ranking, preserving intentional law approval and the native provincial eligibility filter.
3. Add bounded outcome diagnostics for project proposals: eligible type/site found, chosen, submitted, approved/refused, advanced, planned and expired. This makes low activity distinguishable from native site/uniqueness/cooldown restrictions. Do not spam player events.
4. Compare Reserved and Expanded authority using the same opening save and period. Check the Chancellor's programme, Emperor approvals and Revenue personality separately. The current one-law run cannot establish a balanced approval rate.
5. Only then tune idle common surplus, project proposal selection and military replenishment. Prefer needs-based expenditure and protected project commitments over artificially draining the bank or granting every ministry a large unconditional balance.

Acceptance still pending: frequent succession, concurrent projects, new bills during wars, optional/required contribution coverage, low-cash periods and temporary deficits between weekly payments. All nine positive balances at the end are encouraging but insufficient to mark these passed.
