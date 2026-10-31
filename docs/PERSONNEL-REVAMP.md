# Ministry of Personnel revamp

Build: **0.4.0-alpha.20-dev.44**  
Updated: **2026-10-28**  
Status: **Revamp complete, accepted on 2026-10-27 at dev.41. Jurisdiction maintenance dev.43 implemented; native engine regression tests remain pending.**

## Purpose and boundaries

Personnel shapes who governs through senior nominations, service assessment, imperial favor and political patronage. The emperor sets appointment authority; the Chancellor directs routine priorities within imperial instructions.

- County and duchy appointments retain vanilla order. They generate no Personnel appointment events.
- Senior civilian public governorships use Personnel appointment events. The supported custody unit is a clean senior jurisdiction directly below the emperor, or a kingdom beneath a supported civilian territorial empire governor.
- Eligible unlanded people remain candidates. Existing governors can be promoted without a manual replacement chain.
- The imperial throne, military jurisdictions, central titular ministries and ambiguous or unsupported land bundles retain native handling. They are not silently treated as ordinary civilian provinces.
- Deaths, the native governor resignation transfer routine, and promotions made through this workflow are connected to custody. Conquest, revocation, civil-war settlement and unrelated direct title-grant commands retain their native meaning.
- The Censor-Justice case system was removed in dev.42 for a fresh future design; minimal shared appointment/save-compatibility plumbing remains.
- The custom register window and launcher are unregistered. The old Personnel talent-register decision is hidden. No new flow requires the register.

## What to do in each role

| Role | Entry point | Responsibility |
|---|---|---|
| Personnel, any assignment | Vacancy event; Personnel: Resume Senior Appointments | Select eligible senior successors |
| Personnel, Manage Talent | Right-click an official ? Personnel: Review Official | Endorse improvement, record evidenced poor service, or continue observation |
| Personnel, Bestow Royal Favor | Existing native targeted council assignment | Cultivate favor and improve senior appointment prospects |
| Personnel | Existing mark-candidate interaction; Personnel: Clear Marked Candidate | Choose a personal shortlist candidate |
| Chancellor | Right-click Personnel ? Personnel: Direct Ministry Priorities | Set professional, continuity or discretionary priorities when imperial instructions permit |
| Emperor | Personnel: Set Appointment Authority | Delegate appointments or reserve imperial confirmation |
| Emperor | Confirmation event; Personnel: Review Appointment Recommendation | Approve or return reserved nominations |

Decision names follow `Personnel: <Verb> <Object>`. Role ownership controls visibility; temporary blockers control validity. Obsolete automation, recordkeeping toggles, old jurisdiction/discretion menus, forced-transfer proposals and judicial QA controls are retired or inaccessible.

## Current realm laws

Only one custom ministry law group remains available:

| Law group | Choices | Purpose |
|---|---|---|
| Senior appointment authority | Delegate / Reserve Empire / Confirm Every Senior Appointment | Whether Personnel can appoint directly or needs imperial confirmation |

Removed from gameplay in dev.34: Personnel nomination jurisdiction, Personnel selection discretion, judicial review, and the Chancellor's judicial mandate. The first two belonged to the retired forced-transfer workflow; the latter two belong to the suspended Censor?Justice system. Chancellor Personnel priorities remain available through the current interaction.

Old law menus and AI law-changing decisions are removed. Compatibility definitions retain the old database keys but have no defaults, policy flags, costs or effects and cannot be displayed, adopted or kept. Campaign startup cleanup removes old selections and cooldowns across rulers. A quarterly callback cleans affected rulers in loaded saves; Personnel maintenance also repeats cleanup for the emperor. The groups are hidden immediately after restarting with this build. Appointment-authority selections are preserved. Custom recruitment standards were also retired in dev.36; their saved selections and cooldown are removed. No vanilla files are changed.

## Senior appointment loop

1. An eligible vacancy is captured before normal succession/transfer installs a new governor.
2. The emperor temporarily holds the jurisdiction. The file records the exact acquired component titles, protecting unrelated imperial land.
3. Each custody file gets a persistent FIFO entry on the realm title. Personnel receives one queued appointment at a time; completing or deferring a case wakes the next eligible file after the current action resolves (normally within two game days).
4. The event presents named default, professional, minister-preferred and marked candidates when available.
5. Refresh searches current candidates and rereads the marked person. An already open choice retains its displayed character; it cannot silently switch to a newly refreshed person.
6. Native qualifications, current authority and source succession arrangements are rechecked.
7. A delegated appointment proceeds. A reserved appointment becomes an imperial recommendation instead.
8. The recipient explicitly remains a vassal of the emperor. After the title grant resolves, the office's recorded direct vassals are assigned to the new holder in a separate transaction. A serving appointee's lower source posting follows native succession; a clean senior source enters its own independent custody file.
9. A successful appointment records its outcome, applies contextual stress and links any active paid obligation.

Deferring a Personnel file snoozes it for 30 days. The resume action restores pending work. After 90 days, refreshed fallback candidates are considered; reservation laws still require imperial approval. If nobody qualifies, custody remains pending rather than granting office unlawfully.

