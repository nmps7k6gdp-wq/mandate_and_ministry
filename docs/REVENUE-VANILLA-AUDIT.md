> Historical dev.44-48 snapshot. Superseded by the dev.49 [common-fund implementation](COMMON-FUND-IMPLEMENTATION.md), [expense audit](COMMON-FUND-EXPENSE-AUDIT.md), and [test checklist](COMMON-FUND-TESTING.md). Earlier runtime statements have not been revalidated for dev.49.

# Vanilla Ministry of Revenue: foundation audit

Reviewed: **2026-10-28**  
Mod baseline: **0.4.0-alpha.20-dev.44**  
Method: read-only native inspection at dev.44. No engine playtest. This audit itself did not change vanilla/gameplay files; the later dev.45 implementation is described below.

Current design and implementation progress: [Revenue tracker](REVENUE-REVAMP.md). The agreed scope excludes custom fiscal reviews, career-score changes and campaign provisioning.

AI initiation, native cooldowns, existing automatic budget maintenance and the proposed recurring driver: [Revenue AI plan](REVENUE-AI-PLAN.md). The manual budget-suggestion decision is AI-disabled; native annual budget checks and a random annual AI fallback remain active under their conditions. The earlier quarterly-fallback description was incorrect; the proposed custom quarterly driver is separate. Final limitations: [Preflight review](REVENUE-PREFLIGHT.md).

## Main finding

Revenue is already a treasury administrator, creditor and budget adviser. The revamp should make these powers work together and create political choices around them. A second system of generic gold grants, debt requests and recovery projects would duplicate much of the native foundation.

This is an audit of the relevant script paths, not a claim that every government/DLC combination or engine-side calculation has been tested.

## What exists now

| Native feature | Observed behavior | What the revamp should add |
|---|---|---|
| Revenue office | `e_minister_of_revenue` uses the `councillor_steward` council seat. Native appointment effects synchronize title and seat. | Fiscal priorities and decisions attached to the existing office; preserve its succession handling. |
| Collect Taxes | The default Steward/Revenue task increases the council owner's **domain tax** through a Stewardship-scaled modifier. Its monthly side-effect pool includes extra gold and adverse county taxation/corruption events. | Preserve native behavior; no new observation or quota-audit system. |
| Other Steward tasks | The same task file defines Promote Culture, Promote Cultural Acceptance and Convince De Jure Territory, with their native conditions. Develop County is restricted to Works when the council owner has the Chinese ministry system. | Preserve native task availability. Avoid assuming that Revenue owns Chinese county development. Exact menus still need an in-game check. |
| Treasury requests | `celestial_request_treasury_interaction` redirects ordinary non-councillor civilian governors' requests to Revenue when the appropriate Chinese hegemony/ministry conditions hold; military requests go to War. It checks the recipient's treasury, spends Influence, and can request debt clearance. | Policy for prioritizing requests and exceptional aid, ideally through the existing route rather than a competing petition. |
| Request consequences | Accepted requests pay from the recipient's treasury. Debt clearance can create a strong indebted hook and a dynastic-cycle catalyst. AI requesters can gain gratitude; player recipients have a native three-year AI request throttle after acceptance. | Preserve native political credit and hooks. Avoid adding duplicate rewards or a second unthrottled AI petition route. |
| Demand remittances | `celestial_demand_treasury_interaction` gives Revenue a same-realm civilian-target branch, including subjects below another governor. It requires recipient treasury above 100, has a two-year general cooldown and ten-year target cooldown, and costs Influence. | Give extraordinary demands a policy purpose and context. Do not invent a parallel flat personal-gold back-tax demand. |
| Give treasury | `celestial_give_treasury_interaction` supports treasury transfers to eligible same-realm recipients. Native AI availability requires treasury above 1,000. | Use this payment foundation where suitable, with an explicit account and authority. It is a shared interaction, not a Revenue-exclusive power. |
| Clear treasury debt | `pay_treasury_debt_interaction` supports Revenue, War and the recipient's top liege under its native branches. It pays the treasury deficit, can demand a weak or strong indebted hook, and offers a kindness route to Generous/Compassionate characters. Native AI requires treasury above 1,000. | Make debt assistance part of Revenue's political identity. Retain the civilian/military distinction and existing relationship consequences. |
| Budget proposals | Revenue can propose salary, ministry, military, sovereign-favored or balanced budgets, or increases to individual categories. The decision requires adulthood and peace, costs Influence and has a three-year cooldown. The emperor receives an event to accept or refuse. | Chancellor advice, reasons for proposals and better AI prioritization. Keep the existing budget laws and imperial approval path. |
| Ministry funding | The native civilian minister contract includes `monthly_treasury_from_ministry_budget_base = 1`. The emperor already has salary, ministry and military budget allocation laws. | Keep departmental funding distinct. The revised plan uses authorized imperial funds for provincial assistance and limited contributions between ministries, so Revenue's standard share is not routinely drained. Individual ministry budgets can already vary below or above the default. |
| Individual ministry budget | `celestial_ministry_budget` already supplies Low, Medium and High Budget settings in the celestial subject contract. Low adds `-0.5` and High adds `+0.5` to `monthly_treasury_from_ministry_budget_base`; Medium is the default with no adjustment. Other modifiers can affect the final receipt. | A concrete native foundation for proposed Revenue influence over future departmental funding. Exact distribution and effects on the imperial budget need engine verification; a lower setting must not be assumed to finance an equal increase elsewhere. |
| Census great project | Revenue, the Chinese emperor and an eligible Grand Secretariat diarch can found `minister_project_conduct_census`. The project uses treasury-or-gold costs and has a base construction time of 1,825 days before modifiers. On completion it improves local control and gives eligible counties in the target duchy a 20-year census modifier. | Retain the native project and avoid duplicating its benefits; no custom review dependency. |
| Census benefits | The county modifier gives +10% tax, +10 popular opinion and +10% development growth. Other project contributions include treasury-debt work, exam verification, fertility measures and disaster insurance. | Recognize these native efforts before adding competing relief, assessment or career rewards. Review the detailed contribution behavior before extending it. |
| Disaster recovery | In the native minister-aid event, Revenue removes specified recovery/resettlement tax burdens and sets a flag preventing related negative tax modifiers from project contributions. It earns native Influence and Merit. The Chinese ministry branch assigns general recovery management availability to **Works**. | Revenue finances/tax-relieves; Works organizes reconstruction. Link to native recovery rather than starting a second disaster system. |
| Career influence | The shared ministerial career interaction already exposes candidate-score, Merit and family examination-bypass options under its native conditions. | Preserve native options; the revised Revenue plan adds no custom fiscal career score. |
| Treasury corruption | Vanilla already has the shared Siphon Treasury scheme, with five-year target cooldown and AI restrictions including Honest/Just exclusions. | Reuse or deliberately distinguish from existing corruption. Do not assume the removed custom Censor-Justice ledger still records anything. |

