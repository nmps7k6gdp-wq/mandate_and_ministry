# Revenue: complete workflow review

Reviewed **dev.52**, **2026-10-29**. This is a source audit and redesign specification. The proposed replacements are **not implemented** by this review.

**Follow-up:** dev.54 corrects the character-price/title-scope mismatch in project authorization checks and exposes individual grant failures. It also prepares paid AI project reserves in the native long-term budget, subject to engine verification. Dev.53 corrects the specific Strengthen Capital governor-jurisdiction blocker reported after this audit. The remaining replacement lifecycle is still a specification. The accompanying inventory remains the historical dev.52 source snapshot.

Scope: Emperor, Chancellor, Revenue, other ministers and governors; every Revenue decision, interaction and event; cash, approvals, queueing, projects, native compatibility and interruptions. Personnel gameplay is outside the rewrite.

The inventory covers **50 Revenue source/localization files**, **7 custom decisions**, **7 custom interactions**, **3 native interaction overrides** and **21 common-fund events**. Another **25 legacy front-end/event definitions** are classified separately. Exact IDs, option text, visibility rules, source lines and hashes are in `REVENUE-WORKFLOW-INVENTORY.json`.

## Main finding

The system has payment processing, but lacks a complete expenditure lifecycle. Approval, a cash transfer, a reserved allowance, a planned project and a project under construction are different states. Current events often stop at the transfer and describe too little of what must happen next. More AI willingness cannot repair a missing execution step.

## Findings and priorities

| ID | Priority | Finding | Required correction |
|---|---|---|---|
| F01 | Critical | A successful project payment sets an earmark but has no explicit native planning handoff. The common module contains no `plan_great_project` execution. | Approve a concrete project order, execute it through native checks and record the resulting project instance. |
| F02 | Critical | Starting grants cover the planning price. Treasury contributions are separately gated to a matching allowance; there is no automatic AI contribution-request path in the initiative driver. | Budget the intended starting package and route later contribution invoices under the same project order. Distinguish planned from constructing. |
| F03 | Critical | One project slot belongs to the office. When its reserved cash reaches zero, a later starting grant can replace `mam_cf_project_instance` even though the previous project is active. | Allocate by project order/instance, not by one mutable office slot. Zero remaining cash must not erase project identity. |
| F04 | High | Native AI has short-term, long-term and war-chest budgets. Native examples explicitly move money between them before projects. The common module models total treasury but does not prepare project budget liquidity. | Verify budget-category behavior in the engine, move existing cash into the appropriate category when executing an authorized invoice, and verify unchanged total cash. Do not invent money. |
| F05 | High | Project earmarks normally prevent a routine sweep, but completion/cancellation callbacks clear protection; annual expiry clears it even if a project is still active. Ordinary sweeps later determine actual returns. | Tie protection, expiry and return to each authorization's state and actual remaining cash. Show a deadline and a return result. |
| F06 | High | Entry points use different identity tests: some use the looser ministry-member trigger while execution requires synchronized ministry/council identity. | Use one eligibility contract from visibility through execution. Explain temporary custody or an unsynchronized appointment before accepting a request. |
| F07 | High | Native gifts/demands/debt actions involving pooled ministries are blocked, but there is no replacement general common-treasury payment interaction. | Add one public-treasury payment flow, routed through the fiscal law. No personal-Gold fallback. |
| F08 | High | Weekly service covers currently observed bills outside discretionary caps. Native hiring/spending cannot be universally vetoed; this can fund an unapproved expansion without identifying the exception. | Preserve solvency, record new spending variances, and route material changes for review. Describe the actual limits of fiscal authority. Routine payroll must not become an approval popup. |
| F09 | Medium | Supplementary funding exists as both a decision and interaction. Accounts lead through several menu events. | Give each action one principal entry point and use contextual follow-up actions in accounts. |
| F10 | Medium | Resume Fiscal Papers clears all cases' snoozes, not only the caller's papers. | Reviewers recall only their own deferred cases; automatic queue recovery remains hidden maintenance. |
| F11 | Medium | One result letter is reused for approvals, reservations, transfers and failures. It is sent back to authorizers as well as requesters. | Show the actual state and next action; notify affected players once. Avoid confirming the same decision back to its author. |
| F12 | Medium | An AI imperial top-up cooldown is set when the proposal is made. A denied proposal can suppress automatic reconsideration for a year despite a materially different shortage. | Separate proposal, refusal and successful-allocation cooldowns; permit bounded reconsideration after a material change. |
| F13 | Medium | Project candidates are selected by a broad jurisdiction first; project-specific location tests come later. A jurisdiction can contain no valid site for the chosen project. | Select and validate an exact native site before presenting the final funding proposal. |
| F15 | Critical; corrected in dev.54 | Character-price helpers were evaluated inside title scope, losing minister discounts and potentially rejecting a correctly funded starting/contribution grant. | Cache the native price in character scope before checking the title-stored grant; verify native price fixtures and actual engine behavior. |
| F16 | Critical; design pending | A new starting grant sets the same 90-day timestamp that blocks contribution allowances, including required continuation. | Separate new-work throttles from invoices on an existing approved project. |
| F17 | Critical; design pending | Grand Campaign's required Marshal pledge gates other native pledges and can initiate war, but it has no dedicated automatic launch-funding path. | Approve a campaign launch package, fund the proper native contributor, preserve military authority and verify native war execution. |
| F14 | Medium | Source tests check symbols, accounting examples and parity, but do not demonstrate a project planning, funding its required contributions and entering construction. | Add an end-to-end engine acceptance test for each supported project family. Keep source verification claims separate. |

