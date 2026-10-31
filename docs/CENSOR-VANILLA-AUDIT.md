# Censor: vanilla gameplay and compatibility audit

Read-only installed-source audit, 2026-10-30, against MAM dev.61. This is design evidence, not implementation or an engine playtest. Read this before [the revised proposal](CENSOR-REVAMP-DRAFT.md).

Later implementation boundary: the user separately authorized Justice at dev.66. [JUSTICE-IMPLEMENTATION.md](JUSTICE-IMPLEMENTATION.md) documents its narrow native authority/observation wrappers, exact original-cost/acceptance compiler and explicit prospective warrant. This earlier Censor audit is not a prohibition on that newly authorized module. Native secret discovery/blackmail and their rewards remain native; passive receipts and accusations still are not automatic crimes.

## Main finding

Vanilla Censor already has a substantial intelligence and political-leverage loop. The earlier draft checked ordinary Spymaster tasks but missed the dedicated ministerial Find Secrets scheme. A second generic investigation/search system would duplicate native gameplay. The revised proposal concentrates on supported MAM official records and formal imperial reporting, preserving native discovery, hooks, rewards and criminal mechanics.

## What vanilla already provides

| Native feature | Actual behavior | Design boundary |
|---|---|---|
| Council position | Censor occupies `councillor_spymaster`. Ordinary Disrupt Schemes, Support Schemes and Find Secrets task definitions remain; Find Secrets has AI-specific visibility conditions. | Preserve tasks, targeting, visibility and council effects. The ministerial scheme below is a separate native action. |
| Minister: Find Secrets | Censor or Justice can start `celestial_minister_find_secrets_scheme` against an eligible fellow subject's court through `censor_find_secrets_interaction`. Title/council-seat requirements apply. It is a political scheme with agents, phases and success handling. | No second court-secret search, progress meter or free parallel investigation. Preserve Justice access. |
| Secret discovery | Monthly logic searches major/minor secrets of the target, courtiers/guests and direct vassals through native selection helpers. Relevant discovered secrets are revealed to employer and investigating minister. | A custom option cannot conceal a secret already revealed to the emperor. Do not impose new titled-official restrictions on vanilla court espionage. |
| Censor hook opportunity | When native secret conditions fail, the Censor can receive a fabricated-hook opportunity: keep it personally, give it to the employer, or decline. Options already have costs, rewards, opinions, personality weights and Honest stress. | No duplicate hook/bribery subsystem or rewards. A fabricated hook is not proof of an official-record allegation. |
| Scheme completion | With a counted discovery, `.8066` ends the scheme and offers personal Gold or, when eligible, Treasury. Failure `.8067` ends it and loses Influence. | Preserve currency choice. The successful event directly adds the resource; it does not show a corresponding employer debit. Do not describe this as a verified Treasury transfer or add another completion reward. |
| Blackmail | Eligible Censor blackmail gives the normal hook plus conditional Merit/Influence and the Dynastic Cycle minister-blackmail catalyst. | Do not pay twice or fire a second catalyst for the same action. |
| Career influence | `influence_meritorious_career_interaction` has minister options for succession score, Merit and family examination bypass. These are shared minister privileges. | Preserve Personnel and examination honors. Bypassing a pass requirement is not earning a top-placement honor. |
| Grand Secretariat | `grand_censor_law` can designate the Censor as Director. An accepted native request to become Director can change the controlling law. | Chancellor is not always Censor's superior. Respect current law; serious/conflicted reporting needs an imperial route. |
| Intelligence expenditure | A Treasury-holding Censor gets native Treasury agent-bribe options; execution pays Treasury to the agent's Gold. Giving the employer a fabricated hook also has a native Treasury cost when applicable; keeping it personally costs Gold. | Budget for actual native costs. Preserve intentional native currency conversion without making general public grants personal gifts. No second debit or new common-fund payment per phase. |
| Other ministry/Director activity | Native development, control, Census and canal definitions contain Censor-related eligibility/behavior. Some permissions depend on the Director role and project conditions. | Do not present all projects as unconditional Censor powers; preserve existing project eligibility and funding bridges. |

Holding the title alone does not make every action available: seat synchronization, government, realm, imprisonment and scheme/target checks still matter. Council modifiers also retain native intrigue/scheme benefits.

### Native AI already acts

Find Secrets has AI willingness and peer-vassal target selection. AI entry gates include peace and no existing political scheme. Monthly processing, AI semiannual follow-up and native option weights drive outcomes. Honest/Loyal, greed/honor, relationships, affordability and other contextual checks influence choices.

An AI Censor waiting during war or while occupied by another political scheme is therefore not automatically missing a scheduler. Frequency and completion balance still require CK3 observation. Do not bypass these limits with extra automatic secret searches.

