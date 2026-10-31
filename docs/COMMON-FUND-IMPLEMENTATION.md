# Common fund: implementation

Build **0.4.0-alpha.20-dev.61**, 2026-10-30. **Test4 provides dev.60 accounting/AI evidence. The targeted dev.61 fixes below require focused engine retesting.**

Current whole-mod contracts and editing instructions are in [MOD-CURRENT-STATE.md](MOD-CURRENT-STATE.md).

Latest [test4 evidence](BALANCE-AUDIT-test4-2026-10-30.md): another 9,071 days, 324 reconciliations, latest statement four days old, 42 confirmed AI starts, all nine final departments positive, and no current account holds. The former missing campaign war alias and invalid completion-recipient errors are absent after actual completion callbacks. The long run exposes native Wall great-building collisions, one type-17 foreign-border grant falling into the provincial rule, and dead-contributor/titleless-target campaign paths. A later campaign retains an ended war link after its Marshal died, requiring lifecycle review rather than automatic relaunch. Current-session eventstats is an earlier partial snapshot; counts in the audit are qualified accordingly. No runtime patch followed this inspection.

## Dev.61: missionary sites, Wall completion and campaign safety

- Implemented: missionary type 17 receives the same approved foreign-border exception as type 1. Native site/faith eligibility remains; existing unexpired paid grants can retry without another payment.
- Implemented: Wall contribution completion removes only known lower Wall levels 1–3 before setting level 4, following vanilla's building-upgrade pattern. Existing level 4+ is retained; an unrelated great building is preserved and diagnosed. Native living-contributor rewards remain. Already-completed historical sections are not upgraded retroactively.
- Implemented: all 20 campaign contribution validity callbacks and the common-fund invoice binder require a living current Marshal in the imperial realm before a new native action/payment. The worker records active-war, between-war or missing-command status and the current Marshal on the project. It does not restart wars, reset launch approval, replay pledges or refund them. A funded campaign with no live war and all counties of its nonempty target list already secured can complete through the native callback.
- Implemented: source-pinned native `.0004`, `.0005` and campaign CB overrides add only missing-holder/portrait and living-reward guards. A replacement Marshal does not receive a deceased predecessor's personal credit. Culture's four personal completion callbacks also require a living contributor; provincial effects remain.
- Verification: the staged build runs the existing fiscal, jurisdiction, native price/key/parity and scheduler checks plus `verify_completion_safety.py`. Its report separates source/model verification from pending engine execution. The native safety registry pins original file/definition hashes and exact reviewed patches; future game updates must be audited deliberately.
- Presentation: the user's unchanged square artwork is `thumbnail.png`; the descriptor uses it as the mod image. See [MOD-ARTWORK.md](MOD-ARTWORK.md).

Save contract: no new case/key IDs, no save mutation, no retrospective charge/refund, no automatic war recreation, and no change to Personnel. Test4's ended campaign war is a native between-stage condition, not proof of an unpaid launch. See the [dev.61 checklist](COMMON-FUND-TESTING.md).

Publication result: all eight staged source/model checks passed, including 159 protected files, 19 native project definitions and 152 contribution bindings. Publication regression checks passed separately; the final repeated full build published zero runtime or report changes. Both the packaged descriptor and the exact local launcher registration now reference the original thumbnail and dev.61. Engine behavior and launcher rendering remain untested by the agent.

## Dev.60: Wall jurisdiction, final grant checks and campaign callbacks

The Wall starting-grant mismatch is concrete: native Wall types 10–12 have no provincial location filter, and AI plans them in the imperial capital context, but the old custom location check allowed only type 9 to escape the selected governor's province. Wall preflight omitted the custom location restriction, so it could approve a site that paid-grant execution then rejected. New Wall requests record imperial jurisdiction; the location predicate recognizes 10–12 as imperial work. Previously paid valid Wall grants use that correction without another payment. Territorial, geographic and border project restrictions remain.

The existing 17-type native site search is shared between AI menu preflight and final grant commitment. Commitment checks the actual requesting holder, current native type/site eligibility and the current character-priced starting cost before transferring Treasury. Changed conditions return the request (outcome 4) with an explanatory letter and no payment. This neither fabricates a temporary paid grant to probe the engine nor waives native planning/Influence/cooldown rules. A historical grant that already expired is not recreated.