Reserved recommendations have a separate imperial notification queue. An unanswered recommendation returns to Personnel after 90 days; it is never silently approved. The emperor can return it earlier without punishment.

## Manage Talent and performance

Observation follows the assignment automatically. Cancelling Manage Talent marks an observation gap; resumption invalidates baselines. Unobserved time does not earn credit.

- Mature, comparable service requires three years of observations.
- Improvement without current concern can earn a non-stacking three-year endorsement: **+20 native candidate score for an eligible higher senior civilian office**.
- Evidenced decline without recorded war disruption can receive a three-year poor-service assessment: **?10 senior candidate score**, withdrawing an existing endorsement.
- Neither action evicts an incumbent, manufactures qualifications or bypasses eligibility.
- A Compassionate minister receives **10 base Stress** when recording poor service.
- AI service advice uses the same evidence-based career consequences.

## Bestow Royal Favor

This remains Personnel's native council assignment. Its native effects are preserved. Eligible targets gain a refreshed 90-day favor modifier worth **+10 senior civilian appointment score in the sponsoring realm**. It is separate from service evidence and does not bypass qualifications. County/duchy score order is unchanged.

## Personality, politics and player consequences

| Influence | Implemented direction |
|---|---|
| Just / Honest | Lawful order, qualification and resistance to corruption |
| Diligent / Patient / Humble | Professional choices and competence |
| Lazy / Impatient / Content / Shy | Continuity/default selection biases |
| Ambitious | House, political clients, actual shared faction and house-bloc ties |
| Family Hierarch / Gregarious | Eligible family and friends |
| Vengeful / Forgiving | Stronger/weaker penalties for personal rivals and hostile-house relations |
| Paranoid / Trusting | Distrust of rivals / greater acceptance of endorsements |
| Greedy / Arbitrary / Deceitful | Greater weight toward private obligations or personal preference |
| Zealous / Cynical / Loyal / Arrogant | Faith, practical skill, loyal connections or personal connections |
| Compassionate / Callous | Different tolerance of documented performance concerns |

Preferences combine under the existing bounded ministerial score; they do not override eligibility. Native factions, house blocs and designated political clients are distinct inputs.

Player consequences occur on commitment, not browsing:

- Personal nominations more than five public-suitability points below the professional comparison: **15 base Stress each for Just and Honest** after successful appointment.
- Appointing a personal rival: **15 base Stress for Vengeful** after success.
- Accepting a bribe: **25 base Stress each for Honest and Just**.
- Appointing a qualified relative is not automatically corrupt.

Tooltips explain these consequences. Normal game stress modifiers may alter final amounts.

## Patronage and Chancellor oversight

Each accepted payment has a passive durable story record: payer, minister, amount and date. Successful senior appointment can link that record to the posting. The existing active obligation lasts up to three years or one successful sponsored appointment. Expired obligations do not earn appointment linkage. Private bribery preference is not advertised as public native candidate score. No criminal proceeding is started while Censor?Justice is disabled.

Chancellor priorities weight routine AI choices. An explicit imperial professional/continuity instruction binds the Chancellor. Imperial discretion withdraws that instruction and permits Chancellor direction again.

Appointment confirmation is a separate realm law:

- **Delegate Senior Appointments**: routine Personnel appointment.
- **Reserve Empire Appointments**: empire-tier public nominations need confirmation.
- **Confirm Every Senior Appointment**: all senior nominations need confirmation.

Changing confirmation law costs 150 Prestige, requires peace and has a five-year cooldown. Existing submitted recommendations retain their confirmation requirement.

## Implementation completion checklist

- [x] Task-based reviews, endorsements and poor-service consequences.
- [x] Favor-based native senior candidate-score addition.
- [x] Senior vacancy custody and promotion/source handling.
- [x] Native resignation transfer bridge with vanilla fallback.
- [x] Current candidate refresh, marked shortlist and stable displayed choices.
- [x] Personnel and imperial notification queues, deferral/resume and timeouts.
- [x] Political preferences, contextual player stress and payment history.
- [x] Chancellor priorities and binding imperial instructions.
- [x] Imperial confirmation laws and approval/return flow.
- [x] Legacy forced-transfer mutation gates disabled and proposal migration added.
- [x] Role-owned decisions, naming cleanup and obsolete menu retirement.
- [x] Register window/launcher unregistered; judicial runtime still disabled.
- [x] Static structural/reference/localization audit.
- [ ] Combined CK3 playtest and error-log review with the user.

## Combined playtest

Use a disposable save for the first custody tests.

1. Confirm the register is absent and each role sees only its own decisions/interactions.
2. Check county/duchy succession remains native.
3. Trigger one clean senior governor death; inspect temporary custody, exact titles and vassals.
4. Appoint an unlanded candidate, then test a serving candidate with a source successor.
5. Test native resignation and a senior-source promotion.
6. Mark a new candidate, refresh, and verify the visible name matches the appointed person.
7. Open several vacancies: check queue, defer/resume, role turnover, timeout and save/reload.
8. Exercise all three appointment-authority laws, imperial return and unanswered confirmation.
9. Compare trait-driven AI choices; inspect stress, patronage history and advancement/favor/poor-service scores.
10. Switch council assignments: confirm observation gaps and recordkeeping behavior.
11. Review fresh error/debug logs and tune scores after functional results are known.