## Justice is already present in vanilla

The shared scheme has a distinct Justice branch, `.8071`, for known criminals: native imprisonment, referral to the proper liege, pardon or inaction, subject to option checks. Ordinary imprisonment/pardon interactions also have Justice rules. Eligible Justice secret exposure has native Merit/Influence and a Dynastic Cycle exposure catalyst.

Removing MAM's custom Censor-Justice investigation/trial/register did not delete vanilla Justice. A future Justice proposal must build on those actions. Censor's shared scheme access does not grant it Justice's special criminal options.

The noble-family purge interaction recognizes prisoners held by Censor/Justice, but its actor is the eligible human celestial emperor. It is not an independent Censor power to purge families.

## Corrections to the first draft

| Earlier idea | Revised treatment |
|---|---|
| Independent 90-180-day investigation alongside native work | Drop the generic parallel search. Use native discovery for secrets; scrutinize a specific supported official record/act. |
| New generic secret, hook, bribe and investigation rewards | Keep native versions. Any distinct administrative recognition needs separate approval and a once-only guard. |
| Conceal any completed finding | Only still-private custom records can be withheld. Never erase known secrets or undo notifications. |
| Chancellor controls all escalation | Respect Secretariat law and direct imperial reporting; avoid self-review. |
| Native secrets automatically become new criminal files | No automatic conversion. An administrative memorial is not a conviction or imprisonment reason. |
| Quarterly scanning creates another case bureaucracy | At most a bounded supported-record lead, no register, court search or accusation quota. |

## Existing MAM bridges and limitations

- Personnel has passive patronage records and successful-appointment linkage. A qualified relative, lawful favor or unrelated gift is not automatically misconduct. An adapter must establish a specific obligation and act.
- Revenue project receipts record legitimate actor/office/project/amount/date and approver where available. A receipt alone proves neither theft nor missing approval. The proposed richer unauthorized-release ledger was not established in the inspected common-fund runtime.
- No inspected MAM runtime definition overrides the ministerial Find Secrets interaction/scheme, `.8065-.8071` events, agent interaction or ministerial career influence. Existing central succession and public funding still affect the Censor office.
- Existing operating provision and special supplements are available for native intelligence costs. This audit adds no automatic funding request, dedicated allowance or approval gate. Test adequacy before tuning.
- Technical payment holds, incomplete scopes and failed transfers remain diagnostics, not corruption evidence.

## Recommended new value

**Later user feedback:** passive record reporting was rejected as insufficient. [Historical design](CENSOR-HISTORICAL-DESIGN.md) and [the revised proposal](CENSOR-REVAMP-DRAFT.md) now explore independent inspection, compelled answers, censure and impeachment. The native findings here remain evidence; the narrower recommendation below is retained as audit history, not the current proposed limit on Censor authority.

**Native intelligence discovers secrets; the proposed extension scrutinizes supported official acts and submits administrative memorials.** Add the reporting/response layer, not another espionage engine.

A native-scheme outcome extension is a candidate integration point, not a verified API. Prototype it while preserving Justice, original follow-up, discovery counts, notifications and rewards. If incompatible, use a narrow document-review interaction for identified MAM records, without new secrets or parallel secret-search progress.

## Installed source map

Paths are relative to the read-only installed game directory `C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game`. Lines refer to this installation and may shift after updates.

| Source | Entry / lines |
|---|---|
| `common/council_positions/00_council_positions.txt` | Censor mapping/effects; ministry mapping at 535 |
| `common/council_tasks/00_spymaster_tasks.txt` | Disrupt 1; Support 205; Find Secrets 350 |
| `common/character_interactions/10_tgp_interactions.txt` | Career influence 4133; minister Find Secrets 11132; emperor-only purge 11235 |
| `common/schemes/scheme_types/tgp_dynastic_cycle_schemes.txt` | Minister Find Secrets 826 |
| `common/scripted_effects/00_scheme_scripted_effects.txt` | Follow-up preparation 12725 |
| `events/scheme_events/scheme_critical_moments_events.txt` | Follow-up `.8065` 8598; success `.8066` 8623; failure `.8067` 8666; discoveries `.8068` 8701 / `.8069` 8899; Censor hook `.8070` 9073; Justice `.8071` 9315 |
| `common/character_interactions/00_blackmail_interactions.txt` | Censor conditional rewards/catalyst around 148 |
| `common/character_interactions/00_character_interactions.txt` | Justice exposure rewards/catalyst around 1740-1767 |
| `common/character_interactions/00_invite_agent_to_scheme.txt` | Treasury-to-Gold payment 94-110; Treasury option gates 533 onward |
| `common/character_interactions/00_prison_interactions.txt` | Justice imprisonment/pardon rules |
| `common/laws/02_admininistrative_laws.txt` | `grand_censor_law` around 1535 |
| `common/character_interactions/00_diarch_interactions.txt` | Director request and accepted office-law change around 8627 onward |
| `common/great_projects/types/00_ministry_projects.txt` | Development 1655; control 2163; Census 4005; inspect exact role conditions |
| `common/great_projects/types/00_great_project_types.txt` | Grand canals 6998; inspect exact role conditions |
| `localization/english/dlc/tgp/dlc_tgp_china_game_concepts_l_english.yml` | Censor/Justice/Director help around 165-200; executable definitions govern actual behavior |

