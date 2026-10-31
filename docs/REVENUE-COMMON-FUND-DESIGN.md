# Revenue: replacement gameplay and workflow contract

**2026-10-29. Design reviewed against dev.52. Implementation pending.**

This replaces the earlier design summary. Current behavior and source findings are documented in [the complete workflow review](REVENUE-WORKFLOW-REVIEW.md). The audit snapshot is dev.52; the current dev.54 build includes targeted capital-jurisdiction, character-price and grant-diagnostic corrections plus AI budget preparation. This replacement contract remains unimplemented.

## 1. The five roles

| Role | Decisions that matter | Principal entry points |
|---|---|---|
| Emperor | Overall native ministry budget, imperial contributions, fiscal law, reserved expenditure, government priorities and appeals above the Chancellor | Fiscal law, spending programme, imperial contribution, payment/approval events |
| Chancellor | Government programme within imperial instructions, allocation disputes, ordinary approvals under supervision and material operating appeals | Programme, review queue, ministerial appeals, temporary delegation safeguard |
| Revenue | Custody, solvency, assessment of requests, ordinary lawful releases, payment execution and an explicit choice to make an unauthorized release | Accounts, operating review, treasury-payment interaction, request queue |
| Other ministers | Seek operating purchases, propose exact projects, execute approved work, seek later invoices and appeal material cuts | Ministry interactions with Revenue, own provision and active project orders |
| Governors | Request genuine recovery/debt assistance, consent to provincial contributions and receive authorized public payments | Petition/contribution interactions and clear outcome notices |

All new interactions remain in **Ministry**. Use the **Revenue:** prefix consistently for fiscal actions. Only a role able to act sees the relevant decision. Personal-Gold gifts remain entirely vanilla.

## 2. A smaller front end

Keep global decisions for accounts, the spending programme, imperial funding and the current reviewer's pending matters. Use character interactions for recipient-specific actions. Use an existing project's order for its contribution invoices and returns.

A minister has one principal **Request Funding** interaction with Revenue. Its first choice states the purpose: an operating change, a one-time public purchase, a project order or an invoice on existing work. Contextual options can open that same flow from the minister's account or project status. They must not create competing queues, different cooldowns or different rules.

Revenue has **Arrange a Treasury Payment** on a living character with an eligible public treasury in the Chinese realm. Manual recipients may include lower-tier officials; automatic fiscal discovery remains bounded to the supported senior jurisdictions. No public treasury means this interaction is unavailable. It never changes to Gold.

The Emperor and Chancellor can originate the same payment order. The final action says **Authorize and pay**, **Pay under delegation** or **Submit for approval**, according to their actual rights. An Emperor does not approve an identical proposal to themself in a second event.

**Review Pending Fiscal Matters** recalls only matters belonging to that reviewer. Queue maintenance and lease recovery are automatic and hidden.

## 3. One expenditure lifecycle

Each order has a unique identity and purpose. Store the requester, paying office, beneficiary office/current recipient, proposed amount, approved ceiling, reviewer, law and programme, execution state, receipts and expiry/renewal conditions.

| State | Meaning | Money movement |
|---|---|---|
| Draft | Recipient, purpose, amount and any project/site are being chosen | None |
| Submitted | A complete request is waiting for its lawful reviewer | None |
| Approved and committed | Authority exists and a stated amount is reserved against common cash | Reservation only; no payment is claimed |
| Executable | Current account, identity, price and non-cash requirements pass | Exact authorized invoice can be paid |
| Paid | A verified debit and matching credit occurred | Actual movement recorded |
| Executed | The intended native action occurred, such as project planning | Native expense/action verified separately |
| Blocked | A requirement changed or funding is unavailable | Give a concrete reason and a bounded remedy |
| Refused / cancelled / expired | The order cannot make further payments | Release unused commitments and reconcile actual advances |
| Returned | Unspent advanced money was verifiably repaid, or an unadvanced commitment was released | Say which happened |

Only payment execution may move cash. Changing an amount, viewing an event, approving a ceiling and refreshing accounts must not themselves imply successful expenditure.

A general treasury grant reaches its terminal state after verified payment. A project order remains active across multiple invoices until completion/cancellation. A paid record cannot be reopened or paid again.

Recipient ownership matters. An ordinary governor's treasury is outside monthly ministry pooling, so its completed grant is not automatically collected again. A payment to a pooled ministry must carry an operating or purchase authorization: cash reserved under that live authorization is excluded from surplus collection. Revenue funding its own work is an internal authorization within the common bank, never a transfer to itself or a fabricated debit/credit receipt.

## 4. Fiscal authority with real consequences