## Verification and maintenance

Static source checks passed in dev.33. They do not execute CK3. Title transfer, saved-event scopes, AI behavior, interface layout and save compatibility remain unverified until the combined playtest.

Native bridges are pinned to the installed game scripts: Manage Talent, civilian appointment score, custody validity and governor resignation. Recompare these after a game update. Existing already-imposed judicial outcomes are not reversed; essential release cleanup remains active.

Detailed prior progress is retained in `PERSONNEL-REVAMP-HISTORY.md`; static verification scope is in `PERSONNEL-STATIC-CHECKS.md`. Update this document after fixes and replace the pending playtest box only when actually verified.

## Playtest issue: Henan vacancy ? dev.33

User killed Henan's governor and received no Personnel appointment. The game log confirmed two unknown `clear_list` effects in the vacancy/refresh code and missing UTF-8 BOM warnings. Replaced the unsupported command with native list-element removal and normalized script encodings. The incumbent filter now also accepts appointment succession inherited from the holder's realm law, matching the mod's existing governor eligibility pattern.

The exact failed runtime gate for Henan was not recorded in dev.22, so this is not yet a verified gameplay fix. Added `MAM_PERSONNEL_VACANCY` stage diagnostics: callback reached, custody filters passed/rejected, minister missing, candidate pool empty, custody acquired or postconditions failed.

Interaction cleanup: hid standalone legacy credential/dossier actions and retained their details within Review Official. The obsolete governorship-review action remains hidden. Mark/client actions exclude self, emperor and current ministers; bribes target the actual Personnel officeholder. Updated the marked-candidate description to refer to the new shortlist.

Retest: fully restart CK3, reload a save from before the governor's death, repeat the death and advance at least two days. The event is scheduled one day after successful custody. Already completed vanilla succession is not retroactively reversed. Inspect fresh `MAM_PERSONNEL_VACANCY` lines if no event appears. Static structure/encoding checks pass; engine retest remains pending.

## Playtest issue: empty candidate event ? dev.33

The Henan screenshot confirms the event opens after successful custody. Debug log confirms candidates were found before custody. Error log then records repeated attempts to define temporary `mam_emperor` where that permanent saved scope already exists. Removed the conflicting target declaration; callers already establish the permanent emperor reference.

An empty candidate refresh now retains the original shortlist references rather than deleting them. Added scan/native-validity/merit/full-eligibility counters and `MAM_PERSONNEL_POOL` diagnostics. Corrected a separate disabled rebellion on_action whose feature gate was incorrectly placed outside its effect block, as reported by the engine.

Static checks pass. This addresses the logged scope error; the full empty-list behavior requires an engine retry. Restart CK3 with dev.33, then reopen or refresh the pending appointment. A saved custody file can be retained; repeating the original death is unnecessary if that file was saved. If candidates are still absent, pool diagnostics distinguish native eligibility, merit and later restrictions.

## Shortlist refinement ? dev.33

User requested separate lateral transfers and promotion/first-office alternatives.

- The original vanilla-order candidate remains available when eligible, explicitly labeled lateral transfer, promotion or first office grant.
- Independent category slots now search for an eligible same-tier transfer, a lower-tier governor for promotion, and a candidate without a territorial public office. Each category excludes the original default, so a same-tier default cannot occupy the only promotion/unlanded alternative slot.
- Slots appear only when an eligible alternative exists; candidates are not generated and qualifications are not waived to fill a category.
- Minister-preferred and marked options also display their appointment type. The professional comparison remains internally available for contextual stress.
- Classification ignores nominal family/estate and other landless titles. Higher-tier territorial officeholders are explicitly excluded from lower-tier vacancies.
- Clean empire-tier source offices are included in the source-governor adapter. All existing custody, source-replacement and imperial-confirmation checks remain in force.
- Static checks passed; event labels, pool results and transfers still require in-game verification. Refresh a pending event after restarting with dev.33 to rebuild the new category slots.

## Empty-list investigation ? dev.33

Both Henan and Qingxu reached custody with eligible candidates before the event opened. Later logs report unset refresh-counter variables during visible-event tooltip simulation, so those zero-count messages cannot establish that real candidates failed merit.

Candidate preparation now runs in a dedicated hidden event (`mam_senior.3`), which saves shortlist scopes before opening the visible chooser (`mam_senior.1`). Refresh also goes through this preparation event.

Installed vanilla reference: `game/common/character_interactions/06_ep3_interactions.txt` reads `scope:target.min_appointment_level` before checking candidate qualification. The mod now captures that exact native requirement before temporary imperial custody, together with certification that the original title used appointment succession. Post-custody eligibility retains the captured requirement instead of inheriting a different custodian-dependent view. This avoids estimating a threshold from the available candidate pool.

Static checks pass; in-game resolution of the empty-list issue remains unverified. Reload a pre-vacancy save for the next test because older pending stories do not contain the newly captured qualification baseline.

Vanilla installation is read-only reference material. All edits and native-function overrides are inside the mod directory; no installed game files have been edited.

