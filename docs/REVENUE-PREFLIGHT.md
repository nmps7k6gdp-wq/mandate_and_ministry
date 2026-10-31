> Historical dev.44-48 snapshot. Superseded by the dev.49 [common-fund implementation](COMMON-FUND-IMPLEMENTATION.md), [expense audit](COMMON-FUND-EXPENSE-AUDIT.md), and [test checklist](COMMON-FUND-TESTING.md). Earlier runtime statements have not been revalidated for dev.49.

# Revenue: final technical and thematic review

Reviewed: **2026-10-28**, baseline **dev.44**.  
Result: **Feasible for a staged implementation after user approval. Source checks pass; engine behavior remains unproven.**  
Implementation authorization: **Granted after this review. Full source implementation is now in dev.45; the user explicitly deferred engine proofs and runtime bug fixing until all features were installed.**

The findings below record the original dev.44 preflight. Current implementation and remaining tests are tracked in [REVENUE-REVAMP.md](REVENUE-REVAMP.md).

Main plan: [Revenue tracker](REVENUE-REVAMP.md). Details: [native audit](REVENUE-VANILLA-AUDIT.md), [AI plan](REVENUE-AI-PLAN.md).

## Confirmed foundations

Twenty focused source assertions passed across native payment, contract, callback and AI definitions plus existing shared ministry interfaces. These verify the definitions and their scope, not a running custom system.

| Foundation | Result |
|---|---|
| Treasury transfers | Demand/Give Treasury use `pay_short_term_treasury` with the donor as payer and an explicit recipient. |
| Individual ministry budgets | Native Low / Medium / High settings exist. They require the primary title to use the normal ministry appointment law. |
| Contract changes | The native administrative contract interaction uses `vassal_contract_set_obligation_level`. |
| Recurring initiative | Yearly and quarterly playable callbacks are documented; additive module callbacks are viable. |
| Existing interface | The Ministry category and title/council-seat synchronization query already exist. Reuse them read-only. |
| Native AI limitations | Request cooldowns and AI-disabled manual budget suggestions are confirmed. Native automatic budget maintenance also exists. |
| Removed systems | Old case-recording hooks are empty compatibility definitions. They cannot provide Revenue functionality. |

## Corrections and implementation rules

1. **Grand Marshal is a special case.** Its native succession law differs from the normal ministry law. The normal ministry-budget setting does not establish support for changing its budget. Ordinary implementation targets eligible civilian ministries; upper-office or military transfers require explicit imperial authority. Do not change military budget mechanics to force compatibility.
2. **Provincial allowance is not tax remission.** `celestial_treasury` changes treasury received from the liege. It does not directly reduce taxes remitted upwards. Extra remittances use proven public transfers; recovery uses verified grants/allowances. Any genuine tax remission must first prove its effect and recipient path, particularly for nested kingdoms.
3. **Budget changes are not guaranteed equal redistribution.** A Low setting in one department cannot be presented as an exact transfer to another. Prove total allocation behavior before promising a balanced reallocation. Use explicit transfers for exact contributions.
4. **The native AI fallback is random annual, not quarterly.** The earlier audit misread its enclosing callback. It is inside `random_yearly_playable_pulse`. The new module's own quarterly driver is a separate, deliberately planned mechanism.
5. **Native requests need a real integration point.** They currently validate/pay from the recipient's treasury, with a five-year interaction cooldown, additional AI cooldowns and native rewards. Appending a callback after payment cannot prevent the old debit. Use a narrowly scoped mod-side bridge for supported civilian requests; preserve unaffected native branches and do not erase global cooldowns indiscriminately. Before that bridge exists, reserve guarantees apply only to our custom transactions.
6. **Identify the account as well as the person.** Check office title, current holder, primary title, treasury availability, council-seat synchronization and realm. Same-account transfers are invalid even if displayed office labels differ. Unsupported mixed/temporary ownership waits or is excluded; Revenue never repairs it by transferring titles or vassals.
7. **Authority is not automatically supplied by a payment command.** Code can move funds, so our checks must enforce the mandate. Emperor sets limits; Chancellor owns fiscal priorities; Revenue selects allocations within them. Revenue may recommend changing policy at its annual review, not overwrite the Chancellor. Self-benefiting allocations and changes affecting the approving Chancellor's own ministry go to the emperor. Missing required approval means no payment.
8. **Preserve newer decisions.** Future-funding settings remain until a subsequent authorized review/native edit. Do not add automatic expiry that restores an old contract over a newer player decision. Any later temporary contract feature needs its own proven edit-detection strategy.
9. **Native consequences may already exist.** Low Ministry Budget includes native subject opinion; requests/debt assistance already award relationship, Influence, Merit or catalyst effects. Count them before adding targeted Revenue credit. No rewards for browsing, annual attendance, rejected requests or failed transactions.
10. **Do not promise global reserve locks.** Our checks protect our transfers. Other native spending still exists. Recheck the current balance, outstanding authorizations and holders at commitment; refuse stale/unaffordable actions rather than creating money or taking personal gold.