| Law | Routine service under existing provision | New ordinary payment/project budget | Sensitive or conflicted expenditure |
|---|---|---|---|
| Imperial Fiscal Control | Automatic within standing provision | Emperor | Emperor |
| Chancellor-Supervised Administration | Automatic within standing provision | Chancellor | Emperor |
| Delegated Revenue Administration | Automatic within standing provision | Revenue within the approved programme and delegated ceiling; larger measures go to the Chancellor | Emperor |

Sensitive cases include Revenue increasing its own provision, reserved upper/military offices, conflicted reviewers and additional imperial appropriations. A Chancellor cannot adjudicate their own funding appeal. The Emperor's valid direct authorization satisfies the approval requirement immediately.

Retain the current **500-treasury ordinary delegation ceiling** as the initial balance baseline. Related instalments share an order and approved ceiling; splitting a large project into small payments must not turn it into a delegated project. A programme also bounds discretionary releases in aggregate; it must not be merely an AI preference label.

Resolve authority both at review and at payment. A law/office change reroutes an unpaid order as necessary; it does not silently give Revenue a former superior's rights. Paid historical records keep the law and authorizer that applied when paid.

Keep native overall percentage budgets as the source envelope. Common pooling does not charge that same income to the Emperor twice. Extra imperial contributions are separate, explicit payments.

## 5. Ordinary operation and exceptional purchases

Recurring native bills receive essential service. Revenue retains a buffer for actual obligations and reports material cost changes for review. Discretionary headroom is an allowance; recruitment purchases, large activities and projects need their own stated purpose and amount.

Native hiring and every native expense cannot all be vetoed through one script hook. Record an unapproved expansion as a spending variance and route it to the appropriate superior. A variance is not automatically proof of corrupt intent. The player should see how much is being serviced, why and whether a review is pending.

Grand Marshal needs cash for recruitment/size expansion as well as raised, unraised and reinforcement upkeep. A recruitment provision is separate from payroll and does not grant extra native regiment slots. War assistance uses an approved operating/purchase allocation, with no duplicate request for an already approved invoice.

Scarcity order: existing essential service, earned liabilities and contracted work before optional new ambition. Programmes change optional priorities and protected reserves. Existing known obligations appear as commitments in accounts.

## 6. Projects must be executable orders

Before submission, choose an eligible project and **exact valid native site**. Show the office doing the work, site/jurisdiction, native planning cost, required starting contributions, non-cash requirements and the requested ceiling.

For AI and player requests, the same eligibility and execution helpers apply. Once approved:

1. Reserve the approved package in common custody.
2. Recheck the exact site, actual native prices, Influence and other requirements.
3. Release only the invoice needed now; prepare the recipient's native AI budget category when needed without changing total cash.
4. Invoke the native planning action and save the actual project instance. Verify the native expense instead of charging it again manually.
5. Fund the required construction contributions covered by the approved package through native contribution actions. Label a project **planned** until its native construction state actually changes.
6. Keep later invoices attached to that instance. Within-budget instalments use the existing authority; changed scope or a higher ceiling needs fresh approval.

Every ministry may have distinct orders for distinct active projects. An exhausted balance does not erase an active project's identity or authorize spending on a different project.

**Contributions:** pooled ministries request/execute project-specific invoices against one approved shared contribution envelope. Covered required invoices do not need a fresh approval or new-project cooldown. Governors normally contribute from their own provincial funds. Grand Campaign's mandatory Marshal pledge belongs to an explicit campaign launch package: it can trigger the native war-start event, and other campaign contributors wait for it. See [the contribution and campaign contract](REVENUE-PROJECT-CONTRIBUTIONS.md) for role, budget, execution and AI details.

If requirements fail, show the actual blocked reason and next action. The initial proposed deadline for an unstarted order is **90 days**, with amendment/renewal routed under the law. A project already in progress uses its own milestone schedule; it does not lose all authorization merely because a general one-year timer elapsed.

Technical evidence: native `can_plan_great_project`, `plan_great_project`, `can_fund_project_contribution` and `fund_great_project_contribution` exist in installed game sources. Native exact-location rules must be preserved with correct founder/owner/province scopes; finding an arbitrary province is insufficient. These commands still need a complete engine test for the supported project families.

## 7. Unspent funds and returns

An approved but unadvanced project commitment remains in Revenue's bank and reduces its spendable balance. There is no reason to send that entire budget to a department immediately.

Cash advanced for an executable invoice remains protected while that authorization is live. Routine collection touches only genuinely uncommitted surplus. It cannot reclaim a valid project payment merely because it was unspent for a few days.

Cancellation, rejection of changed scope, failed execution or explicit expiry releases unused commitments. Recover only actual unspent advanced cash. Do not debit an office for money already verifiably consumed by a native project or take its payroll buffer to manufacture a refund. If account readings are uncertain, hold the disputed transaction and expose the reason.

