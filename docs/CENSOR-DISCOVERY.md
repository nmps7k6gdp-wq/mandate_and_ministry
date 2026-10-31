# Censorate discovery bridge: dev.64

Dev.65 adds the separately documented [senior public-accusation adapter](CENSOR-PUBLIC-ACCUSATIONS.md). Its allegation/grounds fields remain separate from this adapter's confidential discovery facts. An inspection can now retain one public matter alongside its one confidential discovery; original dev.64 behavior below is otherwise preserved.

Implemented at the user's request on 2026-10-31. Source verification is separate from CK3 acceptance. This extends the authorized Censorate inspection chain; it does not restore the removed Censor-Justice trial/register.

## Player loop

The native Find Secrets task/scheme still does the discovering. Within a weekly intake, relevant secrets actually known to the current Censor can become a confidential report. The official can be questioned through the existing inspection chain, or the Censor can take the discovery directly to the emperor in a memorial. The Censor may defer or bury their report. This leaves native knowledge, exposure, criminal reasons, hooks and rewards intact.

Supported secret types are public-treasury siphoning, embezzlement, examination cheating, soliciting an incursion, coup plotting, murder and attempted murder. Ordinary sexual/religious secrets are not automatically official misconduct. Inspection subjects remain titled public officials, including county/duchy governors; an unlanded witness is not a new independent investigation target. The emperor is outside this ordinary subject filter.

Discovered murder, abduction and imperial-treasury siphoning plots in the imperial court generate an **unidentified plot warning**. Discovery is not proof of the owner's identity. The Censor can trace the real, still-live plot once, taking seven days, or give its living intended victim six months of closer protection. Protection adds five days to hostile scheme phases against that character; it neither cancels schemes nor guarantees safety. A treasury-target plot has no invented personal victim.

Tracing uses actual Censor Intrigue and Learning against the actual author's Intrigue and Diplomacy, with Diligent/Patient/Deceitful effects, bounded to 10-90%. A roll identifies only the saved real author. Failure, an ended scheme or a changed investigator names nobody. The hidden author is never used in portraits, names or accusation choices before successful tracing. The chance preview is refreshed when tracing resolves; it is not a promise that the live plot will survive seven days.

Once identified, a plot can enter the same official questioning, ministerial defense, Justice advice, censure, impeachment and imperial confrontation as other supported discoveries. A supported administrative finding is not an automatic criminal verdict. Serious discoveries cannot be resolved by the minor administrative-correction option; a Censor can still decline a sanction, and the emperor can protect the official.

## Discretion and safeguards

- Just/Diligent/Honest Censors favor an inquiry; Ambitious/Vengeful Censors favor direct memorials, especially against an actual rival. Arbitrary/Deceitful Censors are more inclined to bury a friend or house ally's report; Ambitious Censors may favor a faction ally. Craven/Lazy/Fickle behavior can delay action. Known supported acts can be left without sanction, at contextual Just/Diligent stress cost. An unidentified dead-end warning does not apply that stress.
- The emperor's independently known secret against the current Censor routes to the emperor. The Censor cannot adjudicate or bury that referral. This has a separate one-time source marker from ordinary Censor intake.
- Unknown-owner plot callbacks deliberately exclude the current Censor's own plot: this adapter does not pretend the Censor investigates their own secret order. An emperor who independently learns a supported native secret can still act against them. Wider counterintelligence against an unknown/foreign/unlanded author remains native gameplay.
- Only plots discovered against the emperor, a public official hosted at the imperial court, or `h_china` itself are routed. Provincial/private court plots are not magically broadcast to the capital. No all-world spying scan is added.

## Institutional state and bounded presentation

`mam_censor_intelligence_service_story` is a single sovereign-owned weekly worker, indexed by `h_china.mam_cen_intel_service`. Startup, title succession and the documented quarterly sovereign callback adopt old saves. It scans at most one new relevant Censor-known secret and one independently known imperial allegation against Censor per poll. It does not invoke a new discovery scheme or fabricate secrets.

`mam_censor_intelligence_lead_story` snapshots the actual actor, discovery kind, discoverer, date, optional victim, pending state and review sequence. `h_china.mam_cen_intel_queue` holds at most eight live referrals. A real Secret receives only this module's intake marker. A real Scheme receives only this module's source identity pointing to its lead. No transient Scheme or Secret pointer is retained in the lead. Tracing re-finds the live scheme among the saved author's schemes by that source identity and checks exposure again.

Only one intelligence brief or one inspection may be presented automatically at a time. A matching identified lead can join an existing inspection before imperial presentation. It invalidates the old findings/reply token and returns to a hearing of the new allegation. It never overwrites another official's file or silently adds new allegations after the emperor has already heard the memorial. Additional leads wait behind the active inspection. Each inspection accepts one discovery snapshot; other discoveries remain separate referrals.

Deferred referrals sleep 30 days. Pending referrals expire after two years without sanctions. Completed source snapshots remain ten years. A new discovery can bypass the ordinary random-inspection rest/cooldown because it is a distinct identified event, but each source is imported once. Eight full queue slots postpone secret intake until capacity returns; a plot callback arriving while full is not imported. All native discovery still runs.

Every brief choice rechecks pending identity, sequence, reviewer, current office, subject, absence of another active inspection and tracing state. Changing the reviewer invalidates old buttons. Manual inspection start defers an already open intelligence brief and invalidates its token. Succession transfers the institutional stories; personal responsibility is not inherited. The role-owned Review Confidential Discoveries decision recalls only a current brief actually addressed to that player; it is hidden when none exists.

Secret intake markers point to their immutable lead snapshots. The lead records the inspection that consumed it. Independently learning that same native secret does not create another referral while the first is pending or its inspection is active/already sanctioned or followed by a verified retirement. An independently informed emperor can reopen a Censor's buried, unsanctioned report once; their distinct knowledge marker prevents repetition. This is separate from genuinely different discoveries concerning the same official.

## Compatibility and source

Additive `on_scheme_discovered` routing preserves the native callback's existing effects. Known-secret polling avoids overriding any secret type or its `on_discover`/`on_expose`. This means a secret exposed/deleted before the next intake may not be imported; there is no claim of a universal instantaneous callback. Native scheme/Justice agents, rewards, criminal options and exposure remain unchanged.

Sources: `tools/templates/censor/intelligence.txt`, `tools/build_censor_intelligence.py`, and the existing Censor templates/generator. Run the full staged common-fund build. The 11-file runtime footprint is retained. New event 101 is independent of the existing stage event IDs; none are renumbered. Own state uses `mam_cen_*`; Personnel and Revenue implementations are untouched.

Use [CENSOR-TESTING.md](CENSOR-TESTING.md) for engine checks and [CRASH-2026-10-31.md](CRASH-2026-10-31.md) for the separate unresolved native crash audit.

Final source verification passed through the full staged dev.64 build: nine check suites, 159 protected files, 15 pinned native definitions, five lifecycle-contract examples and five actual-source skill tests. All engine acceptance boxes remain pending; this is not a confirmed native crash fix.
