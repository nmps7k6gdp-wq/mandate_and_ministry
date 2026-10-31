"""Discovery presentation; called only by the staged Censorate generator.

No engine/native override and no independent live publication entry point.
"""


def author(loc, events):
    def option(key, text, effect, tip, condition='', ai='base = 50', stress='', stress_if=''):
        name = loc(key, text)
        tooltip = loc(key+'_tt', tip)
        guard = 'mam_censor_intel_actor_trigger = yes '+condition
        impact = 'stress_impact = { '+stress+' }' if stress else ''
        if impact and stress_if:
            impact = 'if = { limit = { '+stress_if+' } '+impact+' }'
        return f'''option = {{ name = {name} trigger = {{ {guard} }}
         custom_tooltip = {tooltip}
         if = {{ limit = {{ {guard} }} {impact} hidden_effect = {{ {effect} }} }}
         ai_chance = {{ {ai} }}
        }}'''

    loc('intel_title', 'What the Confidential Papers Reveal')
    loc('intel_known', 'The papers name #bold [scope:mam_cen_intel_subject.GetShortUIName]#!. This is a discovery to answer, not a sentence already passed. I can call the official to account, bring the matter before the throne, or keep my own report quiet.')
    loc('intel_public', 'A criminal matter involving #bold [scope:mam_cen_intel_subject.GetShortUIName]#! has reached the Censorate. The office is too important for either the charge or its handling to pass without scrutiny. I can hear the official, examine the lawful grounds and seek advice before reporting to the throne. An accusation alone does not establish guilt.')
    loc('intel_unknown', 'A plot has been uncovered within the imperial court, but its author remains unnamed. I can put my officers on the trail or strengthen the intended victim\'s protection. Naming an enemy without tracing the plot would prove nothing.')
    loc('intel_trace_failed', '\n\nThe trail has broken off, or the plot ended before its author could be identified. No official has been named. Protection is still possible; another roll will not conjure up a culprit.')
    loc('intel_victim', '\n\nThe intended victim is [scope:mam_cen_intel_victim.GetShortUIName].')
    kinds = {
        1: 'The discovery concerns the siphoning of a public treasury.',
        2: 'The discovery concerns embezzlement.',
        3: 'The discovery concerns cheating in an imperial examination.',
        4: 'The discovery concerns an invitation to a foreign incursion.',
        5: 'The discovery concerns a conspiracy to seize sovereign power.',
        6: 'The discovery concerns a murder.',
        7: 'The discovery concerns an attempted murder.',
        20: 'The officers have traced a discovered murder plot to its author.',
        21: 'The officers have traced a discovered abduction plot to its author.',
        22: 'The officers have traced a discovered treasury-siphoning plot to its author.',
    }
    detail = []
    facts = []
    for kind, text in kinds.items():
        key = loc('intel_kind_'+str(kind), '\n\n'+text+' Native exposure and criminal proceedings remain separate from this inspection.')
        detail.append(f'triggered_desc = {{ trigger = {{ scope:mam_cen_intel_lead = {{ var:mam_cen_identified = 1 var:mam_cen_intel_kind = {kind} }} }} desc = {key} }}')
        fact_key = loc('facts_intel_'+str(kind), '\n\n'+text+' The original discovery is retained in the inspection; it has not created an automatic arrest or criminal sentence.')
        facts.append(f'triggered_desc = {{ trigger = {{ scope:mam_cen_file = {{ has_variable = mam_cen_native_fact var:mam_cen_native_fact = {kind} }} }} desc = {fact_key} }}')
    for kind,text in {
        30:'A public criminal record is accompanied by a native legal reason against the official. The inquiry must distinguish the right to proceed from proof of the alleged act.',
        31:'Someone holding a native legal reason has formally referred the accusation. Their claim is on record; the Censor has not adopted it as a verdict.',
        32:'The official has been taken into custody within the empire. The circumstances and the grounds for proceeding deserve examination. Detention does not prove guilt, and this review does not release the prisoner.',
    }.items():
        key=loc('intel_kind_'+str(kind),'\n\n'+text)
        detail.append(f'triggered_desc = {{ trigger = {{ scope:mam_cen_intel_lead.var:mam_cen_intel_kind = {kind} }} desc = {key} }}')

    opts = [
        option('intel_open', 'Require #bold [scope:mam_cen_intel_subject.GetShortUIName]#! to answer this discovery.',
               'mam_censor_intel_open_effect = yes',
               'Open one inspection of the named official, preserving this discovery as a supported factual lead. The official can answer, challenge your methods or seek a defender. No title, money, secret exposure or criminal sentence changes now.',
               'mam_censor_intel_can_open_trigger = yes mam_censor_officer_trigger = yes scope:mam_cen_intel_lead.var:mam_cen_intel_kind < 30',
               'base = 100 modifier = { add = 80 has_trait = just } modifier = { add = 60 has_trait = diligent } modifier = { add = 30 has_trait = honest }'),
        option('public_open', 'Hear #bold [scope:mam_cen_intel_subject.GetShortUIName]#! and examine the accusation.',
               'mam_censor_intel_open_effect = yes',
               'Open one inspection of the senior official. This records the accusation or detention, not guilt. The official may answer from custody; a minister can intervene, and Justice can assess the current native legal grounds. No arrest, release, conviction or title transfer occurs now.',
               'mam_censor_intel_can_open_trigger = yes mam_censor_officer_trigger = yes scope:mam_cen_intel_lead.var:mam_cen_intel_kind >= 30',
               'base = 150 modifier = { add = 100 has_trait = just } modifier = { add = 75 has_trait = diligent } modifier = { add = 50 has_trait = compassionate }'),
        option('intel_imperial_review', 'Review the conduct of #bold [scope:mam_cen_intel_subject.GetShortUIName]#! under my own seal.',
               'mam_censor_intel_open_effect = yes',
               'Open imperial review of the matter concerning the named Censor. They cannot investigate or judge themselves. Allegations remain distinct from supported misconduct. You decide the administrative disposition; no automatic exposure, release, money transfer or criminal sentence.',
               'mam_censor_intel_can_open_trigger = yes mam_censor_emperor_trigger = yes',
               'base = 120 modifier = { add = 80 has_trait = just }'),
        option('intel_memorial', 'Place the discovery against #bold [scope:mam_cen_intel_subject.GetShortUIName]#! before the Dragon Throne.',
               'scope:mam_cen_intel_lead = { set_variable = { name = mam_cen_urgent value = 1 } } mam_censor_intel_open_effect = yes',
               'Submit a supported memorial directly to the emperor without first hearing the official. The emperor may censure, protect, return it for further work or authorize a guarded removal. This does not automatically expose a secret or grant an imprisonment reason.',
               'mam_censor_intel_can_open_trigger = yes mam_censor_officer_trigger = yes scope:mam_cen_intel_lead.var:mam_cen_intel_kind < 30',
               'base = 20 modifier = { add = 100 scope:mam_cen_intel_lead = { OR = { var:mam_cen_intel_kind = 4 var:mam_cen_intel_kind = 5 var:mam_cen_intel_kind >= 20 } } } modifier = { add = 80 has_trait = vengeful scope:mam_cen_intel_subject = { has_relation_rival = root } } modifier = { add = 45 has_trait = ambitious }'),
        option('public_memorial', 'Put the handling of #bold [scope:mam_cen_intel_subject.GetShortUIName]#!\'s case before the emperor.',
               'scope:mam_cen_intel_lead = { set_variable = { name = mam_cen_urgent value = 1 } } mam_censor_intel_open_effect = yes',
               'Refer the accusation or detention directly to the emperor. The referral creates no proof, criminal reason or release. Without supported misconduct or separately verified current legal grounds, an administrative removal still incurs the existing custom Tyranny consequence.',
               'mam_censor_intel_can_open_trigger = yes mam_censor_officer_trigger = yes scope:mam_cen_intel_lead.var:mam_cen_intel_kind >= 30',
               'base = 20 modifier = { add = 75 has_trait = ambitious } modifier = { add = 100 has_trait = vengeful scope:mam_cen_intel_subject = { has_relation_rival = root } } modifier = { factor = 0.3 has_trait = just }'),
        option('intel_trace', 'Follow the messengers and find who gave the order.',
               'scope:mam_cen_intel_lead = { mam_censor_intel_trace_effect = yes }',
               'Attempt to identify the actual author in 7 days. Current chance: [scope:mam_cen_trace_chance|0]%, from your Intrigue/Learning against the author\'s Intrigue/Diplomacy and relevant traits (10-90%). The plot must still exist. One attempt per discovered plot; failure names nobody. Succession during tracing invalidates that investigator\'s attempt.',
               'scope:mam_cen_intel_lead = { var:mam_cen_identified = 0 NOT = { has_variable = mam_cen_trace_finished } } mam_censor_officer_trigger = yes',
               'base = 100 modifier = { add = 70 has_trait = diligent } modifier = { add = 50 has_trait = paranoid } modifier = { factor = 0.2 has_trait = lazy }'),
        option('intel_guard', 'Place #bold [scope:mam_cen_intel_victim.GetShortUIName]#! under closer protection.',
               'scope:mam_cen_intel_victim = { add_character_modifier = { modifier = mam_cen_guarded months = 6 } } scope:mam_cen_intel_lead = { mam_censor_intel_finish_effect = yes }',
               'Give the living intended victim closer protection for 6 months: hostile scheme phases against them take 5 days longer. This ends this intelligence referral without accusing anyone or ending the native plot. The modifier refreshes without stacking.',
               'exists = scope:mam_cen_intel_victim scope:mam_cen_intel_victim = { is_alive = yes top_liege = title:h_china.holder } scope:mam_cen_intel_lead = { var:mam_cen_intel_kind >= 20 }',
               'base = 15 modifier = { add = 40 scope:mam_cen_intel_lead = { has_variable = mam_cen_trace_finished var:mam_cen_identified = 0 } } modifier = { add = 40 has_trait = compassionate }'),
        option('intel_hold', 'Keep these papers under seal. I will decide later.',
               'scope:mam_cen_intel_lead = { mam_censor_intel_defer_effect = yes }',
               'Set this referral aside for 30 days, allowing other work to proceed. The lead expires after 2 years without a new penalty. Existing native knowledge and plots remain unchanged.',
               ai='base = 5 modifier = { add = 30 has_trait = fickle } modifier = { add = 20 has_trait = lazy }'),
        option('intel_bury', 'I will not pursue my report.',
               'scope:mam_cen_intel_lead = { mam_censor_intel_finish_effect = yes }',
               'Close this referral without a sanction or reward. This does not erase anyone\'s native secret knowledge, stop a plot, or prevent an independently informed emperor from reviewing the Censor. The same discovery cannot generate repeated rewards.',
               ai='base = 10 modifier = { add = 50 has_trait = craven } modifier = { add = 65 has_trait = arbitrary exists = scope:mam_cen_intel_subject scope:mam_cen_intel_subject = { has_relation_friend = root } } modifier = { add = 50 has_trait = deceitful exists = scope:mam_cen_intel_subject exists = scope:mam_cen_intel_subject.house scope:mam_cen_intel_subject.house = root.house } modifier = { add = 50 has_trait = ambitious exists = scope:mam_cen_intel_subject scope:mam_cen_intel_subject = { mam_censor_shared_faction_trigger = { OTHER = root } } } modifier = { factor = 0.05 has_trait = just }',
               stress='just = 15 diligent = 10', stress_if='scope:mam_cen_intel_lead = { var:mam_cen_identified = 1 var:mam_cen_intel_kind < 30 }'),
    ]
    # Unlike an ordinary inspection, an unidentified plot never binds the hidden
    # author as a portrait/name. The engine's owner pointer is not public proof.
    events.append('''mam_censor.101 = {
     type = character_event theme = intrigue title = mam_cen.intel_title
     left_portrait = { trigger = { exists = scope:mam_cen_intel_subject scope:mam_cen_intel_subject = { is_alive = yes } }
      character = scope:mam_cen_intel_subject animation = worry }
     right_portrait = { trigger = { exists = scope:mam_cen_intel_victim scope:mam_cen_intel_victim = { is_alive = yes } }
      character = scope:mam_cen_intel_victim animation = thinking }
     trigger = { mam_censor_intel_actor_trigger = yes }
     desc = {
      first_valid = {
       triggered_desc = { trigger = { scope:mam_cen_intel_lead.var:mam_cen_intel_kind >= 30 } desc = mam_cen.intel_public }
       triggered_desc = { trigger = { scope:mam_cen_intel_lead.var:mam_cen_identified = 1 } desc = mam_cen.intel_known }
       desc = mam_cen.intel_unknown
      }
      '''+'\n'.join(detail)+'''
      triggered_desc = { trigger = { scope:mam_cen_intel_lead = { var:mam_cen_identified = 0 has_variable = mam_cen_trace_finished } } desc = mam_cen.intel_trace_failed }
      triggered_desc = { trigger = { exists = scope:mam_cen_intel_victim } desc = mam_cen.intel_victim }
      triggered_desc = { trigger = { scope:mam_cen_intel_lead.var:mam_cen_intel_kind >= 30 exists = scope:mam_cen_charge_accuser } desc = mam_cen.facts_public_source }
     }
     '''+'\n'.join(opts)+'''
     option = { name = mam_cen.stale trigger = { mam_censor_intel_actor_trigger = no } ai_chance = { base = 100 } }
    }''')
    return '\n'.join(facts)
