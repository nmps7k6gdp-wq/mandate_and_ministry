# Censor revamp: independent inspection and impeachment

Design for discussion, revised 2026-10-30 against dev.61 after user feedback that the prior draft was too passive. **Direction approved for implementation on 2026-10-30.** The subsequent dynamic-story request is implemented in dev.62 source; use [CENSOR-IMPLEMENTATION.md](CENSOR-IMPLEMENTATION.md) for exact behavior, limits and verification. This historical proposal does not imply that every suggested power is implemented. Read [historical context and ministry relationships](CENSOR-HISTORICAL-DESIGN.md) and [the native gameplay audit](CENSOR-VANILLA-AUDIT.md). The removed dev.42 case/trial/register stays removed; accepted Personnel and Revenue runtime stay unchanged.

## Identity and power

Personnel determines who enters office. Revenue administers shared resources. The proposed Censor can compel scrutiny of how officials exercise authority and place their continued tenure before the emperor.

Its core powers should be independent initiative, official inspections, demands for records/answers, pursuit of connected misconduct, formal censure, impeachment and remonstrance. It does not need another minister to hand it a proven crime before it can act.

This replaces the passive receipt-review design. Independence is from investigated administrators, not unlimited authority over every imperial decision. Native Secretariat law and the emperor's ultimate political authority remain relevant.

## Core loop

**Choose an administration to inspect -> demand records and explanations -> follow supported connections -> close, order a defined correction, censure or impeach -> correction or imperial political confrontation.**

A separate remonstrance option challenges a policy/appointment on its merits. It must not claim that every criticized lawful choice is corruption. Routine inspection can finish cleanly; the system never invents wrongdoing to satisfy a quota.

## 1. Begin an inspection

Censor can target a serving public official, central ministry or supported provincial administration. No prior known crime or Chancellor/Revenue permission is required for an ordinary lawful inspection. Imperial request, petition, native discovery and a supported official record can provide leads, not automatic guilty verdicts.

New targets are county through territorial empire public officials and central ministers. Automatic attention focuses on senior offices; lower-tier attention is targeted. Unlanded people may be witnesses or recorded participants but do not generate standalone official cases.

Choose a concrete subject: appointment conduct, a specified public expenditure/project, alleged official abuse or, when future producers exist, a military return or legal decision. This is a review of public acts, not another search for adultery secrets. Vanilla tasks and ministerial Find Secrets remain available under their own rules.

## 2. Make officials answer

A valid demand names the records/conduct, current responsible office and reasonable response period. The official can cooperate, show authority, explain genuine impossibility, admit fault, contest scope or deliberately obstruct. New concealment/false reporting must be an actual recorded choice, never inferred from a missing script scope.

Demand compliance is a real obligation. Unjustified obstruction can independently support censure/escalation, while never proving the original allegation. War, death, office change or absent records need deliberate pause/reroute handling rather than guilt.

Censor can pursue a supported link to a sponsor, recipient or collaborating official within the same inspection. Friendship or faction membership alone is not proof of a conspiracy. One major inspection can concern several connected officials; it need not spawn a popup for every county.

## 3. Exercise authority

| Censor action | Proposed consequence | Limit |
|---|---|---|
| Clear and close | State what was examined and why no supported charge remains | No accusation-volume rewards or new perpetual immunity |
| Direct correction | Require a concrete lawful administrative remedy within delegated authority | Responsible module executes it; no unilateral transfer, title change or rewritten score |
| Formal censure | Supported lesser misconduct brings a bounded, visible reputational/Influence consequence and official response | Allegation alone has no penalty; contextual counter-appeal; once per act |
| Impeach | Seek dismissal, specified restraint or criminal referral directly before emperor | Censor cannot choose replacement, manufacture legal grounds or execute punishment |
| Withhold a supported custom finding | Protect ally, bargain or avoid danger, leaving a passive decision record | Cannot erase native secrets already revealed or delete institutional receipts |
| Remonstrate | Publicly oppose a specific government policy or appointment without calling it criminal | No automatic veto over Personnel, Revenue or imperial edicts |

An ordinary correction cannot imply powers not yet granted by design. For example, repayment requires separate lawful Treasury execution; stopping an appointment or grant requires a separately approved, tested adapter. The first release should not claim a universal freeze or veto.