Returns preserve the order's spending/cooldown history. They do not permit the same grant to be requested and paid again immediately.

An unauthorized payment that is later returned keeps its original evidence record and adds the verified recovery. Later investigation must distinguish gross unauthorized expenditure from any remaining financial loss. An unauthorized internal authorization for Revenue is a reservation until native expenditure actually occurs; it must not be recorded as a cash transfer that never happened.

## 8. Deliberate unauthorized release

Revenue may choose **Release the treasury funds without the required seal** when an otherwise valid payment requires approval. It is a separate, clearly marked option with a second explicit confirmation of amount, recipient and missing authority.

This bypasses approval only. It still requires real common cash, a public-treasury recipient, valid current identities, a positive amount, protected obligations and an unused transaction identity. It cannot override a failed-payment hold or force an unwilling governor to contribute their own provincial funds.

On a verified unauthorized payment, retain a passive institutional record containing:

- Actual responsible minister and office; recipient character and office at payment.
- Actual amount, payer, receipt, date, purpose and source order.
- Law/programme in force, required approving authority and the absence/refusal of that approval.
- Any actual family/friend/faction relationship used as the choice basis.

These records survive ministerial succession and ordinary request cleanup. Authorized delegated payments remain lawful and are not mislabelled corruption. Evidence records distinguish an unauthorized release from proven bribery or theft; later investigation can evaluate motive and circumstances.

No Censor-Justice event loop, automatic prosecution or new punishment is introduced now. Stress appears only for applicable actual traits/actions. AI should not bypass merely because it is Greedy when it receives no personal benefit: require a real patronage motive or exceptional public purpose, use a low bounded frequency, and prevent Honest/Just AI from routine unlawful releases.

## 9. Outcomes, accounts and AI

Use short natural letters for requests and notices, character/title links and precise tooltips for financial effects. Every review shows who pays, who receives, the amount, purpose, required seal and current state. A submission says it is submitted; an approval says it is approved; a project-start notice names the created project. Give actionable failure reasons and avoid duplicate acknowledgement letters to the player who just made the decision.

Keep all nine departmental accounts in one window. Clearly distinguish current public cash, essential working target, approved purchases/projects, common commitments, spendable balance and the last settlement. Refreshing is read-only.

AI governors petition for genuine need; Revenue assesses and releases under the same rules as the player; the Chancellor sets priorities and arbitrates; the Emperor supplies the envelope and handles reserved exceptions. Ministers propose executable work and continue its invoices after approval. Avoid proposals with no valid native site and repeated requests for the same already funded work.

Use bounded initiative discovery, one actionable matter per reviewer, and meaningful cooldowns on completed/refused actions. A newly material crisis can reopen reconsideration; a year-long proposal throttle must not silently disable needed government service. Personality alters lawful priorities and explicit misconduct choices, rather than replacing cash/eligibility checks.

## 10. Interruptions and delivery checklist

| Edge case | Required result |
|---|---|
| Several simultaneous requests | Separate orders; deterministic queue and one active reviewer lease |
| Minister or governor dies before payment | Revalidate office/current holder and any personal conditions; no payment to a stale character |
| Minister dies after project starts | Project/commitment remains institutional; new holder cannot duplicate the grant |
| Reviewer or fiscal law changes | Reroute unpaid authority; preserve completed historical receipts |
| Revenue vacancy or temporary custody | Stop unauthorized use of the Emperor's own account; explain waiting state |
| Site leaves the realm or ceases to qualify | Block/amend/cancel the specific order and reconcile unused funds |
| Two projects use one ministry | Keep separate instance identities and balances |
| Common cash becomes insufficient | Prioritize existing obligations; show shortage and seek lawful funding |
| Repeated click, deferred event or save/reload | No second debit/credit, no resurrected refusal and no duplicate project |
| Corrupt release succeeds/fails | Evidence only for actual verified expenditure; no invented loss on failure |

- [x] Full current-source inventory and workflow audit.
- [x] Replacement role, authority, payment, project and corruption-record contract.
- [ ] One authority resolver and one typed order lifecycle.
- [ ] Exact-site project execution and native contribution continuation.
- [ ] Shared contribution envelopes, automatic AI invoices and an explicit Grand Campaign launch package.
- [ ] Per-project commitments, staged advances, deadlines and returns.
- [ ] Public-treasury payment interaction and explicit unauthorized-release records.
- [ ] Consolidated role-owned front end and truthful outcomes.
- [ ] Migration of outstanding dev.52 requests/earmarks without replaying payments.
- [ ] Full native engine acceptance tests, including the user's stalled Works/Marshal projects.

Implementation is modular: accounts/cash, orders/authority, project execution, AI discovery and passive misconduct records. They share a small documented order/receipt contract. Personnel remains an external read-only dependency; later investigation reads records through that contract.
