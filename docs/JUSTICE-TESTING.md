# Justice dev.66: engine acceptance checklist

Status: authored/source checks are separate from these tests. **None of the following are marked engine-passed.** Use a backed-up save and restart CK3 to load the new classes. Keep developer hot reload enabled as preferred; restarting this test session does not require disabling it. Save before/after an important failure and supply `error.log`, `game.log` and the save name. For a crash preserve the crash bundle before attributing a cause.

Source verification completed 2026-10-31: all ten staged suites passed, including 23 Justice contracts, 13 Censor tests, exact native cost/acceptance comparisons, 14 Justice native pins and 159 unchanged protected files. [Generated report](JUSTICE-VERIFICATION.json). The engine boxes below intentionally remain unchecked.

## First player run

- [ ] As Emperor, find **Judicial Authority** with levels numbered 1 and 2, complete descriptions and native-style icons. Change law only at peace, for 150 Prestige, with a five-year cooldown.
- [ ] As Justice, right-click an eligible senior official under **Ministry → Justice: Refer a Judicial Matter**. Read portraits, linked highlighted names, hearing options and relevant tooltips. County/duchy routine subjects should not gain this interaction.
- [ ] Let the accused answer/contest/plead. A connected minister can intervene. The current reviewer alone should have **Justice: Resume My Pending Business**; no register appears.
- [ ] Compare a capable, compassionate/just minister with a greedy/arbitrary/vengeful one. Check real skill/relationship effects and stress only for traits that the actor has. Mitigation must not erase a real criminal right or manufacture proof.
- [ ] Under delegation, ordinary existing-ground arrest can proceed if the actual native performer is eligible and auto-accepted or has genuine surrender. Central ministers/protected imperial family require Emperor participation. Under reservation, the proposal reaches the Emperor first.
- [ ] Refuse reserved approval: no resource charge, arrest, release, pardon or punishment occurs. Approve: native costs charge once to the actual performer. Test Justice Treasury shortage with a well-funded common fund, then with Revenue refusing the operating request. Pending finance should retry quietly, not repeatedly open modal invoices.

## Mercy, custody and native rights

- [ ] A native pardon names whose four categories of rights it clears; it must not promise a single-charge pardon. Test a nested governor with immediate-liege grounds, and one with imperial grounds only. Test another authority retaining separate rights. No empty-bundle pardon rewards.
- [ ] Add a new category of grounds/change the right-holder while a reserved pardon is awaiting approval: renewed review is required. Same-category individual offense identity is an engine limitation described in the implementation document.
- [ ] Pardon a prisoner: pardon alone must not release them. Arrange release separately with the actual custodian's consent. Refusal leaves custody unchanged and is not a new crime.
- [ ] Execution/banishment require native grounds plus current imperial approval. Banishment additionally needs prisoner acceptance. Change custodian after approval/consent: old consent must not apply. No torture/mutilation/vow/puppet terms are silently selected.
- [ ] As a player prisoner facing an AI executioner, receive the original native execution notice. Justice must wait for its actual final execution, not charge/replay it or announce an early death. Verify the final receipt names the actual executioner; a different intervening death is not falsely reported as that execution.
- [ ] Try native Justice interactions and Find Criminal while the law reserves senior measures: matching gates should direct reserved business to Ministry. Lower native business/other actors' powers should retain original behavior. A completed native action must close the obsolete custom proposal without double charging/rewarding.

## Censor and personal misconduct

- [ ] Refer an actual Censor inspection to Justice; the Censor can independently finish administrative work. Justice may request at most one independent inquiry, waiting no more than 60 days.
- [ ] An allegation or lawful procedural objection alone must not offer an imperial corruption warrant. Test a real dated, corroborated post-adoption paid appointment/false certification/judicial demand; Emperor must explicitly approve the warrant.
- [ ] Warrant grants an imprisonment reason only. It must not grant execution/banishment/revocation. Withdraw only that warrant and confirm unrelated native rights remain. Arrest/pardon/new reign cannot reissue the same consumed source.
- [ ] Offer a private bargain as a corrupt player Justice. Decline/report as the recipient: no money/hook transfers. Accept and complete the promised act: exactly 100 personal Gold or one agreed hook, never public Treasury. Check native Loyalty Hook does not cause a second hook. Replace Justice before settlement: successor cannot collect it.
- [ ] Report actual solicitation/execute a noncapital bypass. Censor should eventually receive a real lead when free, while retaining discretion. The actual author may be rebuked/restrained; successor must not be sanctioned for inherited work. Honest/Just AI must not solicit or bypass.
- [ ] Leave a private demand unreported: the Emperor and unrelated advocates must not see private facts or an omniscient rebuke option. Corroboration privately held by Censor is not yet an imperial memorial; reporting/formal disclosure changes that.
- [ ] If more than one source accompanies an inspection, a warrant proposal and its seal must name the same qualifying source identity. An unproved secondary record cannot consume the warranted source; changed evidence requires a new proposal/review.

## Interruptions and observation

- [ ] Two officials acquire grounds simultaneously: two case identities, one actionable modal at a time, both eventually processed. Unchanged native grounds should not create an endless stream of new proceedings.
- [ ] Death, retirement, office succession, sovereign succession, imprisonment of reviewer and realm exit while a window is open: stale buttons cannot commit. Current judge inherits work, not old private obligations. Native execution should not trigger reentrant payment/duplicate case execution through succession callbacks.
- [ ] Petition once after a completed disposition: coordination/imperial review can criticize handling, but cannot replay/undo a pardon, punishment or consumed right. A new active case must not be overwritten by an old petition.
- [ ] As the accused, including while imprisoned, use the owned **Justice: Petition for Review of My Treatment** decision. It and the Ministry interaction share the same one-petition limit; a full queue must not block a petition on an already-active case.
- [ ] Keep existing custody after a hearing: at most one automatic review after 180 days. Defer/leave a window open: no timeout conviction and no project-style modal retry spam.
- [ ] Observe 3–5 years from a saved starting point, save the end state separately, then review logs and both saves for case throughput, actual balances, unsupported warrants, repeated executions/fees, endless retained cases and AI personality differences. Counts alone do not prove fair AI balance.
- [ ] Regression: simultaneous Personnel vacancies/jurisdictions/marks, accepted senior appointments, common-fund payroll and native project/campaign payments still behave as before. No Justice custom title handoff bypasses Personnel.

Automated verification command: full staged `tools/build_common_fund.py`; the tenth suite is `tools/verify_justice.py`. Its predicate/native-source tests are not substitutes for these engine checks.