Every one of the 20 native campaign funded-contribution callbacks now binds `grand_campaign_war` from its own project's saved live war, clearing an inherited alias first. This covers native governor contributions too. The helper is scope-only: first pledges keep native war-start behavior, subsequent pledges receive the existing war, and no second war is declared. Completion notifications now require a funded slot and a living contributor. The original source hashes remain; the one small notification replacement is documented as old/new/reason under the campaign definition's `post_replacements`, alongside the callback insertions. The native-parity check applies that explicit replacement and still checks all original native files, 19 project definitions and 152 prices.

The allegedly stuck Wall invoice in `test3` is key 30 (`walls_19`). Its attempt charged nothing, and that exact slot was later funded by another contributor. The old `mam_pc_blocked` flag was stale presentation state. A safe no-debit/no-receipt wait can now clear after seven days, with a live recorded actor and no current account hold; its attempt snapshot stays. Native check refusals receive a diagnostic. Any unexplained native cash movement on an unfunded attempt now enters the uncertainty hold path rather than returning the entire advance optimistically. Holds are never reset, and an ordinary unfunded/no-charge refusal still returns only the actual advance.

Staged checks pass, including the new [edge-case source/model report](PROJECT-EDGE-CASE-VERIFICATION.json): imperial vs provincial jurisdiction, all 17 final price/site branches, all 20 native campaign callback bindings, funded/living notification recipients, native-refusal returns and partial-debit holds, plus the saved `test3` fixture. These are not a dev.60 engine execution claim. The full builder is still required; no direct upgrade-script run or vanilla edit is part of deployment. New behavior has a [focused test checklist](COMMON-FUND-TESTING.md).

Latest [test3 evidence](BALANCE-AUDIT-test3-2026-10-30.md): 1,601 days, 58 completed reconciliations, 21 starting requests, 13 successful starting authorizations and 12 confirmed AI starts. All nine final ministry balances are positive; the common bank holds 34,223.80, with no pending fiscal cases or account holds. One Wall advance waited and expired; another wall invoice retains a failed-attempt marker. The active Grand Campaign has a funded Marshal pledge, a real war and all four funded contributors on its attacking side, but native war-scope errors and missing completion-notification recipients remain. The previous unset relief-priority error is absent. Current-session eventstats was unavailable (the file was stale); conclusions use save diagnostics and current logs. This read-only audit did not change runtime behavior.

## Dev.59: reliable reconciliation and measurable project activity

The [32-year test2 audit](BALANCE-AUDIT-test2-2026-10-29.md) found a solvent common fund of 41,908.86, sparse AI project initiation and a reconciliation statement 67 days old. The former `monthly_playable_pulse` hook has no documented/scripted native source on the installed build. Startup and title gains could reconcile incidentally; the live weekly worker could not.

Due reconciliation now runs within the existing seven-day sovereign lease, retaining the independent 25-day monthly guard. Normal accounting periods are approximately four weeks (28 days), not strict calendar months. A native `quarterly_playable_pulse` entry replaces the unsupported monthly hook and repairs the existing lease through startup logic. There is no second payment timer. Existing saves retain due dates, authorization, project cash, receipts and holds; an overdue save settles its current position once rather than replaying past months. First adoption still takes 35 days. New funding proposals remain bounded to one ministry per reconciliation, with existing native eligibility, law and queue checks.

Relief ranking now uses guarded `mam_cf_programme = 2` for current Provincial Recovery instead of the retired unset `mam_rv_priority`. The existing +25 preference still requires genuine recovery need. No prices, spending weights, reserve sizes, authority permissions or Personnel gameplay were changed.

The Laws window uses **Revenue Fiscal Authority**, with **Imperial Fiscal Control**, **Supervised Fiscal Administration**, and **Delegated Fiscal Administration**. Existing law IDs, indices, icons, costs and effect descriptions remain; only names and the explanatory breadcrumb change.

New compact counters/date stamps on `h_china` and fixed debug markers diagnose the actual effect paths:

| Diagnostic key | Meaning |
|---|---|
| `reconciled` | Completed statement/reconciliation, not a weekly eligibility check |
| `proposal_cycle`, `proposal_dispatched`, `proposal_no_dispatch` | A regular proposal opportunity, selected ministry, or no eligible dispatch under the existing cash/role/cooldown/slot rules |
| `proposal_jurisdiction_found`, `proposal_no_jurisdiction` | Scheduled actor found/no longer found a supported senior target; Marshal still needs a frontier |
| `proposal_valid_choices`, `proposal_no_valid_choice` | Native type/site preflight leaves at least one or no eligible project in the chooser |
| `project_requested` | A real starting request was created; separate log marker gives its type number |
| `start_advance_authorized` | Successful initial grant committed real cash or an in-place custodian reservation; this alone is not native planning |
| `start_result_N`, `budget_result_N` | Starting/contribution case closed with existing outcome code N; result 1 does not always mean a new payment, especially covered budget duplicates |
| `start_planned` | Native AI planning passed the existing project/charge receipt checks |
| `start_waiting_native`, `start_no_project`, `start_payment_uncertain` | Paid grant waits on native conditions, native planning returned no project, or an uncertain created project is held without replay |
| `project_advance_expired` | A grant expired with positive remaining project cash; existing sweep/return rules still apply |

Counters are `mam_cf_diag_<key>` and last-date stamps `mam_cf_diag_last_<key>`; fixed debug lines start `MAM_FUND_DIAG:`. They initialize missing counters only and never reset historical ones, pay cash, change a law, remove a hold or create a player popup. A wait counter is recorded when entering the existing logged wait state, not continuously every day. The read-only save auditor already extracts these `mam_cf_` variables and debug markers.

Staged publication runs all prior required verifiers plus `verify_common_fund_scheduler.py`. Its eight bounded source/model cases cover overdue saves, normal two-year cadence, duplicate callbacks, first adoption, unavailable custody, sovereign succession, missing leases and reload retention. This is not engine confirmation. The separate central-death callback, passive Personnel story-owner and native campaign-notification errors remain outside this fiscal patch; protected module hashes must still match.

Retest from `test2` as described at the top of [COMMON-FUND-TESTING.md](COMMON-FUND-TESTING.md). Expect more regular fiscal activity, but do not require every request to be approved or a campaign to occur inside a short peacetime window. Valid approved projects and mandatory pledges must progress when native conditions permit.

## Dev.58: pending-status spam and the supposedly missing campaign

The user supplied `test1.ck3` after reporting “The Contribution Must Wait” on every funding request and a vanished Emperor-founded campaign. Read-only inspection confirms the campaign is still present: project 3, `in_progress`, required `attack_1` funded by Marshal character 30031, 250 spent/500 remaining, with an existing `grand_campaign_kingdom_invasion_cb` war 16777258 led by 30031. Strengthen Capital is in progress with six funded contributions and a verified saved 375-Treasury charge. Evidence is recorded in [PLAYTEST-test1-2026-10-29.json](PLAYTEST-test1-2026-10-29.json); the save was not changed. The latest failed optional attempt is separate from the already paid mandatory pledge.

The modal spam came from the weekly worker retrying a human minister's saved intent while its budget awaited review. `mam_fund.31` now resets a manual-action marker; pending requests are skipped, and only an explicitly chosen UI action may open status event `.34`. Reviewers still receive real recommendations and approved work resumes. The status event initializes its page offset, and native location/contribution predicates guard missing grant variables before comparing them. The session's unset type/instance/menu-offset errors have explicit source regressions.

A once-only nonmodal imperial toast now identifies an existing campaign war and its Marshal contributor. It does not cancel, recreate or repay the project. Restart and reload `test1` to verify quiet background retries and war visibility; no new campaign or replacement grant should be necessary for the recorded active project.

## Dev.57: explicit AI planning and engine-log regressions

The user's continued test produced concrete engine errors at 10:09–10:16: duplicate `on_cancel` blocks; a bare `if` in a contribution definition; `mam_cf_selected_project` saved as temporary despite an existing permanent target; project/character comparisons using `root`; and unset result reads during tooltip traversal. Several funded slots then entered uncertain-receipt holds. The native-parity verifier previously accepted generator insertions without checking the engine's callback schema. New regressions check callback uniqueness/placement and target lifetime collisions in addition to parity.

