> Historical dev.44-48 snapshot. Superseded by the dev.49 [common-fund implementation](COMMON-FUND-IMPLEMENTATION.md), [expense audit](COMMON-FUND-EXPENSE-AUDIT.md), and [test checklist](COMMON-FUND-TESTING.md). Earlier runtime statements have not been revalidated for dev.49.

# Revenue AI and recurring gameplay

Updated: **2026-10-28**  
Native audit baseline: **dev.44**; implementation: **dev.48**  
Status: **Custom initiative and role-based responses implemented in dev.48 source. Engine/observer testing and balance tuning are pending.**  
Main tracker: [REVENUE-REVAMP.md](REVENUE-REVAMP.md).

## Why a custom driver is needed

Native AI already makes some treasury decisions, but its conditions and cooldowns do not guarantee activity for the proposed Revenue module:

- Treasury requests require AI applicants to be at peace, have a sufficiently low treasury and have no request cooldown. Patient/Humble traits reduce their willingness to ask; sufficiently strong negative weights can suppress a request.
- Native refusal can give an AI applicant a **ten-year** request cooldown. A player recipient receives a **three-year** AI-request throttle after acceptance or refusal. These are anti-spam measures, but they can make a ministry feel quiet.
- Native remittance demands use a `vassals` AI target pool even though the interaction's civilian eligibility supports wider same-realm targets. Revenue's own vassals do not represent all eligible civilian governors. Our initiative should enumerate supported offices explicitly.
- The manual Suggest Budget Change decision has `ai_potential = { always = no }`, all tier check intervals at zero and `ai_will_do = { base = 0 }`.
- **Budget AI is not entirely disabled:** an annual native callback attempts `tgp_china_ministry.0100`, whose conditions include elapsed budget time, changed capacity or a large deficit. A fallback in `random_yearly_playable_pulse` can also enact an AI budget. The earlier description of that fallback as quarterly was incorrect. Coordinate with these native paths instead of creating competing budget changes.

## Guaranteed checks, meaningful choices

The module must run without a human clicking an interaction or an AI passing a random interaction roll. Scheduled checks are guaranteed; they generate financial action only when a valid need or opportunity exists. A healthy realm must not be forced into debt or a disaster merely to produce an event.

| When | What happens |
|---|---|
| Startup / loaded-save initialization | Initialize the realm's Revenue state once and resume valid pending work. Do not invent a backlog, reset cooldowns or pay anything on setup. |
| Every quarter | Check senior civilian distress, available ministerial reserves, existing funding needs and outstanding requests. Select a small number of meaningful cases, deduplicated by office and purpose. |
| Annually | Offer one Revenue review of allocations under the current fiscal priority. Maintain the programme, propose a real allocation or recommend a priority change to its authority. Chancellor owns priorities subject to imperial instructions; Revenue cannot overwrite them. AI follows the same hierarchy. Coordinate imperial budget proposals with native maintenance. |
| A relevant request/change | Reconsider an existing case when an official petitions, a supported recovery/project need appears, a contribution is disputed or funding becomes available. Use verified callbacks where available; the quarterly check remains the fallback. |
| While a case is pending | A bounded maintenance check revalidates authority, people, need and money. Follow standing policy, seek required approval or expire an obsolete proposal. Never turn an unanswered approval into consent. |

Use the documented `quarterly_playable_pulse` and yearly callback additively, filtered to the Chinese realm authority with a per-realm cadence guard. Revenue's checks must continue on other council assignments; Collect Taxes keeps its native behavior. Do not add an unverified monthly engine hook or scan every character every day.

## How the actors interact