## Authority and lifecycle to implement

- Routine measures require an explicit active mandate and remaining capacity. Without one, Revenue can propose, not compulsorily debit other offices.
- A donor's voluntary acceptance or an applicable compulsory authorization must be recorded. Human voluntary choices cannot be made by AI. Disputes go to the appropriate superior; upper-office/military measures remain reserved to the emperor.
- One durable request identifies donor office, beneficiary office, purpose and amount. Bind the actual people again on presentation and commitment; a changed holder requires fresh validation/confirmation.
- Use one native payment call through one commit helper. Record completion and apply consequences only after the payment result is established. Never retry a possibly paid case simply because its later notification failed.
- Keep incomplete, returned, cancelled and completed outcomes distinct. No answer is never consent. State survives save/reload without resetting cooldowns or creating a fresh queue for the same need.
- Store Revenue's persistent realm state independently of the emperor's changeable primary title. Use the existing Chinese realm identity, separate Revenue records and bounded pending-work maintenance.
- Keep Personnel succession, custody, candidates, scores, tasks and appointment events untouched. Do not reuse its death-specific vacancy trigger as a general fiscal eligibility check.

## First engine proofs after approval

These are initial implementation gates, not reasons to claim the feature already works:

| Proof | Must establish before expanding |
|---|---|
| One guarded contribution | The intended public account loses the exact sum, the intended recipient receives it, personal gold is unchanged, native budget buckets behave as expected, and insufficient/stale/repeated actions fail safely. |
| One eligible budget change | The correct contract setting changes, monthly receipts and total allocation are measured, unrelated obligations survive, and a later native/player change remains respected. Grand Marshal is excluded from this proof. |
| One complete autonomous cycle | A real need is discovered without clicks; AI creates/decides the proposal; a lawful payment resolves once; human reserved decisions remain interactive. Include save/reload and a holder change while pending. |

If a proof fails, keep that route unavailable and adapt the implementation. Do not compensate with unmatched treasury creation, a global rewrite of native finance or changes to Personnel.

## Thematic judgment

The focus on contributions, public allocations and provincial bargaining is appropriate historical inspiration. Zhang Yibing's research describes early Northern Song fiscal planning, the administrative strain of excessive centralization, and a shift toward circuit-level contributions and greater regional autonomy. This supports our senior-office focus and standing policies. [Zhang, 2024](https://academic.hep.com.cn/fhc/EN/Y2024/V19/I2/181).

This is a CK3 abstraction, not a claim that the same Ministry of Revenue controlled every treasury throughout all Tang/Song periods. The imperial mandate, Chancellor oversight and protected ordinary operations give fiscal power meaningful limits.

Use the language of appropriations, extraordinary contributions, recovery allowances and petitions. Present public money separately from personal gifts. Avoid implying that being poor proves dishonesty, that unspent funds are always idle, or that paying a governor guarantees a project was completed.

Revenue funds and negotiates; Works executes projects; Personnel chooses officials. Military command, tactical supply bonuses and the retired judicial loop remain outside this revamp. Annual Revenue reviews provide decisions within the existing hierarchy without forcing unnecessary expenditure.

## Verification limits

- Twenty source assertions passed after correcting the native fallback's enclosing scope.
- Hash comparison confirmed **160 existing gameplay/asset/descriptor files unchanged** during this review.
- Native references, module boundaries and document links were checked. Historical interpretation uses the cited original research article's abstract.
- No running-game tests, observer balance tests, visual QA or custom transfer/contract proofs have been performed. Initial numeric tuning remains implementation work.
- The original preflight changed documentation only. The later dev.45 implementation adds isolated Revenue files and advances the local descriptor; vanilla files remain unedited.