F01-F03 and F05-F13 are demonstrated source behavior/gaps. F04 establishes that native budget categories exist and are used; their precise contribution to the reported stalled projects still needs an engine test. F14 is a verification limitation, not evidence that every native project fails.

## Current decisions: retain, merge or replace

| Current decision | Current owner | Review disposition |
|---|---|---|
| Examine Common Accounts | Emperor, Chancellor, Revenue, ministers | Retain one concise view; full government figures for fiscal authorities and own provision/status for other ministers. |
| Set the Spending Programme | Emperor, Chancellor | Retain. Say **Set** when the actor can decide; **Propose** when an imperial seal is required. Do not create a second approval to oneself. |
| Appropriate Imperial Funds | Fiscal authorities | Retain as a request by Revenue/Chancellor and a direct authorization by the Emperor. Always identify the imperial payer and common-fund recipient. |
| Fund a Project Contribution | Ministers | Merge into the funded project's own order. Manual and AI contributors must reach the same invoice flow. |
| Resume Fiscal Papers | Fiscal authorities | Replace with **Review Pending Fiscal Matters**, visible only when the caller has relevant matters. Recall only their own deferred papers. |
| Return Uncommitted Project Funds | Ministers | Make contextual to a particular authorization. Distinguish cancelling an unstarted order from cancelling an existing native project. |
| Request Supplementary Provision | Ministers | Keep one principal request path through Revenue; Revenue's own request goes to its superior. Remove redundant general entry points. |

## Current interactions: retain, merge or replace

| Current interaction | Participating roles | Review disposition |
|---|---|---|
| Review Operating Provision | Fiscal authority -> minister | Retain for material changes; clearly separate recurring service, discretionary headroom and exceptional purchases. |
| Request Operating Provision | Minister -> Revenue | Merge the request presentation with supplementary provision; the request must state what is changing. |
| Petition for Public Funds | Governor -> Revenue | Retain recovery/debt purposes. State payer, amount, conditions and actual remaining debt. Do not call a partial grant full debt clearance. |
| Request Provincial Contribution | Revenue -> governor | Retain consent and protected provincial cash. Bypassing imperial approval must not bypass the governor's consent to give their own money. |
| Request Great Project Funding | Minister -> jurisdiction holder | Replace broad jurisdiction-only submission with a specific project, site, starting package and deadline. |
| Appeal Operating Provision | Minister -> Chancellor/Emperor | Retain one appeal per material decision, to a superior who did not decide their own case. |
| Request Supplementary Provision | Minister -> Revenue | Retain as the primary exceptional-operating request; consolidate duplicated menus and results. |
| Native Give Treasury override | Native parties | Keep ordinary non-pooled behavior. For pooled custody, direct the player to **Arrange a Treasury Payment**, instead of leaving a dead end. |
| Native Demand Treasury override | Native parties | Preserve non-pooled behavior; common custody and voluntary provincial contributions need distinct ownership/consent rules. |
| Native Pay Treasury Debt override | Native parties | Preserve ordinary behavior outside custody. Use the common payment order when the payer is a pooled ministry. |

