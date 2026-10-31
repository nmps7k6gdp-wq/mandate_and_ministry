# Examination honors and laureate careers

Build: **0.4.0-alpha.20-dev.41**. Implemented; source checks pass. In-game verification remains pending.

## Integration and the missing badges

[Exam First Rank by BigBen](https://steamcommunity.com/sharedfiles/filedetails/?id=3597419576) supplies the original three badge textures. Its downloaded descriptor targets CK3 1.18; this mod uses the installed 1.20.1.2 examination code. The standalone mod is not enabled in the inspected playset and is not required by this integration. Keep it disabled while testing MAM.

Before dev.40, MAM had distinction tracking and assessment points but no Workshop artwork. Dev.40 added an earned-only replacement for the shared palace icon. That UI gave no indication of honors when the displayed character had no recorded placement; source inspection cannot establish whether the character in the screenshot had earned one. The screenshot alone is insufficient evidence of a missing award.

Dev.41 adds a dedicated **Examination Honors** row to the native Merit tooltip. All three badges are visible: unearned badges are dimmed, earned badges receive the native green stamp. The row itself has no achievement visibility condition, so its presence can be tested independently of examination records. The Government Administration palace slot still displays the highest earned honor. Awarded characters also receive a permanent, visible fame trait.

Only local mod files are changed. Native game and Workshop files are read only. The three 120 by 120 DDS textures are byte-identical copies of BigBen's artwork under `gfx/interface/icons/mam_exam/`. Neither the old full activity overrides nor the original recurring Merit/Diplomacy package is copied.

## Honors and rewards

The user chose capped career Merit and vanilla examination eligibility. Dev.41 adds public recognition and political relationships; there is still no custom lowborn ban or recurring Merit income.

| Highest distinction | MAM assessment | Career Merit ceiling | Career Prestige ceiling | Recognition |
| --- | ---: | ---: | ---: | --- |
| Provincial first | +4 | 0 | 0 | Credentials record |
| Metropolitan first | +6 | 0 | 0 | Credentials record |
| Palace top three | +8 | 50 | 150 | Examination Laureate; book badge |
| Palace first | +12 | 100 | 300 | Palace Champion; jade seal badge; possible imperial audience |
| First at all three stages | +16 | 150 | 600 | Threefold Laureate; scrolls badge; possible imperial audience |

Assessment uses the highest honor, without summing lower grades. These are MAM assessment values, not a blanket addition to every native succession type.

Merit and Prestige have separate lifetime payment ledgers (`mam_exam_career_merit_paid`, `mam_exam_prestige_paid`). Native examination rewards remain separate. Upgrading from top three to champion pays only an additional 50 Merit and 150 Prestige; repeating that honor pays no further distinction currency. Recognition receives one permanent `mam_exam_laureate` fame trait with a dynamic name, description and icon for the highest grade. It grants **+5 opinion between fellow laureates**, across all three grades. It cannot be generated randomly or selected in the ruler designer.

Only real palace-completion callbacks can pay awards. Loading a save, restoring traits, viewing credentials or opening a badge does not pay currency or create an imperial audience. Existing MAM/legacy placement flags can restore the trait; a generic historical palace pass cannot establish past finishing position.

## Recognition and imperial sponsorship

A player who earns a fresh higher honor receives **A Name Distinguished**. The tooltip reports the actual additional Merit and Prestige already paid. AI laureates receive the same trait and rewards quietly.

A fresh champion or Threefold Laureate in the Chinese realm can be presented to the current Chinese emperor in **A Scholar Before the Throne**, with emperor and scholar portraits. The delayed dispatcher resolves the current holder of `h_china`; it does not retain a dead emperor as the authority. An emperor does not receive an audience with themselves.

| Imperial choice | Effects |
| --- | --- |
| Sponsor the scholar | Costs 75 Prestige; +15 assessment/native senior civilian appointment score in the sponsoring realm for five years; scholar gains +30 opinion of emperor for ten years; emperor gains +10 opinion of scholar for five years |
| Commend before the court | Scholar gains +20 opinion of emperor for five years; emperor gains +10 opinion of scholar for five years |
| Offer congratulations | Scholar gains +10 opinion of emperor for three years |

Sponsorship keeps normal eligibility and does not reserve an office. The +15 is included once in each independent scoring path: MAM public assessment, inherited by ministerial assessment, and the existing native senior civilian governor score helper. County/duchy and military native appointment scores are not changed. Leaving the sponsoring realm removes the scoring advantage while away.

AI emperors favor sponsorship more when Diligent, Just or Ambitious; Humble/Honest favor public commendation; Lazy/Arrogant favor formal congratulations. The paid option requires sufficient Prestige. Every consequential option rechecks the current emperor, living scholar, realm membership and unacknowledged honor. A stale audience has a harmless close option. A completed audience stamps the acknowledged grade, preventing repeated audiences at that grade; a later higher grade can receive another audience.

## Personnel and Chancellor gameplay

Existing Personnel service commendations, Royal Favor and standing marks can be used to advance a laureate. Honors appear beside highlighted candidate names in senior appointment and ministerial approval options. Candidate tooltips report the recorded distinction and any applicable imperial sponsorship.

Professional-minded approval authorities (Just, Honest, Diligent or Patient) add a modest **+2/+4/+6** respect term for laureate/champion/Threefold Laureate in central ministerial assessment. This directly affects the Chancellor's lower-ministry shortlist and the emperor's upper-ministry shortlist. The usual role skill and eligibility remain in force. The term is previewed only when it applies.

Passing over a laureate has a narrow political consequence. Before an appointment, MAM compares the selected person with the eligible professional benchmark. If the benchmark is a laureate, more than five assessment points stronger, and the selected person has a family, faction/client or paid-patronage connection to the chooser, the passed-over laureate receives **-10 opinion of that chooser for three years**. The modifier does not stack. Ordinary qualified alternatives and appointments without such connections cause no new penalty.

The benchmark's eligibility, source readiness for territorial appointments, living status and realm membership are checked. The comparison is captured before title transfers can change assessment. The opinion effect occurs only after the territorial title grant or both ministerial title/seat synchronization succeed. Conditional previews explain the actual laureate and opinion consequence. Existing Just/Honest/Vengeful stress rules remain separate; this patch adds no blanket new stress penalty.

## Recording and compatibility

- Provincial first: native finalized winner, after native rewards, with an ordinary provincial pass and cheating checks.
- Metropolitan first: the finalized palace-entrant subset is ranked before native phase cleanup; one activity stamp prevents repeated recording.
- Palace honors: native finalized first/second/third variables, after native rewards. Missing second/third positions are guarded; no re-sorting after rewards and no reliance on the transition's current-phase pointer.
- Actual palace participation and a recorded pass are required. Caught cheating is excluded; a native simulated AI palace pass cannot invent a finishing position.
- Legacy top-three/champion/triple-first flags remain recognized when backed by a palace pass.
- Trait restoration runs on startup and annually for living characters. It grants recognition only, without retrospective rewards or events. If a loaded save does not run the startup hook, the annual repair provides a fallback.
- Three native reward/cleanup effects have one MAM recorder call each. Both current-native GUI types are overridden in a local additive GUI file; the native Merit-tooltip body is preserved apart from one honor-row insertion. Mods replacing these types or effects can conflict. Future CK3 patches require a parity review.

## Source verification

- Balanced blocks and required UTF-8 BOM across **231 common/event scripts**, plus balanced GUI sources.
- Examination event/helper targets, seven read-only GUI queries, trait paths and English localization resolve.
- All three native examination bridges match the installed game bodies after removing the recorder calls.
- Current native Merit-tooltip body matches exactly after removing the honors-row insertion.
- The single permanent fame trait has grade-specific localization/icons, +5 shared opinion, zero random-generation weight, and no recurring Merit or Diplomacy.
- Restoration cannot call the paid recognition effect. Both award ledgers use positive differences and update after payment.
- A limited source evaluator passes 256 mixed MAM/legacy placement and pass-evidence combinations, plus upgrade/repeat/persisted-state payment checks. It does not emulate the CK3 engine.
- Four favoritism snapshot call sites supply the complete template. Application is inside existing successful transaction branches.
- All three texture files retain their previously checked dimensions and byte-identical Workshop assets.
- The engine-rejected six-decimal one-third AI factors found in the existing log were shortened to supported three-decimal values (`0.333`). Other pre-existing log issues are outside this patch.

No CK3 examination or final GUI layout has been executed for this patch. Source checks do not prove engine callback order, trait rendering, option evaluation or loaded-save behavior.

## Engine checklist

Use a separate save, restart CK3, and keep the standalone Exam First Rank mod disabled.

1. **UI presence, no honors required:** hover Merit. There must be an Examination Honors heading and three dim icons below the ordinary examinations. Hover each and check the unrecorded explanation. If the entire row is absent, collect the new log and active playset: this is a GUI registration/conflict issue rather than a missing placement.
2. **Fresh palace result:** note the native top three. First earns the champion trait/seal and lifetime ceilings 100 Merit/300 Prestige; second/third earn laureate/book and 50/150. Fourth receives no new distinction. Native reward amounts are separate.
3. **Three stages:** win provincial, metropolitan and palace. Expect the Threefold Laureate trait/scrolls, highest-only +16 assessment and ceilings 150 Merit/600 Prestige. Two stages must not suffice.
4. **Trait and social effect:** inspect two laureates of different grades. Each should recognize the other through the same +5 trait opinion, with the correct grade name and artwork.
5. **Audience choices:** earn a champion in the Chinese realm. As emperor, inspect both portraits and preview all options. Test all three in separate reloads. Below 75 Prestige, sponsorship is visible but unavailable. Verify actual cost, opinion directions/durations, five-year modifier and +15 score. No automatic office grant.
6. **Upgrade/repeat:** top-three then champion pays only the difference; repeating a grade or reopening the UI pays nothing. Acknowledged audience grades do not reappear. Reloading preserves paid/acknowledged ledgers.
7. **Appointment visibility:** compare a laureate against a non-laureate in Personnel and ministerial approval events. Check name labels, conditional honor/sponsorship/respect tooltips, native qualifications, and professional-Chancellor ranking.
8. **Favoritism:** appoint a connected candidate more than five points below an eligible laureate benchmark. Only after success should the benchmark gain -10 opinion of the chooser. Repeat with an equally strong relative, an unconnected alternative, a dead/ineligible benchmark, a blocked source transfer and a failed ministry synchronization: no new penalty. Existing stress previews should still match traits.
9. **Stale audience:** scholar dies, leaves the realm, or the imperial holder changes before resolution. No stale spending or opinion award. The delayed dispatcher should select the current emperor when possible.
10. **Exam edges:** fewer than three entrants, tied native scores, cheating, withdrawal, cancellation/host death, and AI simulated passes. No missing-scope errors, invented rank or cancellation award.
11. **Historical save:** only evidenced old honors gain the trait through restoration. No Prestige/Merit or imperial audience merely from loading or viewing. Characters with only a generic palace pass stay unranked. Check the annual repair if no startup restoration occurs.
12. **Eligibility and regression:** lowborn admission follows native rules. County/duchy/military appointments, Personnel tasks, suspended Censor-Justice runtime and the disabled register remain as before.

For a failed case, record the character, finishing position, current badges/trait, before/after resources, active mods and relevant log lines. Inspect `mam_exam`, `merit_hud_tooltip`, `widget_palace_exam_status`, `mam_exam_laureate` and GUI function/type errors in a fresh `error.log`.

Live-log follow-up: CK3 prefixes trait-icon filenames with `gfx/interface/icons/traits/`. The initial full-path trait entries produced an invalid doubled path during live reload; corrected to relative filenames with three exact local copies in that directory. The badge-row textures keep their full GUI paths. The same live-edit log contains missing dependency/localization/namespace messages from intermediate files (including the now-removed `is_valid` option field). A clean restart is required to distinguish resolved hot-reload messages from new runtime failures; the finished patch is not claimed engine-verified.
