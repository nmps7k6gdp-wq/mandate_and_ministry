# Ministerial succession approval

Build: 0.4.0-alpha.20-dev.37
Status: implementation complete; static source verification passed; engine playtest pending.

## Requested behavior

- A deceased minister's successor inherits the ministry and council authority through native succession first.
- The Grand Chancellor reviews Personnel, War, Rites, Works, Revenue and Justice.
- The Chinese emperor reviews Chancellor, Censor and Grand Marshal.
- The review always includes confirmation of the installed successor, with qualified professional, personal-preference and marked alternatives when available.
- Emperor and Chancellor have independent ministry-candidate marks. These do not replace Personnel's provincial-candidate mark.
- Natural event prose, linked/highlighted names and office titles, relevant trait consequences and clearly labelled personal preferences follow the Personnel event presentation.

## Implementation boundaries

- Trigger on minister deaths, not campaign setup, ordinary manual hiring or dismissal.
- Native ministry/council effects perform replacement. No provincial custody or temporary imperial ownership of ministries is introduced.
- No obsolete laws, register UI or Censor-Justice case processing are re-enabled.
- A lower-ministry review cannot appoint the Chancellor, Censor or Grand Marshal into a lower seat through this route.
- Marking does not override native eligibility. The incumbent keeps governing while a review is deferred; an unanswered review is never automatically approved.
- Existing ministers can be considered where native hiring allows it. Native council/title handoff handles any resulting move between ministries.

## Work checklist

- [x] Death markers and deferred capture after inheritance.
- [x] Per-office review records and separate upper/lower queues.
- [x] Native ministry qualification checks and role-specific professional/personal scoring.
- [x] Approval and alternative appointment effects, with stale-event validation.
- [x] Separate mark/clear interactions and role-owned resume/clear decisions.
- [x] Natural event/localization, contextual stress and opinion previews.
- [x] Persistent records, simultaneous-death queues, authority revalidation and incumbent-change guards implemented; corresponding engine tests remain pending.
- [x] Static checks and update to the main revamp document.
- [ ] Combined in-game test.

## Current controls and selection

Use the Ministry interaction category. The emperor can Endorse an Upper Minister; the Chancellor can Endorse a Lower Minister. Each mark is personal to that authority, persists until withdrawn and applies to that authority's next relevant review. Existing Personnel provincial marks are separate. Clear the endorsement on the marked character or through the role-owned Clear My Ministerial Nominee decision. Resume Succession Reviews appears only when that authority has pending cases.

The installed successor is always shown as the confirmation choice. A qualified professional alternative, a distinct personal-preference alternative and a distinct marked nominee appear when available. The marked person is excluded from the two automatic alternative slots to avoid duplicate choices. If the mark is already the installed successor, confirming them fulfills the endorsement; there is no duplicate marked button. An invalid marked nominee remains visible as unavailable with current reasons.

Professional comparison uses existing merit, examination evidence, distinctions and skills, plus 1.5 times the native council seat's principal skill: Diplomacy for Chancellor/Personnel, Intrigue for Censor, Martial for Grand Marshal/War, Learning for Rites/Justice and Stewardship for Works/Revenue. Personal comparison adds bounded existing personality/patronage preferences and family, friend and faction connections. Native qualification, availability and title-specific merit gates still control alternatives. A standing endorsement does not waive them. There is no custom recruitment-law bonus or extra strict examination gate.

Approval does not regrant a title already held by the installed minister. Replacement enters the native ministry handoff, with an explicit owner and council-seat synchronization fallback. The operation must leave the selected person holding both ministry and council seat before completion, credit or stress is recorded. If a partial native handoff leaves a different living holder but the seat is not synchronized, the review is retained for that actual holder instead of silently dropped.

## Consequences

- Confirmation/replacement: appointee gains +10 opinion of the actual approving emperor or Chancellor for five years; non-stacking.
- Replacement: displaced incumbent gains -20 opinion of the approving authority for five years; non-stacking.
- Choosing a replacement more than five professional points below the best currently qualified comparison: 15 base Stress for each of Just and Honest.
- Confirming or selecting a personal rival: 15 base Stress for Vengeful only.
- Relevant native opinion/stress previews appear in the choice tooltip. Failed, canceled, deferred or stale choices receive no custom success credit or stress.
- Player incumbents/appointees receive a brief outcome notice. Native council/title side effects follow the normal ministry handoff.

## State and edge cases

The death callback arms only the dead minister's actual office titles. A delayed callback waits for a living successor to hold each ministry, then creates one record per office. Late native title gain can finish an armed handoff. Initial setup, ordinary dismissal and routine manual hiring do not independently create reviews.

Files and queue positions are persistent on h_china, so changing the emperor's primary title does not redirect the queues. Emperor and Chancellor have separate leases and duplicate-presentation guards. Prepared events read the live lease and bind all candidate names before display. A current matching title holder, exact per-title record, actual authority and matching displayed incumbent are required again at commitment. Old events cannot replace a newer successor.

While a review is open, its minister exercises native authority. If the Chancellor dies, lower reviews wait for a valid replacement Chancellor and then bind to that new official. The emperor's successor inherits upper review responsibility; story ownership uses a living new holder or living title heir during succession. An imprisoned emperor does not invalidate pending files; upper reviews wait while an available Chancellor can continue lower reviews.

The custom recruitment law is retired alongside this feature. Only senior territorial appointment authority remains as a custom law group. Censor-Justice case processing and the register are not enabled by ministerial succession review.

## Combined playtest matrix

All items below require engine verification after restarting with dev.37:

1. Play the Chinese emperor; mark a qualified candidate, then kill Chancellor, Censor and Grand Marshal separately. Confirm each successor already holds title and seat before the review. Test approve, professional alternative and marked alternative. Check the designated Secretary Director follows existing native laws when an upper minister changes.
2. Play the Chancellor; mark a qualified candidate, then kill each of the six lower ministers. Only the Chancellor should review them. Confirm a successor, replace one, and inspect both title and council seat. The emperor's upper mark and Personnel's provincial mark must not replace the lower mark.
3. Kill two lower ministers before answering either review; both cases must be retained and shown sequentially. Repeat with two upper ministers and with one upper plus one lower death. A superior receives only one active review at a time.
4. Defer a review, save/reload and resume it. No timeout should count as approval. Repeat after replacing the Chancellor, after the emperor dies, and after the displayed successor dies or is manually replaced. Old event buttons must not install their old candidates.
5. Mark an unlanded eligible candidate, a person already selected automatically, then the installed successor. Verify explicit inclusion and deduplication. Imprison, disqualify or kill a marked person before review and check the unavailable explanation.
6. Compare a qualified relative/friend/faction ally with a weaker related candidate. Check basis colors, relevant Just/Honest/Vengeful previews and actual stress after success. Verify +10/-20 opinion direction/duration and no repeated bonuses from stale clicks.
7. Replace with another eligible lower minister or a territorial governor, then inspect native source-office handling, personal titles, realm membership and council seats. The Chancellor must not take an upper minister into a lower seat.
8. Open the law screen: Civil Recruitment Standards and its decision must be gone. A native-eligible senior provincial candidate must not be excluded just for lacking the retired degree requirement. Examination evidence/distinctions must still affect comparison; senior territorial confirmation authority must retain its existing setting.

Static checks cannot prove CK3 callback order, native council/title transactions, native source-office side effects, event layout, stress scaling or save migration.