## Every common-fund event

| Event IDs | Current function | Review requirement |
|---|---|---|
| `.99` | Startup/adoption | Preserve migration and resume scheduling; never reset paid grants or completed receipts. |
| `.98` | Queue wake | Hidden maintenance only; no gameplay decision needed to make processing function. |
| `.90` | Present the leased file | One actionable file per current reviewer; invalidate stale generations. |
| `.1`, `.8` | Request/recommendation/payment chooser | One logical review model with role-appropriate presentation. Separate submit, approval, release and execution states. |
| `.2` | Operating review/appeal | Show the proposed difference and who may decide it. Existing payroll remains serviced. |
| `.3` | Amount editor | Editing moves no cash and takes no final-action cooldown; show payer and currently spendable money. |
| `.4` | Programme | Effects must change real envelopes/priorities. Use the same authority resolver as payments. |
| `.5` | New project chooser | Show only eligible project/site combinations. The submission is an executable order, not a vague grant. |
| `.6` | Accounts overview | Read-only refresh. Show gross cash, commitments, spendable cash and settlement timing. |
| `.7` | Existing-project selector | Select an exact instance/invoice. Do not create a second unrelated allowance slot. |
| `.20` | Result letter | State submitted/approved/reserved/paid/planned/constructing/blocked/returned accurately; identify the next step. |
| `.96` | AI project initiative | Build a valid order before seeking funds; resume its actual execution after approval. |
| `.97` | AI appeal | Respect a real material decision, one appeal and a valid higher reviewer. |
| `.9` | Explanation of money movement | Short reference text; actual state belongs in accounts and transaction results. |
| `.10` | Own-office provision | Distinguish current cash, working target, purchase reserves and recurring bills. |
| `.11`, `.12`, `.13` | All-department view plus saved-page aliases | Retain one window for all nine offices; old page IDs are compatibility aliases only. |
| `.14` | Safeguards | Show current law, temporary suspension and actor rights. Hide contradictory or inapplicable choices. |
| `.95` | Weekly essential service | Automatic, conserved and idempotent; preserve holds and report spending variances rather than disguising them as new approvals. |

## Direct answers about unused funds

- **Current dev.52:** an active `mam_cf_project_cash` earmark is included in the protected working balance. It should not be collected by the ordinary surplus sweep simply because the minister has not spent it immediately.
- It can become collectible when its authorization expires, is returned or has its protection cleared by project completion/cancellation. Timing and grant identity are insufficiently clear in the current front end.
- **Replacement design:** retain commitments in common custody until an invoice is executable; protect any advanced invoice cash until verified expenditure or explicit return. Ordinary surplus collection must never revoke a live commitment.

## Boundaries for the rewrite

Keep native overall budgets, tax tasks, unit/project prices, project eligibility, Influence requirements, project rewards and personal-Gold gifts. Keep the common fund, fiscal laws, actual recurring-cost service and appointment gameplay.

Introduce a single authorization/execution model, an explicit public-treasury payment interaction, per-project commitments and a deliberate unauthorized-release path with passive evidence records. Do not restore Censor-Justice events or punishments now. The bypass concerns required approval, not cash conservation, recipient eligibility, provincial consent or failed-payment holds.

The replacement contract is in `REVENUE-COMMON-FUND-DESIGN.md`. The full redesign remains unimplemented. The later dev.53 capital-rule correction is recorded separately and does not close the lifecycle findings.