## Appointment presentation ? dev.33

The user's screenshot confirms candidates now appear. The next issue is presentation, not a certified transfer outcome.

- Replaced the procedural paragraph with a short appointment introduction and a readable shortlist.
- Candidate names in the body use native linked character names for quick inspection; buttons remain the separate appointment action.
- Added two conditional native character portraits using distinct eligible shortlist members.
- Shortened buttons to Transfer, Promote or First grant plus the name. Default/ministerial/marked roles move to muted shortlist annotations and tooltips.
- Replaced context-losing character Custom labels with native event-context conditional names. The unsupported-looking fallback rank label and broken question-mark separators are no longer used by active options.
- Minister-preferred and marked choices are suppressed when the same character already appears in an earlier slot; linked rows use the same predicate as their buttons.
- Static event/localization/link checks pass. Actual layout, portrait placement and click behavior require the next in-game view.

## Choice-basis highlighting ? dev.33

User requested clear indication of non-default or biased nominations.

- Default candidate keeps a green Order badge, including when a relationship also warrants disclosure.
- Yellow badges disclose family ties, political connections, friendship and positive trait preference. They do not label a qualified relative or faction member criminal.
- Red badges identify an active paid obligation, family favoritism combined with a material professional shortfall, or a materially weaker public record.
- Neutral alternatives remain labeled Alternative/Your choice. Transfer/promotion/first-grant labels are retained.
- One highest-priority badge keeps each choice compact; hover text lists all applicable reasons. Native shared faction, shared house bloc and designated client are explained separately.
- All six candidate options retain their original appointment effects, eligibility and stress rules. This is presentation only; no new punishment or disqualification was added.
- Static structure, localization-reference and unchanged-appointment-call checks pass. In-game formatting and tooltip context still require verification.

## Relevant consequences and marked nominees ? dev.33

- Removed unconditional Just/Honest/Vengeful warning text from all candidate choices.
- Native `show_as_tooltip` stress previews appear only for relevant traits and circumstances: Vengeful plus personal rival, or Just/Honest plus a personal recommendation materially below the professional comparison. Display-only previews do not apply stress twice.
- Tooltips disclose the title/source-office outcome, imperial confirmation where required, endorsement consumption only when present, and fulfillment of an active recorded paid obligation only when applicable.
- Actual eligibility, effects and stress rules are unchanged. Deferred approvals revalidate the appointment before applying consequences.
- Removed Review another shortlist. The existing candidate rebuild still runs when opening an appointment; it does not pretend to offer a second page of candidates.
- An eligible marked candidate remains included. Duplicates appear once. Marking after the event opens requires setting it aside and reopening through Resume Senior Appointments; the marking interaction now explains this.
- Static checks passed; native tooltip formatting and modifier-adjusted stress amounts require the next in-game hover check.

## Natural event prose ? dev.33

Removed the candidate roster and UI instructions from the appointment body. The vacancy now has a short court narrative; candidates appear in natural-language options. Candidate names are bold and destination titles highlighted. Transfer/promotion/first-grant distinctions and colored choice-basis badges remain. Character links remain available in tooltips.

Rewrote active service-review, ministry-direction, appointment-authority, confirmation and private-payment prose/options. Decision names retain the Personnel prefix. Authority costs, direction effects and exact mechanical consequences live in tooltips. Poor-service assessment only previews Compassionate stress when the minister has that trait.

Static structure and presentation localization checks passed. Gameplay and eligibility are unchanged. The longer highlighted option labels still need an in-game layout check.

## Sequential vacancies, markup and Ministry category ? dev.33

Playtest reports: appointments stopped appearing after the first; options showed ERROR before their colored tags. Logs show later death hooks still firing, several empty eligible pools, and lost nominee/source references inside a nested source-office transfer.

- Source-office custody now uses its own source-file alias. Destination file, nominee, office and source successor are restored from dedicated snapshots, replacing the transfer-variable path named in the engine errors.
- Queue release compares an explicit file identity rather than nested prev scope. Completed, submitted and deferred work hands control to the next pending file. A failed commit releases its lease, briefly snoozes that file, and reports failure rather than silently closing the only notification.
- A genuinely empty pre-custody pool now sends Personnel an explanation before retaining native succession. It is not reported as a queue failure or filled by inventing an ineligible candidate.
- Removed literal square-bracket badges: CK3 parsed Order/Weaker record/Alternative as invalid localization expressions. Colored plain-text labels remain.
- Added `interaction_category_ministry`, displayed as Ministry, and assigned all mod-owned ministerial interactions to it. Future ministerial interactions should use that key.
- Category definitions are mod-local and preserve contiguous indices. The user's Divine Intervention category is retained at index 17, with Ministry at 16; the native category mappings are preserved. No installed game or workshop files were changed.
- Static structure/reference/category checks passed. Sequential appointment success and source-office outcomes still need an engine retest. Restart and use a pre-appointment save for the first verification because earlier failed transactions may have left a pending file.

## Native succession and marked-candidate repair ? dev.33

The Huainan playtest exposed a design error: the mod called the whole appointment pool empty when candidates failed its added source-office replacement requirements. That statement did not describe vanilla's order.

