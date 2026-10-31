# Senior officials and criminal accusations: dev.65

Authorized 2026-10-31: the user asked the Censor to respond when officials, especially kingdom and empire holders, are accused of crimes. This adds a public-proceedings adapter to the accepted dev.64 discovery/inspection flow. No custom trial or register returns, and no Personnel/Revenue implementation is rewritten.

## What reaches the Censor

| Source | Requirement | What it establishes |
|---|---|---|
| Public criminal standing | Serving kingdom/territorial empire governor or central minister; public criminal trait/status **and** a current native imprisonment reason held by emperor or immediate liege | A public legal matter exists; not proof of a particular alleged act |
| Formal referral | Emperor, minister or immediate liege personally holds a native imprisonment reason against the senior official and uses **Censor: Refer a Criminal Accusation** in Ministry | That actual authority filed an accusation; it does not grant a new criminal reason |
| Custody | Senior official is held by someone within the Chinese imperial realm; not currently at war with their captor | An important official is detained; neither lawful arrest nor guilt is assumed |

Public records include Murderer, Denounced and Excommunicated where an actual legal reason exists, plus traits the native `has_any_criminal_trait_in_rite_trigger` regards as criminal under the emperor's current rite. Merely shunned, disliked, sinful or hidden traits are insufficient. This public channel intentionally differs from the narrow confidential-secret list: a public doctrinal crime can be reviewed if native law actually provides grounds. No hidden religious or sexual secret is searched or exposed by this adapter.

The native `on_trait_gained` and `on_imprison` actions are extended additively. Weekly recovery catches existing public grounds, later-applied reasons and eligible custody in old saves. At most one senior public matter is adopted per poll. Murder records, detention and empire-tier offices receive selection priority. Ordinary private secret intake still runs separately. Lower governors remain available for manual inspections and supported confidential discoveries, without mass automatic public-charge monitoring.

Foreign custody and current enemy-war captivity are excluded from automatic detention referral. Continued custody after a war can be reviewed as detention; it is never labelled a proved criminal offense. The emperor is not an ordinary inspection subject, and no unlanded person becomes a new independent subject.

## How the case plays

The existing one-at-a-time intelligence brief names the official and identifies whether the source is a public record, a formal referral or custody. The actual referring authority/captor is linked. A Censor can hear the official, submit the matter directly to the emperor, defer or decline it. Just/Diligent Censors strongly favor a hearing; Ambitious/Vengeful Censors more readily escalate, especially against a real rival. Other participating officials retain their existing personality and relationship choices.

An inspection can retain **one confidential discovery plus one public matter**, without overwriting either. Matching early referrals return to the official's hearing and invalidate old choices; matters arriving after imperial presentation wait. A detained subject may answer the stage-2 letter from custody. This grants neither freedom nor another office. Private favor bargaining is unavailable while the subject is imprisoned, avoiding an unanswered bargain stage.

The Censor can examine the legal grounds directly or ask Justice for advice. Emperor can perform one explicit check if an unreviewed matter reaches the throne, including a recused allegation against the current Censor. Checking records a reviewer and date, and whether emperor/current liege actually holds a native imprisonment reason. **No roll turns an allegation into guilt.** Skills continue to affect actual evidence work and political reception; they do not randomly alter the existence of a native legal reason.

## Grounds, proof and consequences

`mam_censor_supported_trigger` remains restricted to actual admitted/corroborated conduct and independent native discovery facts. A public accusation, detention or completed legal check is not added to that trigger. Existing genuine misconduct can still be established independently or by an explicit act of obstruction during the inspection.

A separate `mam_censor_public_fitness_trigger` requires a completed positive review, a currently eligible senior official, and native grounds that **still exist at commitment**. It permits an explicitly labelled administrative fitness censure: -50 Influence, two-year Publicly Censured (-15% monthly Influence, -5 General Opinion), and resentment toward an unconflicted Censor. It does not create a conviction, arrest, release or criminal reason, and does not grant Trusted Inspector just for reading an existing warrant. The extra public-fitness censure is hidden while the official already has the censure modifier.

Emperor can retain the official or use the existing guarded retirement path. Supported misconduct or separately reviewed current legal grounds avoid the existing custom unsupported-removal Tyranny consequence. Justification is captured immediately **before** a successful native handoff, so losing the old office/consuming grounds during retirement does not retrospectively make a lawful action tyrannical. Otherwise the existing 10 Tyranny applies only after confirmed removal. Failed handoffs receive no timeout, success notice or extra Tyranny.

Prisoners cannot use the guarded retirement path. This adapter neither releases them nor interferes with native Justice's arrest, pardon, punishment or criminal-right consumption. Missing grounds can reflect a pardon, consumption, changed authority or other native state; it never proves innocence or abusive detention on its own. Censor can object to the handling and seek the existing imperial response, without inventing a crime against the original accuser/captor.

## State and duplicate protection

Public lead kinds 30 (public standing), 31 (formal referral), 32 (detention) use the existing institutional lead stories, queue capacity eight, deferral/expiry and review-token guards. They are prioritized before ordinary unpresented secret leads, but do not preempt an already presented brief or inspection.

`mam_cen_public_case`, source kind, actual authority, date, review author and result remain on the inspection story. `mam_cen_public_record` is a character index to the lead; `mam_cen_public_seen` is a durable per-person episode marker. The marker survives archival deletion and prevents the same continuing grounds/custody from regenerating cases every week or ten years. It clears only after grounds are absent, custody has ended, and the previous referral/inspection is no longer active. An already resolved confidential murder is not sanctioned again merely because a matching public Murderer record appears, where that exact prior source is retained.

Native imprisonment reasons expose no verified stable per-offense identity in this adapter. It therefore groups continuing public grounds/custody conservatively as one episode, rather than guessing that every poll represents a new crime. Genuinely different native secrets can still enter through their own source identities, and manual inspection remains available. Formal referrals currently provide a player action; AI public-record and custody responses use automatic intake.

## Sources and verification

Source: `tools/templates/censor/public_crime.txt`, the existing intelligence template and Censor generators. Runtime footprint remains 11 files and the existing 15 event IDs; added choices reuse guarded stages. No native override is added. Four reviewed native definitions are appended to the boundary manifest; the preceding 15 hashes are unchanged.

The verifier checks allegation/proof separation, senior scope, role-owned filing, actual native rights, custody reply scope, no automatic criminal/custody mutation, duplicate guards, pre-retirement justification and current-law revalidation. Three source-predicate tests exercise unproved allegations, withdrawal of grounds and required positive review using supplied native fact booleans. They are **not an engine simulation**.

Run the full staged builder and [CENSOR-TESTING.md](CENSOR-TESTING.md). No new engine, visual, save migration, observer-balance or crash-clearance acceptance is claimed.

Final dev.65 source verification passed all nine staged suites, 159 protected-file checks, 19 native boundary hashes and 13 Censor tests. The three new public-predicate tests passed. Publication changed only final outputs; hot reload remains enabled. In-game acceptance is still pending.