| Actor | Initiative | Response and political behavior |
|---|---|---|
| Civilian governor | AI requests help for actual treasury distress, supported recovery or an unfunded eligible project. It can negotiate an extraordinary remittance or appeal a disputed settlement. | Weigh need, remaining resources, burden and terms first. Ambitious/family/faction ties influence bargaining; a rival relationship can discourage voluntary requests without preventing Revenue from noticing serious need. Human governors choose their own petitions. |
| Revenue | Proactively compares needs with authorized imperial funds and available departmental contributions. It can propose assistance without waiting for a governor to ask. | Fund, offer less, seek a contribution, recommend recovery treatment or decline. Authority and affordability are hard limits. Traits influence which lawful opportunity is preferred. Human Revenue receives concrete proposals, with standing automation only where authorized. |
| Chancellor | Establishes a fiscal priority on taking office and reviews it annually; may reconsider after a material change or resolve a dispute. | Choose Build Reserves or Restore Provinces using real conditions and personality. Respect player-set policy and imperial instructions. Routine authorized measures do not need another Chancellor event. |
| Emperor | Enacts the persistent fiscal-authority law and protected reserve; considers exceptional measures and material budget recommendations. | Weigh affordability, urgency, departmental burden, policy, relationships and trust in the recommending official. May approve, reduce or return a recommendation. Human emperors retain every reserved decision. |
| Donor ministry | Receives a proposed contribution from its available public reserves. | Cooperate, offer less or dispute according to remaining funds, known commitments and political relationships. A valid compulsory mandate may settle the dispute; willingness alone does not override legal authority. |

Chancellor/Revenue disagreement may produce an occasional political choice, not an approval chain on every payment. A favourable grant or burdensome contribution creates its opinion/obligation consequences only after the financial action succeeds.

## Simple balancing rules

1. **Separate starting a case from choosing its outcome.** Real distress or a valid funding gap can create a case reliably. AI then evaluates its response; it is not forced to fund everything.
2. **Need before personality.** Rank urgent hardship above ordinary projects, then waiting time and government priority. Use bounded relationship/family/faction adjustments. Just/Honest prefer defensible terms; Compassionate favours recovery; Greedy preserves reserves or seeks favourable terms; Ambitious builds allies; Vengeful can resist rivals. None bypasses reserve/authority checks.
3. **Use public finances.** Check the actual paying treasury and its balance after payment. Use available native income/balance values and known commitments; do not invent an exact operating-cost forecast. Reserves, expenditure ceilings and contribution cooldowns protect the government.
4. **Prevent extraction loops.** No same-account transfers, immediate donor/recipient reversal, repeated draining of one ministry or grants used solely to manufacture a new eligible request. Do not count money still awaiting approval as delivered funding.
5. **No repeated rejection loops.** Record outcomes on the office/need, with a provisional six-month ordinary resubmission cooldown. Distinct disasters/material deterioration remain balancing considerations; the initial implementation keeps the stated office cooldowns rather than inventing an unverified automatic emergency override. A new holder cannot reset the cooldown. Integrate the custom route with native requests so ten-year/native global throttles do not accidentally suppress the whole module or create double payments.
6. **Keep policy stable.** Hold ordinary AI policy for about a year, subject to imperial instructions or a material change. Annual review must not undo player/native decisions every quarter. Adapt to native budget enactment rather than immediately overriding it.
7. **Fair treatment of people.** Same qualification and financial limits for player and AI officials. AI must not spend a human authority's reserved funds or make a human governor's voluntary decision for them.

Initial treasury floors, amounts, relationship weights and authority limits are implemented and listed in the main tracker. They remain provisional until playtesting; the six-month ordinary aid cooldown and annual policy interval are not tested balance conclusions.

## Activity without popup overload

- A human Revenue minister receives one scheduled annual allocation/recommendation opportunity even in a quiet year, with an explicit option to keep the current programme. This does not give Revenue control over the Chancellor's priority. First appointment/startup can schedule it once after initialization.
- Aim for roughly **two to four additional consequential choices in an ordinary year**, not a required number of crises. This is a playtest target; genuine severe needs or reserved approvals may exceed it.
- Routine AI administration and previously authorized standing policy run quietly. Requests for the same need merge; prolonged incidents do not generate a new popup every quarter.
- At most one active fiscal event per recipient. Prioritize urgency with bounded aging so old requests are not permanently ignored.
- An annual coordinated review can involve Revenue, Chancellor and emperor without sending three copies of the same event. Only each role's actual decision is interactive; routine results use restrained notices or a consolidated report.
- Player Revenue can leave matters pending or resume them. Unavailable authorities preserve or expire proposals safely; no hidden automatic approval or surprise debit.

