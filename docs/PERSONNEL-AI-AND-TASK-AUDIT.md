# Personnel AI and assignment audit

Audited dev.38; fixes implemented in **0.4.0-alpha.20-dev.39**. Source checks pass; in-game task and balance testing remains pending.

## Findings in dev.38

- Personnel nominations have explicit personality weights and current-Chancellor/imperial-priority biases. Professional category weights depend on the number of available lateral/promotion/first-office slots; marked provincial candidates have zero AI weight.
- Provincial imperial confirmation has no explicit approval/rejection weights. Upper/lower central-ministry approval already has its own explicit personality/quality weights.
- The Chancellor priority interaction has ai_frequency 0 and ai_potential always no: current AI Chancellors approve lower ministers, but do not autonomously direct Personnel policy.
- Appointment authority laws have ai_will_do 0 and their decision is human-only: an AI emperor does not proactively change these custom laws.
- Manage Talent is genuinely connected to native monthly callbacks, a yearly observation pass, mature service evidence and player/AI career modifiers. Initial automatic baselines can be delayed until the next annual pass; task-change ordering needs protection.
- Royal Favor's MAM refresh is attached below task_bestow_royal_favor_side_effects, whose native trigger rejects processing while had_chancellor_task_side_effect is present. This can interrupt the promised rolling 90-day benefit.
- AI service commendation does not remove an existing poor-service modifier as the player commendation does.
- The bonus was attached to a native score shared by civilian governors, military governors and Grand Marshal. This leaked civilian career benefits into military appointments.
- Native score additions are +20 endorsement for higher senior rank, +10 favor, -10 poor service. Public-suitability shortlist comparison is separate from this native score; these are not automatically +20/+10 to every custom comparison.
- The latest error log has two make_story_owner target-is-dead errors for mam_senior_appointment_story:on_owner_death at 22:12:01. This is not proof of a task problem, but can disrupt appointment continuity after imperial succession.

## Review interface recommendation

Keep Review Official as the player's Manage Talent action. Consolidate observation duration, baseline/current control/development/merit, interruption flags and endorsement/concern choices into one window. The separate Service Dossier page is optional presentation; the underlying observation records remain necessary. No interface removal has been requested or implemented in this audit yet.

## Balance boundaries

Fix verified callback/state faults before broad numerical tuning. Preserve native task effects and target selection, the 3-year evidence rule, +20/+10/-10 score magnitudes, player task choices, and explicit imperial direction. Any AI policy autonomy must be bounded and must not overwrite a player's standing instruction. Numerical balance cannot be certified without an observed multi-year AI run.

## Implemented first pass

| Area | Change in dev.39 |
|---|---|
| Royal Favor | Personnel's native task clone now applies the custom benefit through its own monthly effect, independent of the throttled random-side-effect handler. All native start/cancel/progress/opinion/prestige/target rules are inherited. Native-allowed unlanded family heads are no longer excluded by an additional landed-only check. |
| Manage Talent | Maintenance runs on task start and monthly callbacks. Initial/resumed baselines are refreshed without waiting for the annual pass; annual judgment runs maintenance first. Canceling the task immediately marks an observation gap. Resumption starts a new period with the correct restart reason. |
| AI commendation | A new endorsement clears the old poor-service assessment, matching player commendation. |
| Career score scope | +20 endorsement/+10 favor/-10 assessment now enter only the native civilian-governor appointment type. The shared civilian/military score is restored to vanilla. Endorsements require a higher current public rank as well as a higher recorded rank, preventing a stale endorsement from rewarding a lateral move after an outside promotion. |
| Chancellor policy | An AI Chancellor can initialize professional, continuity or discretionary nomination priorities and renew them annually. A quarterly wake-up and ordinary task maintenance find new officeholders. Imperial instructions and priorities without AI provenance are protected. Manual direction clears AI provenance. No extra popup or decision is added. |
| Professional alternatives | Total professional-category weight is stable with one, two or three eligible categories. Neutral total is 60; Diligent and professional direction each add 150 before division among the available categories. |
| Personal alternatives | Ambitious/deceitful/greedy bonuses are tied to relevant family, faction, friendship or payment relationships. Weak personal choices are suppressed for Just/Honest ministers and under professional direction. Vengeful ministers avoid rival personal choices. |
| Standing provincial marks | Marked nominees can be chosen when a previously human minister becomes AI; the previous zero-weight dead end is removed. A mark does not force the choice or waive eligibility. |
| AI emperor | Explicit provincial approval/return weights replace the undifferentiated options. Valid ordinary nominations have a 100:10 approval/return weight ratio; ethics, quality and personal rivalry modify that. Invalid nominees cannot be approved. |
| Imperial succession | Pending appointment stories choose a living realm holder or living title heir as their next owner, addressing the logged dead-owner error. |
| Task tooltips | Both native assignments now explain the additional service/favor mechanics. |