## 4. Impeachment has a political endpoint

For a material supported memorial, emperor chooses to uphold the recommendation, demand a specified missing fact, reject the allegation, or deliberately protect the official. Dismissal must eventually use a tested proper native handoff, not death or arbitrary title grants. Personnel still fills supported vacancies; Censor does not appoint a client into the empty seat.

A serious rejected memorial may be pressed once. Censor can accept the decision, remonstrate openly or offer resignation. The emperor then faces a meaningful political choice over an official, the administration and the Censor. Consequences depend on findings, candor, relationships and support, not an unconditional realm-wide penalty whenever emperor disagrees.

A vindictive Censor can abuse scrutiny or push a weak allegation, risking exposure, loss of credibility, imperial dismissal or a supported counter-accusation. Honest inability to prove a concern is not the same as knowingly fabricating one. Player trait stress and AI personality apply to actual choices.

## Relationship with government

| Participant | Part in the proposed loop |
|---|---|
| Personnel | Supplies supported appointment/patronage acts; keeps all accepted appointments, tasks, scoring, marks and honors |
| Revenue | Supplies actual public-account records and funds lawful operating needs; retains custody/execution under fiscal law |
| Chancellor | Directs administration, supports correction and defends policies/officials; may challenge abusive inspection to emperor but cannot suppress all scrutiny |
| Emperor | Hears direct impeachment/remonstrance, supports or restricts exceptional measures and decides contested political tenure |
| Justice now | Keeps native imprisonment/pardon/criminal scheme; no new unfinished custom trial |
| Justice future | Reviews criminal sufficiency/procedure and lawful remedies; can return specific factual gaps without owning Censor's factual findings or vetoing every imperial memorial |
| Other departments | Own their operational gameplay and publish narrow supported conduct records as future modules are added |

Censor must be able to investigate Chancellor and Justice. Neither can decide their own accusation; conflicts route to emperor/an explicitly authorized independent reviewer. Censor's own misconduct likewise requires external review. Native Director law is respected rather than assuming Chancellor always outranks Censor.

Emperor can request scrutiny but a requested subject is not an ordered guilty result. The proposed direct imperial route is not a second fiscal approval queue: inspection/censure authority and Treasury spending authority are distinct.

Every matter must be completable before a new Justice module exists: close, correction, supported censure or imperial administrative decision. Criminal referrals are not left waiting indefinitely for future code.

## Native and accepted boundaries

- Preserve native tasks, ministerial political scheme, agents, secret disclosure, hooks, rewards/catalysts, Justice branches and shared career privileges.
- Native-scheme integration is a prototype question, not a verified API. Official inspection must not create free parallel secret discovery or duplicate native completion rewards.
- Source records must identify real acts, actors, office/time and relevant authority. Paid appointment obligations and lawful discretion must remain distinct. Ordinary Revenue receipts do not prove missing approval or theft.
- No automatic Personnel score penalty, appointment veto or censure of qualified relatives. New cross-module consequences require explicit design approval.
- Preserve protected payroll, existing paid commitments and campaign funding. Inspection cannot silently seize or freeze the common fund.
- Future Works/War/Rites/Justice misconduct needs real producer records; do not pretend all native expenditure or hidden history is already captured.

## Simplicity and implementation boundary

One major inspection with a bounded connected scope, one demand/reply stage and one findings/disposition stage. Only material contests create an extra decision. Hidden workers handle routine progress; correspondence uses [EVENT-DESIGN.md](EVENT-DESIGN.md). No register or evidence-point currency.

Institutional records belong to realm/Censorate and keep admitted facts despite source expiry. Stable act/inspection/disposition identity prevents repeated punishment or rewards. Current holder, law, jurisdiction and authority are rechecked; successors inherit work, never personal guilt.

Before coding: agree exact direct powers and exceptional restraint, inventory evidence producers, prototype native integration, design safe removal/censure handoffs and verify current Personnel/Revenue contracts. Then source-check and engine-test AI, financing, stale events, deaths, save/load, genuine lawful defenses and political confrontations. See [historical design checklist](CENSOR-HISTORICAL-DESIGN.md#scope-and-feasibility-checklist).