The generator now preserves an absent native contribution callback's wrapper, merges lifecycle additions into one callback, captures actual great-project scopes, and hides internal callback accounting. Coverage checking uses distinct read-only story references. The receipt key is stored on the executing office and native contribution charging/checks are explicit; no second manual charge or blanket hold reset is introduced.

A paid AI starting grant now schedules `mam_fund.36` one day later and is reconsidered in the weekly contributor callback. The 17-type dispatcher checks native planning eligibility/current cost, finds an authorized native-valid site, and invokes native planning with the actual minister as founder. AI project choices first preflight locations; Marshal proposals choose frontier jurisdictions. Campaign location authorization now permits exterior neighboring counties while preserving the separate imperial pledge/war mandate. Old valid grants need no new transfer; impossible/changed sites retain funding and wait seven days. Creation with uncertain charge/receipt is held without replay.

This build's native planning, pledges and war-start behavior require another in-game test. Source checks do not prove that the engine charged or created a project. Existing uncertain-payment holds are preserved because no fresh campaign save was available for inspection.

## Dev.56: repeated campaign approval and correspondence

The user reports the same campaign request returning after Authorize. The current debug log records one native-funded invoice with uncertain receipt/cash at 08:50:43; it does not name that invoice. The available local saves predate this campaign, so the exact saved approval state has not been established.

Request creation now explicitly requires an eligible unfunded invoice that lacks sufficient lawful coverage, has no usable paid legacy allowance and is not executing. The former execution fallback could ask for funding when a lock or native execution condition failed, even if authorization was sufficient. Covered pending duplicates retire during queue resolution and commit without another payment or success letter. An existing launch mandate is retained; a genuine financial amendment does not repeat the launch-approval wording. Receipt-failure holds remain intact, with attempt actor/key/price/before/after/date saved on the project for diagnosis.

The campaign request is shortened to fit native letter space; detailed launch/mobilization rules are in the approval tooltip. The displayed mobilization cap follows revisions to the amount. These are source corrections; restarting and reproducing the saved campaign is still necessary to verify the reported loop has stopped.

## Dev.55: project contributions and explicit campaign finance

Existing projects now have one shared remaining contribution budget, with per-project pending requests and cumulative authorization. Kind 13 joins the existing fiscal review queue. Approval reserves cash in common custody; eligible native invoices receive their exact actor-priced advance and execute the real contribution. Required continuation has no new-project cooldown. Ministers can select a concrete contribution; AI ministries discover required invoices and bounded optional opportunities weekly.

The binding manifest covers 152 native Treasury contributions. Their native eligibility, prices, AI values, contributor credit and rewards remain native. A paid legacy allowance is consumed without a second grant. Separate projects do not overwrite one office's contribution slot. Actual receipt/cash verification, exact failed-advance return and account holds prevent blind duplicate payment. Five-year passive pledge receipts are financial records, not a restored investigative system.

Grand Campaign receives a priority imperial launch-budget review under every fiscal law. It explicitly warns that the Marshal's native `attack_1` pledge can start war. A separate, bounded mobilization advance pays once and is protected for 90 days; an approved but unpaid provision blocks pledge execution. Changing native prices triggers a budget amendment instead of exceeding the ceiling. Human Marshals confirm launch and can defer/resume it; AI Marshals execute authorized native pledges. Actual war start/callback timing remains an engine acceptance test.

Unspent project envelopes release on completion/cancellation. Unspent mobilization returns only above remaining operating needs. Source tests verify native parity and accounting contracts; they do not establish successful native execution. See [REVENUE-PROJECT-CONTRIBUTIONS.md](REVENUE-PROJECT-CONTRIBUTIONS.md) and the dev.55 section of [COMMON-FUND-TESTING.md](COMMON-FUND-TESTING.md).

**Workflow review update:** source coverage does not establish an end-to-end working fiscal lifecycle. The [complete audit](REVENUE-WORKFLOW-REVIEW.md) records dev.52 project/front-end gaps. Dev.53–54 correct capital jurisdiction and project-price context; dev.55 implements the contribution/launch portion described above. The broader [replacement contract](REVENUE-COMMON-FUND-DESIGN.md) still contains unimplemented work; it is not a statement that every proposed fiscal interaction exists.