Changes:

- A recorded living local native successor is retained independently of the screened alternatives, including when additional ministry policy blocks selection. An unavailable native candidate is shown with requirements instead of disappearing.
- Removed the manual title-grant validator and unlanded-source-successor requirement from pre-custody screening. The native engine's destination appointment and merit checks remain; source-office transfer planning is separate.
- Persist the engine-qualified pre-custody pool. After custody, candidate revalidation can recognize that certification while still checking current life, age, realm, imprisonment, merit and rank.
- Safe source transfer remains required at commitment. Lower source offices use the native step-down succession effect rather than demanding an unlanded replacement; supported senior source offices enter their own custody files. Compound/unsupported sources are blocked visibly, not described as an empty native order.
- Directly inject the marked person into pre-custody and refresh searches. Store the actual mark even when no automatic alternative qualifies. Reserve their own visible option, including if they are also the native default; categories and the preferred slot do not consume it.
- Invalid marks remain visible and disabled, with relevant reasons for death, age, prison, realm change, insufficient merit, examination policy, higher rank or unsupported source bundle. Disabled choices do not preview phantom stress or modifier consumption.
- Nomination and imperial approval mutations now run through hidden events 7 and 8. Visible choice tooltips no longer simulate new custody records or native source transfers. The log's source-file errors occurred during that preview path.
- Static regression checks passed. Runtime success remains unverified; no claim that the engine test has passed.

Required edge-case playtest matrix:

| Case | Expected result |
|---|---|
| Native default has no territorial office | First grant remains available if normal qualifications pass |
| Native default holds same-tier office | Transfer appears; source arrangements are separate |
| Native successor of the source is landed | This alone does not reject the destination candidate |
| Source is a supported senior office | Separate Personnel custody file and queued appointment |
| Source has unrelated/compound land | Candidate visible but transfer blocked; no unrelated land stripped |
| Native default lacks a separate examination degree | No custom recruitment-law filter remains; native qualifications still apply |
| Mark lies outside automatic top scores | Dedicated marked option if eligible |
| Mark equals default or preferred candidate | One marked option; default-order status preserved for consequences |
| Mark dies, is imprisoned, changes realm or loses eligibility | Disabled option and relevant reason, no silent omission |
| Mark changes while an event is open | Existing snapshot stays stable; reopening rebuilds from the current mark |
| Multiple vacancies and a deferred file | Other files proceed through the queue |
| Personnel/emperor changes before confirmation | Current authority and candidate state rechecked |
| Save/reload with a pending file | Native certification, mark reference and queue survive; old pre-certification files need a pre-vacancy retest |

## Appointment log review and sponsorship opinion ? dev.33

Latest user playtest log records three completed destination grants, each with custody and a nonempty post-custody pool. A later unsupported civilian-contract check correctly retains native succession. This confirms the basic tested appointment paths, not every edge case or administrative consequence.

The error log is not clean: two copied native tooltip strings (`has_appointment_succession_tt` and `promote_candidate_interaction_existing_holder_tt`) account for roughly 25,000 repeated localization errors because they expect a native `target` data scope. Replaced those text references inside the mod-owned bridges with scope-independent mod strings. Fixed the inactive register-widget file's BOM. Vanilla/other-mod warnings remain outside this change.

Successful ministry-nominated appointments now grant the appointee +10 opinion of the actual nominating minister for five years, reusing Sponsored My Appointment. The modifier does not stack. Credit is bound to both sponsor and candidate, awarded only after the destination grant succeeds, and skipped for dead/out-of-realm sponsors. A returned recommendation clears sponsorship. Automatic fallback alone creates no sponsor credit. Native opinion previews appear on candidate and approval tooltips. An emperor confirming a recommendation does not steal the Personnel minister's sponsorship credit.

Static checks pass. New opinion behavior and fresh-log cleanup require a restart/retest.

### Next tests, in order

1. Mark an eligible person outside the automatic shortlist. Open a vacancy and choose the dedicated marked option. Inspect the appointee's opinion of Personnel: +10 Sponsored My Appointment for five years. Repeat nomination/return/failure: no duplicate or premature bonus.
2. Choose a lateral transfer and then a lower-tier promotion. Inspect BOTH source and destination: correct holders, lieges, counties/vassals, no extra governorship or family-property loss. A senior source gets queued; lower sources follow native succession.
3. Set Confirm Every Senior Appointment. Nominate, return once, then approve. No title/opinion/stress change before actual grant; correct sponsor receives opinion afterward.
4. Queue several vacancies, defer one, save/reload and replace Personnel. Work resumes for the current minister with no stale click grants or queue lock.
5. Check Manage Talent service observation/three-year endorsement and poor-service assessment; switch to Bestow Royal Favor and verify only the intended native senior scores change.
6. Exercise an active bribe, a below-benchmark personal nominee and a Vengeful rival appointment. Check relevant native stress/opinion previews against actual results. County/duchy succession and Censor?Justice suspension remain unchanged.

## Obsolete law cleanup ? dev.34

