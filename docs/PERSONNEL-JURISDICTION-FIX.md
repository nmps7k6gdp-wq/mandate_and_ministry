# Personnel jurisdiction and nested-kingdom maintenance

Build: **0.4.0-alpha.20-dev.44**. Updated: **2026-10-28**.

Personnel remains the completed revamp accepted at dev.41. This maintenance patch addresses reported inheritance defects and extends senior appointments to kingdom offices under territorial empire governors. Censor-Justice gameplay remains removed.

## Reported problems and source findings

1. Lower titles/vassals could remain with the emperor after a senior appointment. The old capture stored directly held county-and-higher titles and direct vassal primary titles, but omitted personal baronies and the fuller subordinate title tree. Restoration only moved qualifying living vassals; it could not grant a recorded vassal title back when that title had returned to the emperor. Capture also allowed a known vassal with mixed lower holdings, while restoration later rejected that vassal.
2. A kingdom beneath an empire governor bypassed Personnel because the incumbent filter explicitly required `liege = top_liege`. Commitment always placed appointees directly beneath the emperor and had no final de-jure empire-governor resolution.

These are source-level gaps. The native game transactions producing the reported map state have not been replayed in CK3 for this patch.

## Resulting rules

- Personnel handles clean, supported civilian kingdom/empire offices directly under the emperor, plus kingdom offices beneath a supported civilian territorial empire governor in the same realm.
- The throne remains temporary custodian. Default candidates, merit checks, marked candidates, candidate categories, appointment-authority laws and the queue remain in use.
- At commitment, a kingdom appointee becomes the vassal of the **current eligible holder of the kingdom's de-jure empire title**. The holder must be a living civilian territorial empire governor in the same realm, directly beneath its emperor. Central ministers, foreign rulers and military/non-governor holders are excluded.
- If that empire is unheld or temporarily held by the emperor, the kingdom serves the throne while waiting. A later empire appointment immediately wakes matching completed kingdom files; periodic story maintenance is a fallback. The holder is rechecked at handover, so a stale portrait/reference cannot select a deceased or replaced superior.
- Separately reassigned kingdom governors are not pulled away from another established liege by old appointment records.
- County/duchy vacancies retain native appointment handling. Restoring their existing territory/vassals as part of a senior jurisdiction creates no new lower-tier appointment events.

## Recorded jurisdiction handover

Before death/promotion custody, each file now records:

- The old office's own territorial titles, including directly held baronies, with estate/family, leased and head-of-faith exclusions.
- Original vassal characters throughout the supported subordinate hierarchy.
- Their primary titles and the actual lower title holdings belonging to that jurisdiction.
- The former superior's primary title, to identify legitimate temporary custodians during nested succession.

Custody uses this exact bundle. On completion, personal parts are granted with the senior office. Recovery then grants recorded lower titles/baronies still held by the throne or recorded former superior to the nearest suitable recorded lower-office holder, or to the incoming senior governor when no intermediate holder is available, and restores recorded vassals. A surviving duke keeps the mixed lower holdings that already belonged to that original vassal. A new heir carrying unrelated outside jurisdictions is protected from wholesale reassignment.

Vassals return through the recorded de-jure lower hierarchy where suitable holders exist: counties can remain under their dukes and barons under their counts. Parent holders already beneath, or queued to return beneath, the new governor are recognized. Missing intermediate holders fall back to the new senior governor.

This is not a sweep of all land geographically inside the kingdom. Unrelated imperial demesne, foreign ownership, family/estate titles, leased holdings and separately reassigned vassals are protected. A different live kingdom appointment keeps its own land reservation.

## Simultaneous offices and promotion sources

Root-title custody locks identify the exact pending file. Lower title claims prefer the more specific live office; an empire handover cannot absorb a separately pending kingdom and its counties. Completing the child kingdom protects its land while still allowing legitimate reattachment as a vassal when its parent empire is appointed.

Both normal vacancy capture and promotion-source capture use the same snapshot/custody helpers. Promoting a kingdom governor to its parent empire therefore leaves a separate kingdom appointment in the queue. An empire governor's own directly held de-jure secondary kingdom, by contrast, remains part of that single captured bundle.

A stale file cannot clear a newer file's title lock. Unresolved eligible title/vassal repairs and waiting parent attachments keep a maintenance flag; successful repairs clear it. The existing independent FIFO appointment entries remain intact.

## Existing saves

A one-time per-realm migration checks completed Personnel appointment records and attempts safe restoration using their recorded titles and vassals. It runs at startup, with a quarterly loaded-save fallback. It does not reconstruct missing history from geography or reverse unrelated assignments.

Old files do not contain the new full snapshot. Recorded county/duchy titles can be recovered, but an unrecorded historical barony or subordinate holding cannot safely be attributed after the fact. For complete verification, restart and use a save **before the governor dies or moves**, so the new snapshot is captured.

The one-time stamp prevents the legacy repair pass from repeatedly undoing later deliberate transfers. New files retain their own pending-repair behavior.

## UI and adjacent fixes

Appointment choice tooltips explain whether the office will answer to the emperor or the current de-jure empire governor. Authority is rechecked when the transaction occurs. Existing labels/portraits, merit and opinion/stress rules remain in place.

The current log also showed unset candidate scopes in conditional option names. Those name conditions now guard the scope switch itself, because CK3 can evaluate names for hidden options. This does not add or change shortlist categories.

## Verification

