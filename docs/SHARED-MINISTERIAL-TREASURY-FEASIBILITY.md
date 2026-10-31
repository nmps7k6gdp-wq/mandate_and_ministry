# Shared ministerial treasury: feasibility audit

Reviewed: **2026-10-28**, installed CK3 **1.20** files, mod baseline **dev.48**.

Status: **Investigation only. No treasury merger, government override or new payment bridge implemented. No engine proof performed.**

## Requested model

The emperor retains a separate imperial treasury. Chancellor, Censor, Grand Marshal, Personnel, War, Rites, Works, Revenue and Justice share one ministerial fund. Provincial governors and personal gold remain separate. This is a different proposal from making every ministry spend directly from the imperial treasury.

## Verdict

Revenue custody is now the user's preferred working direction. The automatic funding mechanism still needs proof; see the [common-fund gameplay proposal](REVENUE-COMMON-FUND-DESIGN.md) and [Tang/Song historical comparison](FISCAL-DESIGN-OPTIONS.md).

**A common ministerial financing pool is scriptable using a real existing treasury and native transfers. A literal shared native account for nine independent officeholders is unconfirmed: the inspected exposed schemas provide no account-alias or third-party payer setting.**

The practical candidate is the Revenue office's title-linked public treasury as custodian of the ministerial fund. Other ministries would receive automatic operating advances so the engine can pay their native charges. Their local balances would become controlled operating buffers, not independent departmental savings. They would still physically exist in the native engine and its UI. This candidate requires a small engine prototype before it can be called a working replacement.

Copying the same balance into nine treasuries would create nine spendable balances. Showing one common number in nine windows would not redirect the underlying charges. Neither constitutes an account merger.

## What the installed files establish

Native root: `C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game`.

| Finding | Native evidence | Consequence |
|---|---|---|
| Treasury is a native public resource and follows the title on succession | `localization/english/dlc/tgp/dlc_tgp_china_game_concepts_l_english.yml:101` | A ministry title can serve as the fund's institutional custodian; it must remain distinct from the holder's gold. |
| Government rules enable treasury and substitute it for specified state expenses | `common/governments/_governments.info:107`, `:214` | These settings do not document an alternative treasury-owner selector. |
| Native treasury transfers have explicit payer and target characters | `common/character_interactions/10_tgp_interactions.txt`, Demand/Give Treasury | Funds can be pooled and advanced through actual conserved transfers. This does not redirect every native expense automatically. |
| Court-position salary uses the employing ruler's context; received salary may use a different currency/amount | `common/court_positions/types/_court_positions.info:148`, `:159`; `00_celestial_court_positions.txt:2028`, `:2056` | The schema supports employer treasury to employee gold, but documents no choice of a third minister's treasury as payer. Changing the recipient's salary is not payer redirection. |
| Civil ministers receive a ministry-budget base of 1 | `common/subject_contracts/contracts/celestial.txt:647`, `:672` | Income concentration must account for native allocation and existing Low/Medium/High settings. A presumed 1-to-1 redistribution is not established. |
| Grand Marshal receives ministry-budget base 1 and military-budget base 2.5, plus maintenance/recruitment modifiers | `common/subject_contracts/contracts/celestial.txt:678-705` | Its funding has two sources. Both need an explicit treatment; military money must not disappear or be counted twice. |
| Treasury MaA has native unraised and raised/reinforcement cost parameters | `common/defines/00_defines.txt:685-687` | Removing maintenance would create free military capacity. Automatic funding must cover the actual charges, including changes in army state. |
| Ministries also have project and contribution expenses | `common/great_projects/types/00_ministry_projects.txt:4116`, `:4418` | Census creation uses treasury-or-gold; a census debt-relief contribution can pay 1,000 treasury per eligible debtor. Routine salaries and MaA are not the complete expense inventory. |

An additional identifier scan across **166 native `.info` schemas** found no `shared_treasury`, `treasury_owner`, `treasury_payer`, `treasury_account_owner` or `treasury_owner_target` declaration. This is negative evidence from the installed documentation, not proof that every engine command or future extension is impossible. No generated current-version `script_docs` API dump was available in this investigation.

## Candidate implementation

1. Keep the imperial account and provincial accounts intact. Identify the pooled ministerial custodian by office title, then resolve its current holder for each payment.
2. Consolidate ministerial income and accumulated public balances through conserved transfers. Verify native budget distribution before replacing income modifiers or budget-contract settings. Personal salary gold is excluded.
3. Reserve enough of the pool for approved recurring administration and military commitments before allowing discretionary grants.
4. Automatically advance operating funds to native employer/army accounts. Do not require a popup for each monthly salary or existing regiment. Reconcile unused advances without duplicating income or charging an expense twice.
5. Route new project grants and exceptional expenses through Revenue. Existing native interactions, projects and affordability checks must be bridged deliberately; a periodic sweep alone does not cover their behavior.
6. Expose the common fund honestly. Without a UI change, ministers' native treasury panels still show their local engine balances. A common-fund display alone cannot change native affordability checks.

The operating-advance approach is feasible in principle because native transfers and current income/balance queries exist. Correct timing, expense prediction, AI affordability and debt behavior remain engine-test requirements. Do not claim a working all-expense pool based only on the source audit.

## Approval structure

| Expenditure | Proposed handling |
|---|---|
| Existing court salaries/tasks and approved standing regiments | Automatic payment within the approved operating allocation |
| New ordinary spending within a department's permitted allocation | Automatic or Revenue approval, according to the standing rules |
| Material project grant, increased operating allocation or new recurring commitment | Revenue assessment |
| Departmental dispute or spending against fiscal priorities | Chancellor decision |
| Imperial top-up, exceptional military expansion or spending beyond delegated authority | Emperor decision |

These are proposed rules, not current implemented behavior. A common fund makes competition over resources concrete, but Chancellor priorities still need explicit allocation and review rules to have the intended political effect.

## Required engine proof before implementation approval

- Two unrelated ministries share funding through one real custodian without minting money or moving personal gold.
- Existing and newly hired court staff receive exactly one correct salary; the fund is charged correctly and native AI can still hire within its allocation.
- Grand Marshal costs are measured unraised, raised and reinforcing; both funding streams are accounted for.
- A minister can afford an authorized native project even when funds begin in the common account; rejected requests create no free project or unpaid salary.
- A depleted pool produces an explicit funding shortage without automatic duplicate grants, hidden personal-gold substitution or repeated approval popups.
- Save/reload and succession of the emperor, Revenue custodian and recipient offices preserve balances and commitments. Existing Personnel appointment logic remains unchanged.

The first prototype should cover one court salary and Grand Marshal's standing upkeep before expanding to all nine offices and all native expenses.