- [x] Retire all nine laws in the four obsolete groups; hide the groups and prevent default adoption.
- [x] Remove the old player/AI policy menus and disable their setters. Queued old menu events resolve silently.
- [x] Add idempotent saved-law/cooldown cleanup at campaign startup, affected rulers' quarterly pulse, and ongoing emperor maintenance.
- [x] Preserve the two current law groups, Chancellor Personnel priorities, and appointment eligibility/confirmation logic.
- [x] Static structure, references, retired-law acquisition paths and encoding checks.
- [ ] Restart CK3 and load the existing save: only senior appointment authority should be available among mod laws. Check that its selection remains intact and a fresh senior vacancy still resolves normally.

## Simultaneous vacancies and territorial empire offices - dev.35

The latest log records two senior deaths at 20:32:46 and 20:32:48, successful custody for both, then one completed appointment at 20:32:51. A lateral transfer also creates a source custody file in that sequence. This supports the reported queue problem; the log alone cannot prove the final vassal hierarchy. The old grant had no persistent vassal snapshot or explicit vassal reassignment after custody.

Implemented changes:

- Every captured file receives its own realm-owned queue entry and monotonic queue position. A second death cannot replace the first entry. Source vacancies from lateral transfers use the same index.
- File release schedules a fresh minister callback after the current event finishes. Oldest eligible work is selected; deferred and imperial-confirmation cases do not block other nominations. Imperial recommendations also wake the next confirmation after resolution.
- The preparation callback binds to the realm's current lease, rather than inherited scopes from a different death or nested capture. A per-lease presentation flag prevents duplicate callbacks from opening the same case twice.
- The queue can rebuild older pending files from owned stories. Completed entries are removed from the live index. Existing lease checks still prevent duplicate simultaneous popups.
- Before custody, record the primary title of each territorial direct vassal in that office. Recording titles allows a vassal's successor to be recognized if the vassal dies during custody.
- Grant only the saved personally held component titles and the principal office; explicitly set the appointee's liege. Then reassign eligible recorded vassals after the recipient has their new rank. No broad scan of the emperor's vassals is used to reconstruct a missing jurisdiction.
- A surviving recorded vassal must still be the emperor's direct vassal, remain within the jurisdiction, retain that primary title, and hold no unrelated territorial bundle. Foreign or separately reassigned characters are protected.
- If an eligible recorded vassal remains with the throne after reassignment, retain a repair flag and retry on the story's 30-day pulse. Abandon that retry if the appointee/title/realm relationship no longer matches.
- Clear the ephemeral title-bundle list before each separate custody operation.
- The current minister can use Resume Senior Appointments when an old lease belongs to a former minister, has expired, or points to a resolved/missing file; a valid current popup remains protected.

| Edge case | Implemented behavior | Verification |
|---|---|---|
| Two independent kingdom governors die together | Two custody files; FIFO nomination events one at a time | New engine retest required |
| First choice is a lateral transfer | Its newly vacant source is indexed separately behind older waiting files | New engine retest required |
| One file is deferred or awaiting the emperor | Other eligible files can continue; separate confirmation queue | New engine retest required |
| Territorial empire-tier civilian governor dies | Included when native appointment law, civilian contract, direct-liege and clean-jurisdiction checks pass | New engine retest required |
| Empire governor personally holds a kingdom inside that empire | One empire-level appointment transfers the recorded kingdom and lower component titles with the jurisdiction; no duplicate kingdom event for the same bundle | New engine retest required |
| Empire governor also holds an unrelated kingdom outside the empire | Whole succession retains native handling; explicit mixed-jurisdiction diagnostic. Splitting independent offices is not implemented | Existing safety boundary |
| Higher-tier governor considered for a lower-tier vacancy | Remains excluded as a downgrade; same-tier transfer and lower-tier promotion are distinct | Existing eligibility rule |
| Recorded vassal dies while the office is in custody | Use the title's current holder, with current realm/liege/jurisdiction checks | New engine retest required |
| Recorded vassal gains unrelated land, changes liege, or leaves the realm | Do not forcibly collect that character into the new jurisdiction | New engine retest required |
| Existing file was created before vassal snapshots | Recover its queue entry, but do not guess its former vassals | Compatibility limitation |

Retest from a save BEFORE the two deaths, using dev.35 after restarting CK3. An already damaged save does not contain the new pre-custody vassal records, so this cannot automatically reconstruct vassals lost by old completed appointments.

First kill two independent kingdom governors before answering either event. Complete the first appointment, advance up to two game days, then complete the second. Inspect each new holder's direct vassals and personally held titles; check that unrelated imperial vassals stay with their existing liege. Repeat with one lateral transfer, then with a territorial empire governor holding a kingdom inside their empire. Under Reserve Empire Appointments, that combined empire bundle must reach imperial confirmation.

Static block, reference, encoding and queue/jurisdiction wiring checks pass. No claim of in-engine repair verification is made yet.

## Central ministerial succession and recruitment cleanup - dev.36

See [Ministerial succession approval](MINISTERIAL-SUCCESSION-REVAMP.md) for the complete flow, current implementation and combined playtest matrix.