### What each AI currently controls

- **Personnel:** chooses among lawful provincial nominees using professional quality, native order, personality, standing marks, private relationships and the current priority. Under Manage Talent, performs an annual silent service review after observation updates. Task selection and Royal Favor target selection retain native AI rules.
- **Chancellor:** confirms/replaces successors to the lower six ministries and can shape Personnel's nomination policy when imperial/player instructions permit. Just/Honest/Diligent/Patient favors professional selection; Lazy/Content/Impatient/Shy favors continuity; remaining profiles allow ministerial discretion. This is policy influence, not authority to bypass the emperor's reserved confirmations or appoint the upper three ministers.
- **Chinese emperor:** confirms/replaces successors to the upper three ministries and judges reserved provincial nominations. The current custom appointment-authority law is respected. This pass does not add autonomous changes to that law or autonomous new imperial priority edicts; the existing law/standing instruction continues until changed through its controls.

The 100:10 neutral confirmation ratio is a scripted weighting, not a measured approval rate. With a weak but legal nominee, a Just/Honest/Diligent emperor reduces approval to 20 and raises return to 60. A Vengeful emperor is more likely to return a personal rival. Other simultaneous modifiers can change these examples.

## Remaining balance risks to measure

1. **AI praise is stricter than player praise.** A player needs at least one improving measure and no decline after three comparable years. Neutral AI normally requires two improving measures; Just/Honest/Paranoid/Lazy can require three, Generous can reduce the requirement, and an Ambitious minister is more lenient to their house. Control is capped at 100: a baseline above 95 cannot improve by the required five points. A three-measure threshold can therefore be impossible for an otherwise excellent governor. Recommend a future capacity-aware threshold or a simpler common praise standard after measuring actual awards.
2. **Evidence can be old.** The baseline is not automatically rolled forward after judgment. The same long-term improvement may support another endorsement after the old modifier expires. A recorded war flag remains until observation restarts, so one old war can block later adverse assessment. The emperor being at war marks every sampled governor, even when their own province is not directly affected. A rolling three-year assessment window is a potential follow-up, not implemented in this pass.
3. **Native task switching can interrupt maturation.** Manage Talent has native weight 1 plus 500 below ten filled court positions; Favor has its native loyalty/friendship incentives. This does not guarantee a continuous three-year observation period for AI Personnel. Measure task changes before adding an AI minimum term.
4. **Transfers can create more vacancies.** Lateral nominations are legal, but repeated moves by the same official can churn the queue. Track repeat moves and source vacancies before imposing an AI cooldown or a transfer penalty.
5. **There are two score systems.** These modifiers change native civilian appointment scores and can change the next native/default candidate. Custom professional comparison uses merit/exam evidence/skills; it is not itself increased by +20 or +10. The endorsement does not guarantee selection or make an unqualified candidate eligible. Central ministry succession uses its own score and is outside these civilian task bonuses.
6. **War observations are snapshots.** Baseline, yearly and manually opened observations can record war, but a short war entirely between observations can be missed. Treat the absence of the flag as absence of observed disruption, not proof that no war ever happened.

## Focused in-game test

Use a separate test save and restart CK3 with dev.39. These are expected results, not completed engine tests.

### 1. Manage Talent: initial wiring (one or two months)

1. Play the actual Personnel minister and select **Manage Talent**.
2. Choose a supported civilian county/duchy/kingdom/empire governor in the same realm. Use **Ministry > Personnel: Review Official > Let me examine the service papers**.
3. Within the first monthly callback, there should be a current service record with the correct governor, jurisdiction and recent start date. A title/holder/realm/county-set change legitimately restarts the record.
4. Before three comparable years, endorsement and adverse assessment should be unavailable. The interaction itself should disappear when Personnel is no longer managing talent.

### 2. Manage Talent: actual career effect (three years)

1. Keep Manage Talent active and the governor's office/jurisdiction unchanged for at least three full years.
2. Record the baseline. In a controlled test, increase **Merit by one rank** after observation starts, while avoiding declines in average control/development. Alternatively, improve average control by at least five or average development by at least 0.5 across the governor's entire subrealm. Improving just one county may not move the average enough.
3. Reopen Review Official. A player minister should be able to endorse an improving governor without recorded concerns.
4. The governor should gain **Personnel Endorsement** for three years. In a higher eligible senior civilian title's native candidate-score breakdown, look for **+20 Personnel Endorsement**. Other native score changes can occur at the same time; inspect the named line rather than only the total or rank.
5. The same/lower public rank, county/duchy vacancies, military offices and central ministries should receive no endorsement bonus. The endorsement is consumed by a completed Personnel appointment.
6. Switch away from Manage Talent for a month, then resume it. The observation period should restart; old wall-clock service must not immediately qualify as three newly observed years. Previously earned character modifiers keep their normal remaining duration.

