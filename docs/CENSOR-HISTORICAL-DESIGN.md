# Censor: historical basis and government relationships

Research/design note, 2026-10-30, MAM dev.61. User rejected the passive reporting proposal and requested strong investigative power integrated with existing and future ministries. **No gameplay implementation.** Read with [the native audit](CENSOR-VANILLA-AUDIT.md) and [revised gameplay proposal](CENSOR-REVAMP-DRAFT.md).

## Historical findings

### Tang: broad inspection, investigation and impeachment

The primary institutional text, [Tang liudian, volume 13](https://zh.wikisource.org/wiki/???/?13), assigns censors scrutiny of officials and provincial administration, judicial matters, central departments, accounts and military merit claims. It distinguishes investigative work from ordinary sentencing at the Court of Judicial Review and describes special imperial commissions. This supports an office with its own investigative jurisdiction, rather than a clerk waiting for another ministry to supply a completed case. The text is an institutional prescription with historical commentary, not proof of uniform practice throughout the dynasty.

### Song: political exposure could threaten a chief minister

[The Cambridge History of China, Sung government and politics](https://www.cambridge.org/core/books/cambridge-history-of-china/sung-government-and-politics/B360D3EB6D72ADEE74E46FD8570548EC) describes censors/remonstrants channeling official opinion and pressing chief ministers to leave office. It also distinguishes the document-review powers of other offices. This supports impeachment that creates a political confrontation; it does not justify assigning every edict-return power to Censor or guaranteeing resignation after one accusation.

### Independence was real but conditional

[Historian Yu Yunguo's interview, hosted by Shanghai Normal University](https://renwen.shnu.edu.cn/_t92/ee/50/c2900a126544/page.htm) emphasizes relative independence from chief ministers and sovereign pressure, remonstrance/resignation, supervision of the supervisors and ultimate monarchical predominance. It treats Censorate and remonstrance offices as distinct parts of a wider system. The mod's one Censor role is an abstraction, not a claim that Tang and Song had identical institutions or modern independent branches of government.

## Gameplay conclusions: proposals, not historical facts

1. Censor chooses what official conduct to inspect without first obtaining Personnel, Revenue or Chancellor consent. A known crime is not required to open a routine lawful inspection.
2. The office can require supported records and an official answer. Cooperation, lawful inability, obstruction and destruction/false reporting must be distinguishable acts. No manufactured guilt because a receipt or engine scope is absent.
3. Investigation can follow a supported connection beyond its first official. A ministry, governor and sponsor can become one connected matter instead of isolated modifier events.
4. Formal censure has bounded direct reputational consequences after a supported finding. Impeachment seeks removal or stronger restraint through an imperial decision; Censor cannot choose the successor.
5. Remonstrance challenges a policy or appointment's wisdom separately from alleging a crime. A lawful decision can be criticized without retroactively becoming illegal.
6. Censor can press a serious rejected memorial once and offer resignation, creating a political choice between the government's programme, protected official and censorial independence. No automatic universal faction or legitimacy penalty follows every refusal.
7. An emperor can support inspections, request an area of scrutiny, protect a target or replace a hostile Censor. Requesting scrutiny is different from commanding a fabricated guilty result.
8. Powers to detain, suspend a specific act or remove an official need separate authorization and tested execution. History does not prove CK3 can intercept arbitrary native transactions.

## Responsibilities across the mod

| Office | Its own authority remains | What Censor may inspect/challenge | What Censor must not take over |
|---|---|---|---|
| Personnel | Appointments, lawful favoritism, tasks, scores, marks, honors | Paid obligations tied to official acts, concealed conflicts, falsified explanations; political objections to a particular nomination | Routine talent reviews, replacement selection, succession queue ownership or universal appointment veto |
| Revenue | Common custody, lawful approval/payment, provisions and project grants | Real disbursement/authority records, explicit supported misuse, obstruction; policy criticism of distribution | Cash custody, invoice executor, new parallel audit score, automatic seizure or payroll blockade |
| Works | Project proposal, execution and contributions | Supported misuse, false progress claims or misconduct if future producers exist | Project planning, funding authorization or treating delay as theft |
| War / Grand Marshal | Military administration and campaign command | Supported misconduct, dishonest returns or false merit claims if produced; scrutiny of a campaign's administration | Battle command, launch finance or treating defeat as proof of corruption |
| Rites | Ritual, cultural/religious duties and native eligibility | Specific supported breaches of duty or manipulation, when those features exist | Redoing examination awards or assuming Rites pays every examination cost |
| Justice, now | Native criminal scheme, imprisonment/pardon and legal checks | Supported abuse or obstruction; referrals only through existing valid criminal routes | A new unimplemented trial, invented legal grounds or duplicate punishments |
| Justice, future proposal | Review criminal liability/procedure and advise lawful remedies | Receive Censor's factual referral; request specified further facts; provide reasoned legal review | Becoming a compulsory veto over Censor's direct imperial impeachment, especially when Justice is implicated |
| Chancellor | Coordinate government, programme, six lower ministry succession and lawful fiscal review | Be investigated; defend policy/officials; support correction or petition emperor against abusive scrutiny | Permission gate for every inquiry, erasing records or deciding their own accusation |
| Emperor | Final sovereign political decisions, upper ministry succession and reserved fiscal/campaign authority | Hear direct impeachment/remonstrance, support scrutiny, protect/dismiss officials or Censor | A forced guilty verdict or automatic hidden criminal penalty for disagreement |

Subjects remain titled public officials from county to territorial empire, plus central ministers. Unlanded witnesses/recorded participants are allowed; no standalone new unlanded target queue. Lower-tier inspection is targeted; automatic focus is senior offices.

## Cooperation and conflict

- Chancellor can request a theme such as provincial abuses and provide an administrative answer. Censor controls factual findings and direct imperial escalation. Current native Secretariat Director law remains relevant; do not hard-code Chancellor superiority.
- Emperor can authorize exceptional compulsory measures for a specified subject/duration. An imperial protection order does not delete evidence; Censor can remonstrate or resign. No new authority law is assumed yet, and the fiscal law continues to govern money rather than immunity from scrutiny.
- Justice can disagree on criminal sufficiency while the emperor considers fitness for office. An official may be legally unconvicted yet politically dismissed. A policy dispute is not a criminal charge.
- Future Justice cannot silently kill a referral involving itself. Route conflicts to emperor/another specifically authorized reviewer. Censor's own supported abuses likewise need external review, never self-acquittal.
- Before custom Justice exists, every Censor matter can end in closure, correction, censure or imperial administrative disposition. No waiting-for-unbuilt-Justice state.

## Modular contracts to design before coding

These are required information categories, not existing API names:

- Producers own official actions, actual payment/appointment identity, actor/office/time and authority snapshots. Censor consumes supported facts rather than rewriting Personnel/Revenue internals.
- Censor owns inspection, admitted evidence, demands/replies, connections, findings and memorial. Source expiry must not erase admitted evidence; opening an inspection reveals no omniscient ledger automatically.
- Justice, if later built, owns legal assessment and execution through valid native legal mechanisms. It cannot rewrite facts or pay the same sanction twice.
- The lawful superior owns a disposition. Any removal must use a deliberately designed native/title handoff preserving jurisdictions, vassals, seats and accepted succession. No generic `kill`/title grant shortcut.
- Treasury remedies remain separate Revenue transactions with actual debit/credit. No fake Gold compensation, arbitrary common-fund freeze or new transfer executor.
- Each act/referral/disposition needs stable identity and one-time execution. A new minister inherits institutional work, not personal guilt or an opportunity to repeat rewards.

## Scope and feasibility checklist

- [ ] Agree direct inspection/demand/censure/impeachment/remonstrance powers and who authorizes exceptional restraint.
- [ ] Inventory available Personnel/Revenue records and show lawful, unsupported and abusive counterexamples.
- [ ] Preserve native spying, agents, disclosure, hooks, rewards/catalysts and Justice branches; any native-scheme extension needs a prototype.
- [ ] Determine whether summons/record demands can use native interactions and correspondence without arbitrary imprisonment.
- [ ] Treat universal transaction/appointment veto as out of scope. Any specific restraint needs an explicit subsystem adapter and separate approval.
- [ ] Verify imperial removal/censure execution and accepted title/council handoffs before offering it as functional gameplay.
- [ ] Model one major inspection with a bounded set of connected officials; hidden routine work, material decisions only, no repeated accusation rewards.
- [ ] Balance AI initiative, trait/relationship priorities, real costs, lawful refusals and imperial protection without a scandal quota.
- [ ] Engine-test office changes, death, save/load, current laws, conflicting reviewers and nonstacking consequences after implementation.

Only documentation was changed. No technical or engine feasibility of these new powers is claimed as tested.