| Approving authority | Ministries | Entry points |
|---|---|---|
| Chinese emperor | Chancellor, Censor, Grand Marshal | Queued succession review; Ministry: Endorse an Upper Minister |
| Grand Chancellor | Personnel, War, Rites, Works, Revenue, Justice | Queued succession review; Ministry: Endorse a Lower Minister |

The native successor takes office first. The superior can confirm that minister, choose a qualified professional alternative, back a personal preference, or choose their marked nominee. Natural event prose replaces a candidate roster in the description; option names link/highlight the characters and identify the ministry. Marked candidates are explicitly included, with unavailable choices explained when eligibility changes. Separate upper/lower FIFO queues bind to the Chinese imperial title and the current approving official. Deferral lasts 30 days; no timeout silently approves a succession.

Native ministry title/council handoff is used for replacement. Success requires both title and council seat to match. Actual confirmation gives the minister +10 opinion of the approving superior for five years; replacement gives the displaced incumbent -20 opinion for five years. These modifiers do not stack. Choosing a replacement more than five professional points below the best qualified comparison causes 15 base Stress each for Just and Honest; confirming or choosing a rival causes 15 base Stress for Vengeful. Previews are conditional and consequences apply only after success.

The custom Civil Recruitment Standards law is removed at the user's request. Mixed, Preference and Strict are inert compatibility keys; the law group, policy decision and old menu are unavailable. There is no law bonus or separate strict examination gate in current provincial or central ministerial nominations. Examination qualifications and distinctions still contribute their existing candidate-assessment points, while native appointment eligibility and required merit remain. The obsolete recruitment-law line is removed from the credential breakdown. Saved selections and the old recruitment cooldown are cleaned by the existing retirement migration.

Censor-Justice case processing and the register remain disabled. Reviewing succession to Censor or Justice does not enable the judicial loop. Vanilla files are unchanged.

## Law icons, descriptions and imperial audience - dev.37

The three appointment-authority laws now supply their own native-format 96 by 96 DDS icons. The source artwork is copied unchanged from the installed game's `gfx/interface/icons/laws/` folder into the mod under the exact custom law names. Native law UI tinting supplies the gold/grey states and decorative frame.

| Mod law | Native icon source | Meaning |
|---|---|---|
| Delegate Senior Appointments | imperial_bureaucracy_0.dds | First scroll: Personnel settles kingdom and empire appointments |
| Reserve Empire Appointments | imperial_bureaucracy_1.dds | Second scroll: only empire nominations reach the throne |
| Confirm Every Senior Appointment | imperial_bureaucracy_2.dds | Third scroll: both kingdom and empire nominations require confirmation |

The native law tooltip reads `Law.GetEffectDescription`, so the prior `_desc` strings alone were not shown there. Added `_effects` text for all three laws: kingdom/empire handling, the applicable civilian-office scope, the separate county/duchy and central-ministry rules, and the existing 150 Prestige/peace/five-year change requirement. Law behavior and costs are unchanged.

The provincial imperial-confirmation event now stages the current Personnel minister presenting the papers on the left and the nominee on the right. The emperor substitutes for an unavailable minister; a dead nominee is not given a live portrait. Portrait scopes are prepared before the queued event and rebound when it opens. The title identifies the jurisdiction; narrative and choices use natural language with linked/highlighted person and office names.

Approval previews identify first appointment, lateral transfer or promotion, the recorded jurisdiction grant, a consumed service endorsement where relevant, actual sponsorship opinion, and only applicable stress/obligation consequences for the original Personnel recommender. They do not assign that minister's stress to the emperor. Sponsorship preview checks the nominated-candidate binding. Approval availability also checks the same source-office readiness used by commitment. Return and pending-review choices explain their existing 30-day reconsideration and 90-day unanswered-recommendation behavior.

Static structure/reference/encoding checks pass across 219 scripts. Icon files have valid DDS headers, native dimensions and hashes identical to their sources. No vanilla files are changed. Restart CK3 to check the law row and hover text, open a reserved recommendation and confirm both portraits, then compare approval tooltips with the actual appointment. Final in-engine appearance and behavior have not yet been verified for this build.

## Native law-tooltip formatting - dev.38

Reformatted all three appointment-authority effects descriptions to match the provided vanilla examples: one effect per bullet, native three-character hanging indents for wrapped lines, linked game terms, and ordinary tooltip text. Removed the bold mini-headings, long scope paragraph and repeated manual cost paragraph. Each choice now has four bullets: kingdom handling, empire handling, unchanged county/duchy succession, and separate central-ministry/imperial succession rules.

Enactment requirements, prestige cost and the click-to-pass footer remain supplied by the native law interface. These laws are mutually exclusive rather than cumulative. No appointment rules, costs, modifiers or succession behavior changed. Checked localization syntax, formatting tags, native concept references and BOM; final appearance requires a restart/reopen in CK3.

## AI and council-assignment audit - dev.39

See [Personnel AI and assignment audit](PERSONNEL-AI-AND-TASK-AUDIT.md) for confirmed issues, implemented fixes, exact AI roles, remaining balance risks and practical test steps.

