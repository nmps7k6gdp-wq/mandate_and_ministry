# Project contributions and Grand Campaign funding

**2026-10-29. Contribution/launch design implemented in dev.55 source. Engine acceptance tests remain pending.**

Current implementation: per-project remaining budgets, native invoice execution, explicit imperial campaign launch and separate mobilization provision. See [MOD-CURRENT-STATE.md](MOD-CURRENT-STATE.md) for current contracts and limitations. This document retains the rationale and acceptance criteria; historical problem statements describe dev.54. The broad initial-project planning redesign is not declared complete.

## What is currently broken

Ministries still have native public accounts, but pooling leaves them with operating buffers instead of large independent reserves. Governors retain their provincial funds. Their voluntary native contributions do not need to be financed by Revenue by default.

The current common-fund contribution guard requires the ministry's one project slot to match the exact project and retain enough unspent allowance. The AI initiative driver does not create contribution-allowance requests. The same 90-day gate used after a starting grant also applies to contribution requests. A project can therefore be planned and then lose its funding path immediately, including for mandatory contributions.

The replacement must preserve who contributes and the native participation/reward rules while changing the source of ministerial money.

## Who pays

| Participant | Default source | Revenue involvement |
|---|---|---|
| Pooled ministry | Common fund, through a project-specific authorized contribution | Automatic request discovery for AI; a player can choose an exact contribution through the funding interaction |
| Governor | Their own provincial/native funds | Vanilla participation continues. Seek extra public funding only for a specifically approved assignment or genuine inability to meet a required obligation |
| Emperor | Own imperial treasury for personal imperial contributions; common fund when explicitly authorized | Clearly identify which account is paying; never charge both |
| Grand Marshal's required campaign pledge | The campaign's approved common-fund launch package | Mandatory priority; attached to campaign authorization, not ordinary discretionary pocket money |

## One budget, several contributors

Approve a **project contribution budget**, including required contributions and any optional departmental share. The fiscal law chooses the reviewer of this envelope. Revenue releases covered invoices within it without returning every small pledge to the Emperor.

Each invoice names the actual project instance, native contribution slot, contributing office, eligible current contributor, actual native treasury price and source authorization. Distinct ministries share the same government's remaining project budget. They do not each receive a fresh copy of the whole ceiling.

An optional pledge outside the envelope creates a request for an increase or another lawful allocation. It is not automatically paid because a ministry wants its native reward. Related pledges cannot be split to evade review thresholds.

Required follow-up invoices are continuation of existing authorized work. A cooldown on proposing a **new project** must not block them. If the approved ceiling is insufficient, request a clearly identified amendment instead of leaving the native button unexplained or disabled indefinitely.

## Contribution execution

1. Discover an unfunded native slot and assess the prospective contributor's non-financial eligibility. Do not require the ministry to possess cash or a previously paid allowance just to request that allowance.
2. Quote the native price in the actual contributor's character scope, retaining their discounts and requirements.
3. Check the existing authorization, remaining shared envelope and any required fiscal/launch approvals. Queue one decision only if new authority is necessary.
4. Release the exact required treasury into the contributing ministry's native account, or use an authorized internal reservation for Revenue's own contribution. Protect advanced funds until execution/return.
5. Recheck native eligibility and fund the exact native contribution with the correct contributor. Native execution charges the contribution price; do not manually charge it again.
6. Verify the native slot's funded state and cash result. Preserve native contributor credit, cooldowns, Influence requirements, participation and rewards.
7. Close the invoice once. If native execution becomes impossible, reconcile the unused advance and explain the blocked/returned state. Never replay a paid or already funded slot after reload.

The system should execute the chosen contribution after authorization for both player and AI. Funding approval should not leave the player searching for an unexplained second permission. Optional player contributions require their choice; an AI minister can act within its standing mandate and personality preferences.

Revenue finances the contribution but does not become every project's contributor. In particular, paying as Revenue instead of the actual Marshal would not satisfy the native mandatory campaign pledge.

## Grand Campaign is a launch order

Verified native behavior:

- The mandatory contribution is `attack_1`.
- Its contributor must hold `e_minister_grand_marshal`.
- Its treasury price is the contributor-scoped `great_project_base_contribution_cost`; do not assume a fixed amount.
- Other campaign pledges require `attack_1` to be funded. Their lack of participation can therefore be caused by the missing Marshal pledge, even when those governors have money.
- Funding a campaign contribution invokes `grand_campaign_contribution_effect`. When the native target/defender checks require war, it triggers `tgp_china_ministry.0001`, whose immediate block starts the native Grand Campaign war. This is not merely a passive donation.

The proposed launch package includes:

| Item | Handling |
|---|---|
| Native project planning price | Fund and verify once |
| Marshal's mandatory pledge | Reserve with the campaign authorization and execute promptly once launch is authorized |
| Initial mobilization/operating reserve | Separate stated provision based on actual native needs; never spend payroll to fund the pledge |
| Optional departmental pledges | Covered by an approved contribution envelope or a bounded amendment |
| Governors' voluntary pledges | Native eligibility, willingness and their own provincial funding remain |

Use one explicit **Authorize and finance this campaign** decision under the Emperor's reserved military authority. It must say that releasing the mandatory pledge can initiate war. A generic fiscal payment or delegated small-payment ceiling is not a military launch mandate. Revenue may execute a lawful campaign allocation; it does not independently choose an offensive war by funding a convenient small invoice.

For an already planned campaign with no adequate launch allocation, create one priority launch-funding request. An AI Marshal automatically seeks the missing required pledge; it must not wait for discretionary spare cash or a new-project cooldown. An AI Marshal executes an authorized launch. A player Marshal receives an explicit launch/contribution action and any concrete blocker, rather than a silent failure.

If the Marshal's office is vacant, the target has changed, a defender is no longer valid or funds are genuinely insufficient, show that condition and wait/amend/cancel the relevant order. Preserve native war leader, casus belli, participants, target handling and war events.

An optional future unlawful fiscal release remains an expenditure/evidence issue. It must not silently grant separate military launch authority; deliberately initiating an unauthorized campaign would require a distinct, explicit design.

## AI and popup limits

Prioritize missing mandatory invoices on already authorized projects. Optional pledges use a bounded initiative check and real native contributor eligibility. Personality can affect optional participation; it cannot leave an approved campaign's mandatory funding dependent on an unrelated surplus threshold.

Use one queued approval for an envelope or material amendment. Covered invoices run automatically with concise results/status. Do not create one imperial approval event for every ministry and every governor. Governor donations remain voluntary and native; routine discovery should not turn every low-tier participant into a new unsolicited fiscal petition.

## Implementation and acceptance checks

- [x] Replace the new contribution entry point with project/invoice-specific commitments; retain already paid legacy allowances.
- [x] Separate new-project cooldowns from continuation invoices.
- [x] Add automatic AI discovery/request/execution source for eligible contributions.
- [x] Add a shared contribution envelope with law-based approval and bounded amendments.
- [x] Add explicit imperial campaign launch, separate mobilization provision and priority Marshal pledge. Initial planning price remains the existing separate starting grant.
- [x] Preserve native governor contributions and actual contributor reward source; verify in engine below.
- [ ] Test a minister contributing to a project founded by another minister.
- [ ] Test two projects and several contributing ministries without duplicate grants or overwritten identities.
- [ ] Test starting grant followed immediately by a mandatory contribution, with no 90-day obstruction.
- [ ] Test an approved Grand Campaign from planning through Marshal pledge, native war start and governor participation.
- [ ] Test refusal, vacancy, changed target, insolvency, cancellation and save/reload without duplicate pledges or war events.

Native references are read-only under the installed game's `game` folder: `common/great_projects/types/00_ministry_projects.txt` (`grand_campaign_project`, `attack_1`); `common/scripted_triggers/10_tgp_dynastic_cycle_triggers.txt` (`grand_campaign_valid_contributor_trigger`); `common/scripted_effects/10_dlc_tgp_scripted_effects.txt` (`grand_campaign_contribution_effect`); `events/dlc/tgp/tgp_china_ministry_events.txt` (`tgp_china_ministry.0001`).