## Money and jurisdiction implications

**Additional feasibility check, 2026-10-28:** Equal departmental funding describes the standard setup, not a fixed engine limitation. Native per-ministry budget settings already vary it. The engine also exposes `vassal_contract_set_obligation_level`, used by native contract interactions/events. Applying it to the ministry-budget category through a custom Revenue authority flow remains an engine test, not a proven custom feature.

**Special-office limit:** The ministry-budget category checks the primary title's `celestial_ministry_appointment_succession_law`. Grand Marshal instead receives `celestial_grand_marshal_appointment_succession_law` in the native appointment helper. Do not assume the same budget contract is valid for it. Low Budget also includes native `subject_opinion = -15`; account for this when adding custom political consequences.

**Transfers have a native implementation:** Demand Treasury snapshots a sum from the recipient's treasury and calls `pay_short_term_treasury` in that payer's character scope with a target and amount (`10_tgp_interactions.txt`, 509-533). Give Treasury uses the same command (939-962). This supports a proposed one-time contribution between office treasuries without a custom currency. Use the actual donor as payer; do not mint the recipient's payment with an unmatched `add_treasury`.

**Protected reserves are our authorization checks:** The scripts can check balances and limit a proposed transfer. This is not a global engine lock on the remaining funds; native expenses can still occur. Recheck the current office holders, authority and account balances when committing, and test interaction with native budget buckets. Treasury belongs to the title across succession according to the native Treasury concept, so a new holder must not inherit an old event's unchecked personal authority.

**Treasury and personal gold are different accounts.** The proposal's references to `emperor.gold`, `governor.gold` and the minister's pocket cannot all stand for public finances. Native treasury requests explicitly use `treasury` and `pay_short_term_treasury`; projects can use treasury-or-gold costs. A public appropriation, departmental grant and private bribe must each name the actual account that pays and receives it.