## Engine verification still required

The first treasury-contribution build must include the scheduled driver and AI responses. A player-only interaction is not the completed first playable feature. Policy defaults and basic balancing belong in that build; deeper political tuning can follow.

| Scenario | Expected result |
|---|---|
| Human Revenue, all other relevant roles AI | Valid proposals appear without manual petitions; choices have visible financial/political outcomes. |
| Human governor, AI government | AI Revenue considers the governor's eligible needs and responds to petitions without privileged player treatment. |
| Human emperor or Chancellor, AI Revenue | Routine delegated work happens; exceptional spending/disputes reach the correct human authority. |
| All relevant roles AI | Needs are detected, proposals decided, lawful transfers completed and obsolete cases cleared without human input. |
| Quiet, solvent realm | Annual policy review occurs; no fabricated emergency, pointless transfer or forced expenditure. |
| Treasury-poor government | AI can reduce/refuse aid or propose lawful contributions; protected reserves remain respected. |
| Several simultaneous needs | Queue preserves all distinct needs, combines duplicates and prioritizes fairly without stacked windows. |
| Rival, friend and faction scenarios | Bias changes close decisions; it cannot make unaffordable or unauthorized transactions succeed. |
| Native budget/request activity, succession and save/reload | No duplicate payment, competing budget flips, reset cooldown or stale authority. |

During a multi-year observer test, record checks run, eligible needs, cases created/merged, decisions, completed transfers, rejected commitments, waiting time and notices. An idle quarter should have a concrete reason such as no need, no lawful funding, cooldown or pending player decision. Measure balances, donor concentration, repeat grants, unresolved queues and event count; do not judge AI only by the number of popups.

## Native source references

Paths below are relative to the installed game's `game` directory; all were read only.

- `common/character_interactions/10_tgp_interactions.txt`: request eligibility 5343-5355; refusal/global throttles 5537-5591; request AI 5594-5768; demand target/AI 588-661.
- `common/decisions/dlc_decisions/tgp/tgp_china_decisions.txt`: manual suggestion AI disabled at 1448-1461.
- `common/on_action/yearly_on_actions.txt`: annual treasury-budget event at 1092-1103; AI fallback at 3129-3151 within `random_yearly_playable_pulse` (starts at 3033), not `quarterly_playable_pulse` (2992-3029).
- `events/dlc/tgp/tgp_china_ministry_events.txt`: budget update conditions at 586-610; AI delegation option at 782-839; proposal acceptance/refusal weights at 1125-1246.
- `common/on_action/_on_actions.info`: yearly and quarterly playable callback definitions at 7-13.

## dev.47 playtest feedback

- Fiscal authority is a persistent realm law, with five-year change protection; succession no longer resets it as a new personal mandate. The older standing variable migrates once.
- Player draft amounts are editable; AI keeps bounded ordinary proposals rather than automatically taking the maximum available surplus. Larger transfers still require the proper approval.
- Budget-cut ministers have one appeal within 180 days. AI appeals for treasury below 200, a negative monthly balance, or Ambitious/Arrogant/Greedy traits. The deciding superior weighs actual distress against reserve-building policy. Appeals never create another appeal, and cannot reverse a later contract change.
- Human participants receive deduplicated result events. Donor consent awaiting approval is reported separately from a completed payment. AI participants do not receive informational result events.
- Petition/queue, interruption and multi-year AI tests were explicitly reported as not yet attempted. No behavior or balance pass is inferred from source verification.