Royal Favor refresh is now independent of native side-effect throttling. Manage Talent starts/resumes baselines without waiting for the annual sample, processes observation gaps before annual judgment, and AI commendation clears old adverse assessment. Career scores are scoped to native civilian governor appointments, with promotion-only endorsement guards. The logged dead-owner appointment-story handoff is guarded with living-holder/heir selection.

AI provincial approval now has explicit quality/personality weights. Professional nomination weights are normalized across available candidate categories, patronage bonuses require relevant connections, and standing marks remain usable after a player minister becomes AI. AI Chancellors can issue annually renewed priorities through a quiet controller; explicit imperial and non-AI instructions remain protected. Task choices/targets and autonomous custom-law changes are not added to that controller.

The +20 endorsement, +10 favor, -10 adverse score, three-year evidence/modifier durations and 90-day favor duration remain the first-pass balance values. AI praise thresholds, lifetime baselines, latched war flags, native task switching and repeated lateral moves need measured testing. Keep Review Official as the Manage Talent action; consolidating the separate Service Dossier into that window is recommended. The records themselves remain necessary, and no review interface has been removed in this audit.

## Exam First Rank integration - dev.40

The existing examination distinction hooks now have visible honors. The palace-exam slot in the native Merit tooltip and Government Administration shows the highest recorded honor with its own reward tooltip. Workshop artwork is bundled locally; the older standalone mod is unnecessary. Capped career Merit and vanilla examination eligibility are retained as requested. Palace results use native finalized placement variables, rather than re-sorting entrants after reward callbacks.

See [Exam distinctions and integration](EXAM-DISTINCTIONS.md) for provenance, reward values, compatibility limits and the engine test checklist. Static validation is separate from in-game confirmation; final layout and callbacks remain to be tested after restart.

## Laureate careers and visible honors - dev.41

Implemented permanent, dynamically graded Examination Laureate recognition, +5 mutual laureate opinion, upgrade-only Prestige rewards (150/300/600), a player achievement event and a portrait-based imperial audience for new champions/Threefold Laureates. Imperial choices provide congratulations, public commendation or paid five-year career sponsorship; authority, scholar, realm and acknowledged-grade guards protect stale events. Merit remains capped at 50/100/150.

The Merit tooltip now has an always-visible three-badge honors row, with dim unearned icons and earned stamps. The earlier earned-only palace replacement could not demonstrate that the UI was present for an unranked character. Existing recorded honors can gain the permanent trait without retrospective rewards; generic old passes cannot reveal finishing position.

Senior and ministerial options label laureates. Professional approval authorities respect their achievements, and demonstrable favoritism over a stronger eligible laureate can cause a success-only, nonstacking -10 opinion consequence. Conditional tooltips show applicable effects. The rejected six-decimal AI factor found in the current log is shortened to 0.333.

See [Examination honors and laureate careers](EXAM-DISTINCTIONS.md) for exact values, implementation boundaries and twelve engine tests. Structure/reference/encoding/native-parity checks pass across 231 common/event scripts; final UI and gameplay remain unverified in CK3.

## Personnel revamp closed - 2026-10-27

The user has officially completed the Personnel revamp. Dev.41 is the accepted baseline, including senior appointments, ministerial approvals, Manage Talent, Royal Favor, AI behavior, law presentation, and examination honors/laureate recognition. No further Personnel redesign is planned unless requested. Future reported defects can be handled as maintenance against this baseline.

Censor and Justice remain disabled pending their separate simplified revamp; the register remains disabled. Earlier source-check reports and engine-test checklists remain as historical verification records. User acceptance closes the feature scope and does not retroactively mark unperformed tests as executed.

## Jurisdiction and nested kingdom maintenance - dev.43

Fixed the snapshot/restoration gaps that could leave recorded lower titles with a custodian, and extended Personnel appointments to kingdom offices beneath civilian territorial empire governors. The handover now tracks personal baronies and subordinate holdings, restores recorded land and vassals, and resolves a kingdom's current eligible de-jure empire governor at commitment. Specific-office claims protect simultaneous kingdom/empire files; parent appointment completion wakes waiting kingdom attachments.

Both normal and promotion-source custody use the same helpers. A one-time safe repair pass uses existing saved records; it cannot reconstruct old unrecorded holdings. Conditional option-name scope guards address the unset-target errors in the current log.

See [Jurisdiction and nested-kingdom maintenance](PERSONNEL-JURISDICTION-FIX.md) for source findings, exact boundaries, 20 source/graph scenarios and the engine checklist. Native succession/title transactions still require testing from a save before vacancy capture. Personnel remains the completed revamp; this is maintenance and the specifically requested nested-office extension.

## Empire option error corrections - dev.44

The live log identified an empty lateral candidate being displayed through the default candidate's unavailable rule, plus illegal independent transfers of county capital baronies. The option now requires its own candidate, preview/selection paths guard missing characters and benchmarks, and custody/commit/recovery share a capital-safe transfer predicate. County capitals follow their county; noncapital holdings remain explicit recorded parts.

All 28 focused source/graph scenarios pass after adding missing-candidate and native capital-barony regressions. See the dev.44 section of [Jurisdiction maintenance](PERSONNEL-JURISDICTION-FIX.md) for the exact log evidence and fresh-engine retry checklist.