**Native taxes already reward careers.** The standard civilian province contract includes `monthly_merit_per_liege_tax = 0.8`; other provincial types differ. This is one reason the revised design excludes a separate fiscal promotion bonus. Settlement tuning should still consider existing tax-linked Merit.

**Nested governors already exist in native financial interactions.** Revenue's civilian remittance branch checks the shared top realm rather than requiring a direct vassal. The new fiscal target model should also account for nested kingdom governors supported by the current mod. One county must not be charged or relieved twice because both its kingdom and its superior empire are processed.

**A tax modifier needs a proven recipient path.** A nested king's vassal contribution modifier concerns their immediate liege; it does not by itself prove that the emperor receives a particular amount. County tax changes, contractual contribution changes and explicit treasury transfers are different tools. Follow the native transfer/accounting path when an exact remittance or grant is promised.

**Provincial allowance is incoming funding:** `celestial_treasury` changes `monthly_treasury_from_liege_mult`. It cannot be treated as a direct tax-remission switch. Also, native treasury requests pay from the recipient's account: implementing imperial-funded civilian requests requires a real mod-side routing/payment bridge, not a post-payment callback.

## Current mod relationship

Dev.45 adds a narrow mod-side override of `celestial_request_treasury_interaction` in `zz_mam_revenue_native_requests.txt`. Supported senior civilian cases enter Revenue's queue and use the authorized payer. Supported human players use the Ministry petition instead of a duplicate native request action; native AI can use its existing request selection. Unsupported branches, native costs/cooldowns/AI and the original unsupported acceptance/decline behavior are retained and source-checked. The Ministry petition shares financial records/cooldowns, uses the native medium Influence cost and offers supported hook/debt options.

The native Revenue budget decision, Census, Collect Taxes and debt interaction are not overridden. The annual Revenue review can invoke the existing imperial budget-recommendation event with its expected scopes. Existing ministry handoffs and succession approval remain intact. No Revenue fiscal term was added to Personnel's candidate score.

The old custom Censor-Justice payment/offer/appointment hooks remain empty compatibility definitions. Revenue records facts in its own finite-lived fiscal records and does not call those old hooks or restore prosecution.

## Source map

Installed reference root: `C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game`.

| Source relative to that root | Relevant definitions / approximate starting lines |
|---|---|
| `common/council_positions/00_council_positions.txt` | `councillor_steward` at 139; ministry handoff at 259 |
| `common/council_tasks/00_steward_tasks.txt` | Collect Taxes at 1; Develop County at 133 and Chinese restriction at 151; culture tasks at 669/1414; de jure task at 1884 |
| `common/on_action/councillor_on_actions.txt` | `task_collect_taxes_side_effects` at 347 |
| `common/script_values/99_steward_values.txt` | Collect Taxes scaling section; total scale at 134 |
| `common/character_interactions/10_tgp_interactions.txt` | Siphon at 2; Demand Treasury at 421; Give Treasury at 817; career influence at 4133; Request Treasury at 5278; Clear Debt at 11590 |
| `common/decisions/dlc_decisions/tgp/tgp_china_decisions.txt` | `tgp_suggest_budget_change_decision` at 1242 |
| `events/dlc/tgp/tgp_china_ministry_events.txt` | Imperial budget response `tgp_china_ministry.0200` at 961 |
| `common/laws/02_admininistrative_laws.txt` | Salary allocation at 1721; ministry allocation at 2330; military allocation in the same budget-law section |
| `common/subject_contracts/contracts/celestial.txt` | Civilian tax-linked Merit near 70; civilian minister funding near 672 |
| `common/subject_contracts/groups/subject_contract_groups.txt` | Celestial contract group includes `celestial_ministry_budget` near 150 |
| `common/character_interactions/00_modifiy_vassal_contract.txt` | Native use of `vassal_contract_set_obligation_level`, including near 283 |
| `common/great_projects/types/00_ministry_projects.txt` | Census at 4005; completion around 4160; special contributions from 4323 |
| `common/modifiers/10_tgp_modifiers.txt` | Census and related modifiers at 219 |
| `events/situation_events/tgp_natural_disaster_events.txt` | Minister-aid event at 1510; Revenue option at 1621 |
| `common/scripted_triggers/10_tgp_natural_disaster_triggers.txt` | Chinese recovery management availability uses Works |
| `localization/english/dlc/tgp/dlc_tgp_china_game_concepts_l_english.yml` | Revenue concept and native action breakdown at 176-179 |

Line numbers refer to the installed files inspected on this date and may move with game updates.