### 3. Poor service and recovery

1. Use a mature, comparable record with no observed war. In the test save, lower average control by at least 20 from baseline; this creates a major concern for every AI scrutiny threshold.
2. A player can record concern: **-10 senior civilian candidate score for three years**, removing an old endorsement. A Compassionate minister receives the displayed base 10 Stress, modified normally by the game.
3. For AI Personnel, wait through the emperor's next annual observation/review pulse. There should be no extra review popup; the assessment appears on the governor.
4. Restore the governor and provide enough positive measures for the AI minister's praise threshold. After the next qualifying annual review, an endorsement should clear the old poor-service modifier. The strict-praise/cap issue above can prevent this; distinguish failure to qualify from a missing callback.
5. Repeat with war visible during an observation: the resulting war flag should block adverse judgment. That flag currently stays until a restarted observation period.

### 4. Bestow Royal Favor (months)

1. Select **Bestow Royal Favor** and choose a native-allowed target who can compete for a senior civilian office. The native task requires Royal Court access and sufficient court grandeur; its normal target restrictions still apply.
2. Wait one or two monthly ticks. The target should have **Personnel: Royal Favor** with about 90 days remaining, and a named **+10** line for eligible senior civilian appointments in the sponsoring realm.
3. Leave the task active for **four to six months**. The benefit should keep refreshing rather than lapse at the initial 90-day point, even after a native task side effect fires. It must not stack into +20/+30.
4. Change target or stop the task. The old target's custom favor may last until 90 days after its final refresh; it then expires. Native opinion/prestige and task completion behavior continue separately.
5. Check a county/duchy, military post and central ministry: the custom +10 should be absent. A higher civilian post may combine +20 endorsement with +10 favor when both conditions qualify.

### 5. AI appointment and Chancellor test (five to ten years)

1. Under delegated law, observe an AI Personnel minister across multiple vacancies. Record first grants, promotions, lateral transfers and repeated moves of the same official.
2. Leave imperial direction discretionary and use an AI Chancellor. Within the next quarterly wake-up, check the log for professional, continuity or discretionary policy. The policy normally lasts a year and can reset when the officeholder changes.
3. Set an explicit imperial professional/continuity instruction. That instruction must survive quarterly/annual AI policy checks. A manual non-AI priority is also protected.
4. Select a confirmation law, then let the emperor act as AI. Ordinary qualified nominees should usually be accepted; weak ethical conflicts and Vengeful rivalries should raise returns. Gather several dozen cases before interpreting percentages.
5. Kill two governors, and later kill the emperor with unresolved cases. Both vacancies must survive and reach the current officeholder; the previous make_story_owner target-is-dead error should not recur.
6. Repeat upper/lower central-ministry succession separately. The new civilian career-score hook must not alter those ministry scores; Chancellor/emperor approval authority remains the six/three split.

## Useful log markers

- `MAM_PERSONNEL_TASK: Manage Talent baselines active`
- `MAM_PERSONNEL_TASK: Royal Favor refreshed on current target`
- `MAM_PERSONNEL_SERVICE: poor service assessment applied`
- `MAM_PERSONNEL_SERVICE: advancement endorsed and old concern withdrawn`
- `MAM_PERSONNEL_AI: Chancellor set professional nominations` / `set continuity nominations` / `allowed ministerial discretion`
- `MAM_PERSONNEL_AI: Personnel selected ...`
- `MAM_PERSONNEL_AI: emperor selected approval` / `emperor returned a nomination`

Choice logs show AI intent; the existing `MAM_PERSONNEL_APPOINTMENT: destination grant completed` marker and actual holders/lieges establish completion. New logs require a fresh session with this build. The prior error log also contains unrelated title-flavorization warnings, so this audit does not claim that the whole game log is clean.

## Source verification

Passed structure, unique database key, helper/value reference and BOM checks across 223 scripts. The mod's civilian appointment definition matches installed vanilla after removing its single added career-score term. Favor uses the documented independent task monthly effect, annual review maintenance precedes evaluation, AI recovery removes the old assessment, and the owner-death path validates living targets. This is source verification; native task execution, actual modifiers, AI frequencies and save continuity still need the playtest above.
