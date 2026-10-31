# Existing Revenue features and ministry expenses

Read-only installed-source audit, **2026-10-28**, updated for **dev.52**. Vanilla files were not edited.

## Keep, adapt or retire

| Existing feature | Treatment |
|---|---|
| Collect Taxes and native Steward task effects | **Keep.** No replacement taxation system, quota audits or fiscal candidate score. |
| Emperor's salary/ministry/military percentage budgets | **Keep.** They remain the overall funding controls; the same income is not created again. |
| Revenue's native budget proposals and imperial response | **Keep.** They still change the overall native budget. |
| Individual Low/Medium/High ministry allocation | **Retire as an allocation authority.** Supported contracts normalize to Medium; working balances replace these allocation choices. Marshal's distinct income/contract remains. |
| Old custom inter-ministry transfers and recipient markers | **Retire.** Surplus goes to common custody; payments name the actual payer. |
| Civilian treasury requests and debt clearance | **Adapt.** Common funds, current authority and real receipts; successful explicit clearance retains native creditor credit. |
| Native military requests and War debt assistance | **Keep within provision.** War uses its approved operating funds and can request a supplement. |
| Revenue's direct treasury gifts/debt payments | **Adapt.** Custodial cash requires the common route. |
| Provincial remittances | **Adapt.** Affordable voluntary contributions have consent, reserve protection and cooldowns; distressed provinces are exempt. |
| Census and native great projects | **Keep and fund.** Starting grants precede native charges; contributions have a project-specific ceiling. Eligibility, Influence, duration and rewards remain. |
| Census disaster insurance | **Keep and adapt.** Native payout is 1,000 treasury; an earned Chinese claim waits for common cash instead of adding a new fallback payment. |
| Census debt-purge payments | **Keep and adapt.** Additional native 1,000-treasury payments become earned claims instead of an uncontrolled completion debit. |
| Revenue's native disaster tax relief | **Keep.** Removing native tax burdens is not a new invented treasury expense. Works retains native recovery work. |
| Siphon Treasury scheme | **Keep separate.** No restored custom Censor-Justice system. |

## Allocation follows the actual expense

| Office | Recurring provision | Large/irregular expense |
|---|---|---|
| Chancellor | Actual court/task treasury costs | Supplementary provision; native eligible contributions. |
| Censor | Actual native treasury costs | Native eligible expenses/contributions; no new custom Censor gameplay. |
| Grand Marshal | Court costs and native standing/unraised military costs | Recruitment at the native unit price, grand campaigns and eligible military construction. New maintenance prompts review while essential bills remain serviced. |
| Personnel | Actual court/task treasury costs | Native eligible supplements/contributions; appointment/service gameplay unchanged. |
| War | Court/task costs and approved operating provision | Native military aid/debt, troop projects and eligible construction; supplements for larger costs. |
| Rites | Actual court/task treasury costs | Culture/religious projects and contributions. An examination participant/portrait role does not make Rites the host/payer. |
| Works | Actual court/task treasury costs | Development, eligible barracks/walls/canals, disaster contributions; native starting and stage costs are separate. |
| Revenue | Own operating authorization within the common account | Census requires a superior; insurance/debt liabilities are earned institutional claims. |
| Justice | Actual native court/task treasury costs | Native control projects/contributions; no removed custom prosecution loop. |

Ordinary provision is not an equal fraction of income. It covers the greater of approved and currently observed native recurring expenses; discretionary headroom is separate. Project/supplement authorizations address large costs separately. Their actual affordability and timing still need engine checks.

Important findings:

- Native proactive debt aid requires the AI payer to hold more than 1,000 treasury. War's automatic supplementary request therefore uses at least 1,200, subject to the real fund and imperial approval, rather than an ordinary 75-treasury buffer.
- Grand Marshal can seek recruitment provision in peace when native regiment slots remain open; it need not wait for a war to build its force.

- Emperor-owned projects can charge their ministerial founder/contributor.
- `imperial_examination` explicitly charges its **host** treasury, including the AI `on_start` path. Rites appearing in the activity does not move that invoice to Rites.
- Court-position salaries and army bills use the native employer/owner. The module derives treasury expense from native income minus balance rather than guessing an equal bill for each ministry.
- Personal-Gold activity costs remain personal; a public advance does not change their currency.
- Census debt-purge payments are additional obligations beyond the visible contribution price. Insurance's native 1,000-treasury value is also substantial. Both are retained and accounted for as claims.

## Installed reference map

Paths below are relative to `C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game`:

- `common/council_tasks/00_steward_tasks.txt`: taxes/tasks.
- `common/subject_contracts/contracts/celestial.txt`: ministry/Marshal income and maintenance.
- `common/laws/02_admininistrative_laws.txt`: overall budgets.
- `events/dlc/tgp/tgp_china_ministry_events.txt`: budget advice/approval.
- `common/character_interactions/10_tgp_interactions.txt`: requests, gifts, demands and debt.
- `common/great_projects/types/00_ministry_projects.txt`: ministry costs/Census debt purge.
- `common/great_projects/types/00_great_project_types.txt`: barracks, walls, canals and capital work.
- `common/great_projects/types/00_natural_disasters.txt`: disaster projects/contributions.
- `common/great_projects/types/01_pam_projects.txt`: additional definitions present in this installed reference.
- `common/script_values/tgp_great_project_values.txt`: base costs/insurance value.
- `common/scripted_effects/10_dlc_tgp_natural_disaster_scripted_effects.txt`: insurance.
- `events/situation_events/tgp_natural_disaster_events.txt`: ministerial disaster roles/tax relief.
- `common/activities/activity_types/imperial_examination.txt`: host charges/Rites participation.
- `common/governments/00_government_types.txt`: treasury government behavior.

See [the test checklist](COMMON-FUND-TESTING.md) for actual expense, treasury-bucket and AI validation.

## Dev.52 follow-up

The old quarterly advance ceiling incorrectly gated essential refills. Standing court/army expenses now receive uncapped-by-headroom service from actual common cash, checked weekly. Only discretionary advances consume quarterly headroom; no new money is created. Works development's native financial-readiness bonus (treasury >= 20,000) also recognizes a fully funded matching development grant below that balance. Native war/culture restrictions, project prices and all contribution costs remain. AI project proposals are bounded to one per monthly initiative across the government.

Installed references checked for Marshal: `common/subject_contracts/contracts/celestial.txt:698` enables title MaA and the following modifier provides -50% recruitment and -50% maintenance. `common/defines/00_defines.txt:646` defines base regiment caps by tier, and lines 685-687 define treasury purchase/maintenance conversion multipliers. `common/script_values/01_dynamic_values.txt:406` scales the existing major-treasury quote from six months of variable income, bounded by the native quote limits. Cash, a recruitment quote and regiment slots are different constraints.