## Dev.54: project cost scope, visible grant reasons and AI reserves

The native starting-price helpers contain character tests such as `is_councillor` and character-income based treasury values. The old grant guard entered `primary_title` before evaluating `$COST$`. It therefore evaluated a character price as a title, losing the minister discount and potentially taking the wrong treasury/Gold branch. With the screenshot's base-price fixture, Develop Communities costs 500 for the minister but the old title-scope calculation requires 1,000. The same error existed in contribution allowance checks.

Both guards now bind their required native price with `save_temporary_scope_value_as` while still in the founding/contributing character's context, then compare the title-stored grant to that value. Type, expiry, unused-starting-grant and hold requirements remain. All 17 starting project bridges now expose those individual conditions instead of one opaque generic checkbox.

Requests and paid notices identify the specific project type. Own-office provision names its recorded project. An ordinary operating allowance or Strengthen Capital grant is not automatically a Develop Communities authorization. No existing grant is reset, enlarged, repaid or paid a second time by this correction.

Funded AI project reserves can move internally from the native short-term budget to the long-term project budget, up to the matching reserve shortfall and available short-term balance. This uses the installed native `move_budget_treasury` command, does not touch personal Gold or war-chest funds, does not grant extra cash, and logs an unexpected total-treasury change. It runs after the grant is recorded and during normal office upkeep to prepare existing grants too. Engine behavior still requires confirmation.

The current human route remains: an approved matching starting grant -> native Choose Location within its approved area -> Start Project, subject to native site/currency requirements. The displayed mandatory contribution is a separate expense. These targeted corrections do not implement the full proposed project executor, multi-order lifecycle or automatic contribution continuation.

## Dev.53: Strengthen Capital jurisdiction

The screenshot's unchecked jurisdiction requirement was a custom common-fund constraint. It required the location's county holder to be the approved governor or their vassal. This excludes a directly Emperor-held capital when the grant was requested through an unrelated governor.

TYPE 9 now accepts a location inside the Chinese imperial realm, including the Emperor's own counties. All other project types retain their existing governor-jurisdiction rule. New Strengthen Capital funding requests name `h_china` as their target; existing TYPE 9 grants work without a reset or duplicate payment. Type, cash, expiry, payment-hold and native eligibility/site checks remain intact. Native game files and native project overrides were unchanged by this correction.

The native definition also sets the empire-tier AI planning interval to zero and hegemony to six. That is a separate reason not to promise automatic Works execution from this jurisdiction fix. The missing explicit execution and contribution lifecycle remains in the full redesign. The screenshot shows 1,000 starting treasury and 1,000 mandatory contribution cost; location approval alone is not evidence that construction is funded.

## Dev.52: Rites debt, ongoing military bills and AI project readiness

The source allowed the discretionary quarterly cap to block the essential payment pass. A settled opening buffer and later bills could exhaust that cap while Revenue retained ample cash. This is a confirmed source defect; no current post-failure save was available to prove every cause in the reported Rites account.

Essential provision now bypasses that cap and its ledger. The target follows two months of the greater of approved and currently observed native recurring bills, plus separate discretionary headroom and supplementary provision. Project earmarks remain protected. Current costs do not overwrite approved review records. Existing expenses are serviced while expansion is reviewed, since native payroll itself cannot be paused by this module. Essential deficits and debt reduce only through real, verified bank-to-office payments. Insufficient common cash is still shared proportionally, and uncertain-payment holds remain binding.

A single imperial hidden event checks all nine offices weekly. Startup schedules the first check after one day; a due-date/sovereign lease prevents duplicate execution and restarts custody after imperial succession. Adoption still requires the existing 35-day transition. Monthly pooling continues separately. Only discretionary advances consume the remaining quarterly headroom. Existing-save migration does not erase already recorded spending. Account statements distinguish the last monthly settlement from additional essential advances since it.