Source checks and the focused harness pass. Run:

```powershell
& 'C:/Users/atngu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/verify_senior_jurisdiction.py
```

The harness evaluates the actual snapshot, claim, parent and restoration helper bodies against small title/character graphs. Its **20 scenarios** cover:

- Direct and nested kingdoms, personal county/duchy/barony grants, protected imperial holdings and family estates.
- A subordinate governor dying during custody; a county vacancy under a surviving kingdom during empire custody; original mixed holdings and protected outside-jurisdiction heirs.
- All capture/completion order combinations for simultaneous empire/kingdom vacancies.
- A later empire vacancy after a completed kingdom appointment.
- Barons/counts retaining their internal hierarchy while ancestors are queued for reattachment.
- Changed, foreign and central-ministry parent holders.
- One-time legacy repair and protection against replay after later transfers.
- Promotion of a kingdom holder into the parent empire; an empire holder's own secondary kingdom bundle.
- Superseded custody locks.

The harness models native destination-transaction postconditions and custody lifting; it does **not** emulate CK3's appointment eligibility, native succession callbacks or transaction engine. Its results are source/graph verification, not in-game confirmation.

Final source checks passed across **132 common/event scripts**, covering block structure, encoding, helper/event/localization references, parameter completeness and both capture paths. SHA-256 comparison confirmed **154 unrelated existing files unchanged**, including AI/task/honors sources and the removed Censor-Justice baseline. Native/Workshop files were read only.

## In-game regression checklist

1. Fully restart CK3 and load a save before a supported kingdom governor's death. Note personally held duchies/counties/baronies, vassals and their lieges. Appoint an unlanded candidate. The complete recorded jurisdiction should leave custody and go with the office; unrelated imperial holdings remain with the throne.
2. Repeat while a duke/count beneath that office dies during custody. Recorded lower holdings inherited by a custodian should be restored. Check ownership of the county capital barony as well as the county title.
3. Kill a kingdom governor who is a vassal of a territorial empire governor. Personnel should receive the appointment. The successor should be beneath the live de-jure empire governor, with their own dukes/counts retaining the proper lower hierarchy.
4. Kill the empire governor and subordinate kingdom governor together. Resolve kingdom then empire, then reload and reverse the order. Each vacancy gets its own appointment; the empire choice must not consume the pending kingdom or its land. Final kingdom liege should be the new empire governor.
5. Promote a kingdom governor into that empire vacancy. Confirm the source kingdom gets a separate Personnel appointment and its successor becomes the promoted governor's vassal.
6. Test an empire holder also personally holding a de-jure kingdom. Both titles and associated holdings should move as one clean bundle; independent kingdom vassals retain their own offices.
7. Change or kill the parent empire governor before the kingdom choice commits. The appointment must use the current eligible holder. An unheld/custodied parent leaves the kingdom beneath the emperor until the empire is filled; foreign/ministry holders never receive the vassal.
8. Try legacy-record repair on a separate existing save. Check only recorded holdings are recovered, and compare with the documented historical-data limit.
9. Recheck simultaneous unrelated vacancies, source lateral transfer, marked candidates, imperial confirmation, task availability and honors. County/duchy appointments and Censor-Justice removal should be unaffected.

Collect the new `error.log` and any `MAM_PERSONNEL_JURISDICTION` / `MAM_PERSONNEL_PARENT` messages for failures. Native callback order and actual title/vassal transaction behavior remain to be confirmed in CK3.

## Empire appointment option and capital-barony corrections - dev.44

The 2026-10-28 log at 00:16:09 identifies an unset `mam_senior_lateral` while building an appointment option's tooltip. Its `show_as_unavailable` rule checked for a default candidate instead of a lateral candidate, so an empty transfer slot could be rendered. Basis, consequences and scheduling code then attempted to evaluate the missing character, producing the skill, merit, relationship, certification and native-validity errors in the same trace.

The unavailable rule now requires the actual lateral candidate. Optional eligibility switches, basis/consequence/sponsorship previews and nomination scheduling guard candidate existence before switching context. Weak-record comparisons guard the professional benchmark. Scheduling also rechecks current eligibility/source readiness and resets the selected-person binding only after validation. Valid shortlist categories and appointment policy are unchanged.

The 00:16:20 log also exposes a native restriction missing from the previous graph model: a county capital barony cannot be transferred independently. The county transaction carries it. Custody and commitment now share `mam_senior_queue_personal_parts_effect`; its guard excludes capital baronies from direct transactions. The same guard applies to recovered components. Capital records can remain in the snapshot, while separately held noncapital baronies retain their explicit transfer path. The county grant preserves its ordinary capital ownership without enabling a blanket take-all-baronies operation.

The verifier now models capital provinces, rejects independent capital-barony transactions, and applies automatic capital ownership with county grants. It runs the shared personal-part queue source for both custody and destination transfer. All **28 scenarios** pass: the original 20 jurisdiction scenarios, six missing-candidate preview/scheduling cases, the empty-lateral visibility case, and the capital/noncapital restriction case. These are source/graph tests, not a completed CK3 replay.

After a full restart, retry the empire appointment from a save before the vacancy or source promotion. When no same-tier transfer candidate exists, that option should be absent. Hover the remaining choices and complete a promotion that vacates a kingdom source. A fresh log should contain neither the `mam_senior_lateral` tooltip cascade nor capital-barony transfer errors. Inspect the county and its capital holder together.