## Verification and future test checklist

Completed: read-only tracing of interactions, scheme, preparation/result/opportunity events, costs/rewards, tasks, career privileges, Secretariat law and existing MAM contracts. No runtime implementation or engine test.

Before approving implementation:

- [ ] Confirm ordinary task versus ministerial scheme as player Censor and Justice; check wartime/occupied-political-scheme AI gates.
- [ ] Observe native success, failure and hook opportunities; verify who learns secrets, resources, stress and once-only rewards.
- [ ] Recruit an agent with Treasury; verify public debit, personal recipient credit and adequate departmental provision.
- [ ] Verify native Justice criminal options remain independently completable.
- [ ] Test Censor and Chancellor separately as Director; ensure no conflicting superior/appeal routing.
- [ ] Prove a narrow MAM record adapter with supported, lawfully explained, unsupported and duplicate-record examples.
- [ ] If extending a native callback, deliberately compare installed source and preserve follow-up, agents, Justice, capacity and rewards.
- [ ] Preserve accepted Personnel, central succession, honors and common-fund project execution.

## Dev.64 discovery comparison (2026-10-31)

Read-only comparison of the installed 1.20.1.2 sources established:

- `common/on_action/scheme_on_actions.txt:on_scheme_discovered` has the discovered Scheme as root. Its existing victim-protection and celestial-siphoning catalyst effects remain native. The bridge appends an on_action; it does not replace the definition's effect. Native `hostile_scheme_discovery.2001` distinguishes a discovered plot from identifying an owner. The bridge therefore records an unnamed warning and requires a live opposed-skill tracing step before naming the real author.
- `common/secret_types/_secret_types.info` documents per-secret `on_discover` with Secret root and discoverer/owner/optional target. There is no verified global `on_secret_discovered` action. Instead of overriding every secret type, the adapter polls actual Censor-known secrets through native `random_known_secret` and `is_known_by`. Existing `task_find_secrets_reveal_selection` is presentation before revelation, not proof that the Censor already knows a secret.
- The seven supported secret types' native validity/crime/exposure definitions are retained: siphoned treasury, embezzler, exam cheater, incursion request, coup, murder and attempted murder. No native punishment/reward is replayed. A Secret can carry variables (native embezzlement stake is an example); the bridge writes only its own intake identity metadata.
- Native `every_scheme` on a character is used by Support Schemes and activity invitation logic. The bridge re-finds a real plot under its actual owner by its own saved identity instead of retaining a transient Scheme pointer. Failed/expired tracing names nobody. The native artifact resistance modifier demonstrates `enemy_hostile_scheme_phase_duration_add`, used for six-month victim protection.

Eleven newly reviewed native definitions were appended to `CENSOR-NATIVE-BOUNDARIES.json`; its four earlier hashes were retained. No installed native file or existing secret/scheme definition was edited. Polling can miss a secret exposed/deleted before intake, and bounded callbacks do not cover every world's plot. These limits are explicit in [CENSOR-DISCOVERY.md](CENSOR-DISCOVERY.md); engine tests remain pending.
- [ ] After implementation only: test death/office changes, save/load, stale events, once-only dispositions and bounded popup/AI behavior.

## Dev.65 public accusation comparison

The installed native sources provide `on_trait_gained` (root character, `scope:trait`) and `on_imprison` (root prisoner, `scope:imprisoner`). Native imprisonment interaction evaluates the actual actor's `has_imprisonment_reason` separately from Justice's office privilege; the adapter therefore does not infer a criminal reason merely from holding Justice. The rite helper distinguishes genuinely criminal public traits from merely shunned traits. Four full definitions were deliberately appended to the native boundary manifest, retaining all earlier hashes.

There is no verified universal global criminal-accusation or secret-exposure on_action. Additive trait/custody hooks, bounded weekly public-state recovery and an explicit legal-reason holder's referral cover supported cases without overriding every native event/secret. Native `.imprisoner` is used in existing health/diarchy triggers for actual custody. Native reason identity does not expose a verified per-offense record through this adapter: continuing grounds/custody are conservatively grouped, not converted into a new crime every poll. See [the implemented contract](CENSOR-PUBLIC-ACCUSATIONS.md).