Native Works development AI adds 70 willingness at 20,000 treasury. A fully paid matching development grant now provides that same bonus below 20,000. The insertion precedes native trait/culture/war multipliers, so native zeroes still apply; it does not waive eligibility, cost, site selection or approval. One eligible AI project proposal may enter the queue each monthly review, replacing one random office per quarter. Each office still respects pending requests, unreturned funds, earmarks and its allowance cooldown. Marshal is included when eligible for a native project.

Grand Marshal still needs real upfront recruitment/size-expansion funds and ongoing raised/unraised/reinforcement costs. The native Marshal contract preserves its military income and its -50% recruitment and maintenance modifiers. Cash does not itself grant extra regiment slots. Existing supplementary provision remains the route for recruitment purchases; current maintenance is covered by the essential service buffer. No regiment cap, unit price, troop creation effect or native AI military-budget define was changed.

## Dev.50-51 corrections after in-game reports

The dev.49 engine log exposed invalid localization scope syntax, non-numeric AI base weights, an inline scripted-effect argument which broke compilation of the initiative driver, a character/title heir-scope mismatch and missing durations on decaying opinions. These source errors are corrected. Live reload also exposed an unsupported tooltip trigger wrapper during this fix; it was replaced with native custom-tool-tip predicates. Regression checks now cover these exact forms.

Request/result letters are shorter; detailed rules remain in tooltips. Large-expense supplementary requests are available through Decisions for all nine ministers. New-project funding and contributions to existing projects have distinct entry points; an empty contribution menu is hidden.

The account overview uses direct current-state localization for bank cash, programme and authority. All nine departmental accounts share one compact event, with an explicit refresh action. Administrative safeguards moved off the overview. Rows distinguish cash from approved targets and do not disguise absent/shared/unreviewed accounts as zero. The last monthly statement records verified collections and operating advances, separately from current balances and other grants. Opening/closing snapshots remain saved for inspection. Statement figures are not silently recalculated by viewing accounts.

Rendering and engine behavior after a full restart still require the focused in-game checklist. This report does not claim that the user's HUD/character stock discrepancy is resolved: native source uses the same GetTreasury getter in both, and no fresh post-transfer save was available for inspection.

## Cash and operating provision

Revenue's title-linked native treasury holds the common fund. The roster is Chancellor, Censor, Grand Marshal, Personnel, War, Rites, Works, Revenue and Justice. Office authorizations belong to titles; active event leases belong to current reviewers.

Native budget distribution continues. Supported individual ministry-budget contracts normalize to Medium, while Grand Marshal's distinct military income is preserved. The module collects actual surplus and does not add matching income or charge the emperor again.

The first pooling follows a **35-day adoption period**, allowing the native ledger to settle. The greater of opening and settled recurring-cost observations establishes the initial provision. Paid legacy benefits remain; uncommitted dev.48 proposals close.

Recurring expense is derived from native monthly treasury income minus native monthly treasury balance. The working target is two months of the greater of approved and currently observed costs plus 25/75/150 discretionary headroom and any supplementary provision. Essential shortfalls are checked weekly and during monthly reconciliation. Essential shortages share available money proportionally before discretionary buffers. Only discretionary advances use the quarterly headroom cap. A review cannot reset already issued discretionary advances.

Material cost changes are considered monthly, with a 90-day office review interval. New hiring/recruitment cost changes still prompt review; existing native bills receive essential service while that review is pending. Supplementary provision covers large irregular public expenses: its editable advance temporarily increases the working target for 90 days. It does not convert personal-Gold bills into public expenses.

All actual module transfers use one native payment boundary with positive matching debit/credit checks. An uncertain result holds affected accounts and is not automatically retried or described as paid.

## Projects and earned benefits

Project starting grants precede the native affordability check. They bind the office, project type and intended senior jurisdiction. Contribution allowances bind an exact existing project and consume each contribution's native cost. Imperial ownership does not make the emperor the payer when a minister is the founder/contributor.

Bridges cover **19 installed project definitions and 152 treasury contribution expressions**, including ministry work, walls, barracks and disaster projects. Native eligibility, Influence, construction time and rewards remain. Source manifests reconstruct each override from its original plus explicit insertions.

An office may receive one project/contribution allowance per **90 days**. Contribution prices differ: the initial base quote is an editable ceiling, not a promise to finance every stage. The selector has real pages when more than three projects exist.

Uncommitted returns reconcile actual cash above operating needs. When the custodian is unavailable, reconciliation waits and another advance is blocked. Cancellation does not reset the grant interval. Revenue's own authorization reserves existing cash internally; no self-payment occurs.

Census insurance and debt-purge payments retain their native **1,000-treasury** benefits. Supported Chinese payments become durable earned claims. They wait for real cash after protected operating needs, reserve money against optional grants, and have no new approval popup or ordinary proposal expiry. Native coverage/debt benefits take effect only after successful settlement. Native behavior outside the supported Chinese branch remains, with common Revenue custody excluded as an unrelated foreign payer.

Senior civilian treasury requests use the common workflow. Explicit successful debt clearance retains native creditor Influence/hook credit while the creditor still holds the office. A partial grant which leaves debt does not create the clearance hook. The custom petition uses native medium Influence cost and offers debt clearance.

War's automatic advance accounts for the native AI requirement of more than 1,000 treasury (a 1,200 minimum request). Marshal recruitment provision can be sought in peace when native regiment slots remain open. War's native requests and proactive military debt assistance remain available from its approved local public provision; it can seek a supplement for larger obligations. Direct unreviewed gifts/demands cannot use pooled offices as an alternative allocation route. The native Siphon Treasury scheme remains separate; no custom judicial loop was restored.

## Authority, AI and interruptions

The existing fiscal laws now assign control rights: emperor control, Chancellor supervision or ordinary Revenue delegation. Numbered artwork stays 1/2/3. Native overall budget laws/proposals remain active.

Programmes change protected cash and approval rights, rather than only AI weights. Recovery can use its specific relief provision; optional projects require a superior under Recovery/Reserves. An imperial programme override remains reserved until withdrawn.

AI uses bounded personality/relationship preferences for operating targets and grants. Genuine need, law and cash constrain choices. Compassionate refusal stress applies only to an affordable recovery need; Vengeful funding stress applies only to a real discretionary increase for a rival. Public spending is not automatically personal-spending stress for Greedy or dishonesty for Honest.

Optional quarterly recovery/military initiatives are bounded; a separate project initiative is bounded monthly: at most two recovery cases, one military supplement and one reserve contribution. Imperial shortage proposals have an annual throttle and use the actual shortage, bounded by 1,000 treasury and the imperial reserve. Routine transfers have no popup.

One actionable file is leased per reviewer. Recovery has priority; deferral lasts 30 days and ordinary proposals expire after a year. A material cut/refusal permits one appeal in six months, with eligible AI appeals. Higher-authority allocations use the same cash guards without requiring custodian consent.

Office identity, law, stage and generation are checked again at commitment. Title changes wake the queue between monthly settlements. Stale windows have an exit and cannot cancel a newer generation. Earned claims survive imperial succession; ordinary proposals tied to the former emperor become invalid.

## Source boundaries and verification

- `mam_revenue_common_*`: cash, queue, AI, claims, returns, menus, events, previews and localization.
- `zz_mam_revenue_common_*`: audited native project/spending/insurance bridges.
- Old dev.48 definitions remain for saved-event compatibility; old UI/drivers are disabled.
- Personnel appointments, honors, service and candidate-score files are unchanged.
- No custom currency, register window, trade system, campaign combat subsystem or Censor-Justice runtime.

Run `tools/verify_revenue_source.py` and `tools/verify_common_fund.py`. The latter verifies protected hashes, native parity, scopes/parameters, transaction boundaries and accounting examples. It writes `COMMON-FUND-VERIFICATION.json`.

`tools/build_common_fund.py` deliberately regenerates the module; it is not a startup action. Do not import/rerun it casually after manual edits. Review native changes before rebuilding for another game version or conflicting project override.

Shared custody uses real transfers and operating buffers, not an engine account alias. There is no universal native pre-spending veto. Hiring, recruitment, activities and native theft retain their own controls. Treasury buckets, mixed ministerial/territorial holdership, timing, callbacks, rendering and AI balance require the [in-game tests](COMMON-FUND-TESTING.md).
