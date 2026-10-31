"""Author Censorate runtime in the existing isolated common-fund build.

No native overrides, no edits to accepted Personnel/Revenue definitions. Templates
are source; all .txt/.yml outputs receive BOM. Use build_common_fund.py to publish.
"""
from pathlib import Path
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]
LOC = {}
EVENTS = []
EDGES = []


def loc(key, text):
    key = 'mam_cen.' + key
    assert key not in LOC, key
    LOC[key] = text
    return key


def opt(key, text, effects='', tip='', condition='', ai='base = 50', stress='', stress_if=''):
    ai += ' ' + SKILL_AI.get(key, '')
    name = loc(key, text)
    tt = 'custom_tooltip = ' + loc(key+'_tt', tip) if tip else ''
    guard = 'mam_censor_actor_trigger = yes ' + condition
    # Recheck all availability at commitment; stale options apply no stress either.
    impact = ('stress_impact = { '+stress+' }') if stress else ''
    if impact and stress_if:
        impact = 'if = { limit = { '+stress_if+' } '+impact+' }'
    if key in ('correct', 'remove_official'):
        tt += ''' if = { limit = { scope:mam_cen_file.var:mam_cen_abuse = 0
         scope:mam_cen_file = { mam_censor_supported_trigger = yes }
         OR = { AND = { mam_censor_officer_trigger = yes this != scope:mam_cen_subject }
          scope:mam_cen_file = { exists = var:mam_cen_author var:mam_cen_author != var:mam_cen_subject var:mam_cen_author = { is_alive = yes } }
         }
        } custom_tooltip = mam_cen.trust_consequences }'''
    if key == 'mediate':
        tt += ''' if = { limit = { diplomacy >= 15 } custom_tooltip = mam_cen.mediation_skilled_tt }
         else_if = { limit = { diplomacy < 8 } custom_tooltip = mam_cen.mediation_unskilled_tt }'''
    return f'''option = {{ name = {name}
     trigger = {{ {guard} }}
     {tt}
     if = {{ limit = {{ {guard} }}
      {impact}
      hidden_effect = {{ {effects} }}
     }}
     ai_chance = {{ {ai} }}
    }}'''


def event(n, title, prose, options, extra='', letter=False):
    title = loc(f'{n}_title', title)
    desc = loc(f'{n}_desc', prose)
    intro = f'desc = {desc}'
    if n == 7:
        recused = loc('7_recused', 'The confidential papers concern [scope:mam_cen_subject.GetShortUIName], whose own seal can offer no impartial judgment of this allegation. The decision rests with me. I may uphold a supported censure, retain the official, or require a lawful transfer of office.')
        intro = 'first_valid = { triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_recused } } desc = '+recused+' } desc = '+desc+' }'
    if n == 2:
        public_reply = loc('2_public', 'A criminal accusation concerning you has reached the Censorate. I will hear your account of the charge and of how it has been pursued. You may answer from custody. Neither detention nor this demand for an answer establishes your guilt.')
        intro = 'first_valid = { triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_public_case } } desc = '+public_reply+' } desc = '+desc+' }'
    kind = ('type = letter_event sender = scope:mam_cen_censor opening = { desc = mam_cen.opening }'
            if letter else '''type = character_event theme = intrigue
             left_portrait = { character = scope:mam_cen_subject animation = worry }
             right_portrait = { trigger = { exists = scope:mam_cen_censor scope:mam_cen_censor = { is_alive = yes this != scope:mam_cen_subject } }
              character = scope:mam_cen_censor animation = thinking }''')
    EVENTS.append(f'''mam_censor.{n} = {{
     {kind} title = {title}
     trigger = {{ mam_censor_actor_trigger = yes }}
     desc = {{ {intro} {extra} }}
     {' '.join(options)}
     option = {{ name = mam_cen.stale trigger = {{ mam_censor_actor_trigger = no }} ai_chance = {{ base = 100 }} }}
    }}''')


def setv(key, val):
    return f'set_variable = {{ name = mam_cen_{key} value = {val} }}'


def filefx(body):
    return 'scope:mam_cen_file = { '+body+' }'


def move(stage, days=14):
    return f'mam_censor_move_effect = {{ STAGE = {stage} DAYS = {days} }}'


def close(result):
    return f'mam_censor_close_effect = {{ RESULT = {result} }}'


def author():
    return setv('author', 'root')


def trait(name, amount=60):
    return f'modifier = {{ add = {amount} has_trait = {name} }}'


SUPPORTED = 'scope:mam_cen_file = { mam_censor_supported_trigger = yes }'
UNSUPPORTED = 'scope:mam_cen_file = { mam_censor_supported_trigger = no }'
PUBLIC_FITNESS = 'scope:mam_cen_file = { mam_censor_public_fitness_trigger = yes }'
UNJUSTIFIED = 'scope:mam_cen_file = { mam_censor_supported_trigger = no mam_censor_public_fitness_trigger = no }'
ABUSE = 'scope:mam_cen_file = { var:mam_cen_abuse = 1 }'

# Numeric native AI weights; human actors retain their choices. These are
# political considerations, not rolls that manufacture or erase evidence.
SKILL_AI = {
 'verify': 'modifier = { add = 35 OR = { stewardship >= 15 learning >= 15 } }',
 'consult': 'modifier = { add = 25 learning < 8 }',
 'cooperate': 'modifier = { add = 20 diplomacy >= 15 }',
 'withhold': 'modifier = { add = 20 intrigue >= scope:mam_cen_censor.intrigue has_trait = deceitful }',
 'defend': 'modifier = { add = 25 diplomacy >= 15 }',
 'safeguards': 'modifier = { add = 25 learning >= 15 '+ABUSE+' }',
 'impeach': 'modifier = { factor = 0.6 has_trait = craven exists = scope:mam_cen_defender scope:mam_cen_defender = { diplomacy >= root.diplomacy } }',
 'imperial_censure': 'modifier = { add = 25 exists = scope:mam_cen_author scope:mam_cen_author = { diplomacy >= 15 } } modifier = { add = 20 learning >= 15 '+SUPPORTED+' }',
 'protect': 'modifier = { add = 30 scope:mam_cen_subject = { diplomacy >= 15 } } modifier = { add = 35 exists = scope:mam_cen_defender scope:mam_cen_defender = { diplomacy >= 15 } }',
 'remove_official': 'modifier = { add = 20 learning < 8 '+UNSUPPORTED+' exists = scope:mam_cen_author scope:mam_cen_author = { intrigue >= 15 } }',
 'rebuke': 'modifier = { add = 35 OR = { intrigue >= 15 learning >= 15 } scope:mam_cen_file = { has_variable = mam_cen_fabricator } }',
 'yield': 'modifier = { add = 25 exists = scope:mam_cen_author scope:mam_cen_author = { diplomacy >= 15 } }',
 'mediate': 'modifier = { add = 40 diplomacy >= 15 }',
 'deny_link': 'modifier = { add = 25 intrigue >= scope:mam_cen_censor.intrigue has_trait = deceitful }',
 'return_false': 'modifier = { add = 20 stewardship >= 15 has_trait = deceitful }',
}


def make_events():
    loc('opening', 'Concerning the conduct of public office,')
    loc('stale', 'These papers have been overtaken by events.')
    loc('facts_document', '\n\nThe surviving papers connect a private payment with an appointment. They establish an exchange to explain; they do not turn every favor into a crime.')
    loc('facts_proof', '\n\nThe payment and appointment linkage has now been corroborated.')
    loc('facts_no_proof', '\n\nThe inquiry has not established misconduct. The court can still debate an official\'s judgment without treating suspicion as a proved charge.')
    loc('facts_payment_unproved', '\n\nThe alleged connection between a private payment and an appointment remains uncorroborated.')
    loc('facts_obstruction', '\n\nAn explicit order to withhold records or turn away the inquiry is recorded separately from the original concern.')
    loc('facts_receipt', '\n\nA public project contribution appears in the accounts. It records legitimate expenditure; its presence is no evidence of theft.')
    loc('facts_abuse', '\n\nThe inspection itself has become contentious: threats or a demand for private advantage are recorded against [scope:mam_cen_abuser.GetShortUIName].')
    loc('facts_coercion', '\n\nA confession was demanded under threat. It has not been treated as independent corroboration.')
    loc('facts_fabricated', '\n\nThe memorial asserts more than the admitted record supports. The accusation must not be mistaken for an established fact.')
    loc('facts_defense', '\n\n[scope:mam_cen_defender.GetShortUIName] has put their standing behind the accused. Disregarding this defense may widen the dispute beyond the original inquiry.')
    loc('facts_legal_caution', '\n\n[scope:mam_cen_legal_reviewer.GetShortUIName] disputes the framing of the accusation. The facts remain on record, alongside this disagreement.')
    loc('facts_safeguards', '\n\nA request for safeguards is on the record. Continuing the same pressure will now be a deliberate choice.')
    loc('facts_inherited', '\n\nThis file belongs to the office. Earlier threats and promises remain the responsibility of their recorded authors, including a former Censor.')
    loc('facts_handoff', '\n\nThe intended handoff could not be confirmed. No retirement or appointment timeout is claimed; another disposition is still required.')
    loc('facts_return', '\n\nA return certified during this inspection has been contradicted by its own surviving records. The unsupported attestation is a new official act, not a theft invented from missing money.')
    loc('facts_public', '\n\nA criminal accusation or detention is part of this inspection. Its existence is recorded separately from proof of the alleged act. The Censorate is reviewing the official\'s fitness for office and the handling of the matter; it has not issued a criminal sentence.')
    loc('facts_public_source', '\n\nThe referral records [scope:mam_cen_charge_accuser.GetShortUIName] as the authority who raised or acted on the matter. That does not make their claim an established finding.')
    loc('facts_public_checked', '\n\nThe current native legal grounds have been examined. Any recommendation based on those grounds must still satisfy them when acted upon; a pardon, consumed reason or changed authority can alter the position.')
    loc('facts_judicial', '\n\nA documented request for private benefit or an unauthorized judicial measure has been corroborated against this official. The actual author and act are on record. This finding alone is not a criminal warrant or conviction.')
    # Two short contextual paragraphs, rather than a repeated wall of flags.
    facts = '''first_valid = {
      triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_judicial_proof var:mam_cen_judicial_proof = 1 } } desc = mam_cen.facts_judicial }
      triggered_desc = { trigger = { scope:mam_cen_file.var:mam_cen_proof = 1 } desc = mam_cen.facts_proof }
      triggered_desc = { trigger = { scope:mam_cen_file.var:mam_cen_return_exposed = 1 } desc = mam_cen.facts_return }
      triggered_desc = { trigger = { scope:mam_cen_file.var:mam_cen_obstruction = 1 } desc = mam_cen.facts_obstruction }
      triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_receipt_seen } } desc = mam_cen.facts_receipt }
      triggered_desc = { trigger = { scope:mam_cen_file.var:mam_cen_document = 1 } desc = mam_cen.facts_payment_unproved }
      desc = mam_cen.facts_no_proof
     }
     first_valid = {
      triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_fabricator } } desc = mam_cen.facts_fabricated }
      triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_coerced } } desc = mam_cen.facts_coercion }
      triggered_desc = { trigger = { scope:mam_cen_file.var:mam_cen_abuse = 1 } desc = mam_cen.facts_abuse }
      triggered_desc = { trigger = { scope:mam_cen_file.var:mam_cen_legal < 0 } desc = mam_cen.facts_legal_caution }
      triggered_desc = { trigger = { scope:mam_cen_file.var:mam_cen_backing = -1 } desc = mam_cen.facts_defense }
      triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_safeguards } } desc = mam_cen.facts_safeguards }
     }'''
    facts += ''' triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_public_case } } desc = mam_cen.facts_public }
     triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_public_case } exists = scope:mam_cen_charge_accuser } desc = mam_cen.facts_public_source }
     triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_public_checked } } desc = mam_cen.facts_public_checked }'''
    event(1, 'Where the Censor Casts a Shadow',
          'The seal of [scope:mam_cen_office.GetName] carries authority, but authority invites scrutiny. I have opened an inspection of [scope:mam_cen_subject.GetShortUIName]. How I approach these papers will determine whether officials see a fair hearing, an obligation to answer, or a warning to the whole court.', [
        opt('quiet', 'Hear #bold [scope:mam_cen_subject.GetShortUIName]#! privately first.',
            filefx(setv('style', 1)+move(2, 7)),
            'Begin with a confidential request. No guilt, loss of office or payment follows. The official will choose how to answer.',
            ai='base = 65 '+trait('compassionate')+trait('patient')+trait('honest', 30)+trait('calm', 35)+trait('shy', 25)),
        opt('summon', 'Require the records of #bold [scope:mam_cen_office.GetName]#! under seal.',
            filefx(setv('style', 2)+move(2, 7)),
            'Issue a formal demand for records and an explanation. An explicit order to obstruct can become a separate supported finding; a lawful challenge is not obstruction.',
            ai='base = 75 '+trait('just')+trait('diligent')+trait('paranoid', 40)),
        opt('terror', 'Let #bold [scope:mam_cen_subject.GetShortUIName]#! fear what comes next.',
            'mam_censor_record_abuse_effect = yes '+filefx(setv('style', 3)+move(2, 7))+
            'scope:mam_cen_subject = { add_opinion = { target = root modifier = mam_cen_resentment } }',
            'Gain 10 Dread and Feared Censor for 3 years (+10 Dread baseline, -10 General Opinion). The official loses 25 Opinion of you for 5 years. Your threats are recorded and can provoke a counter-petition. They do not create proof.',
            condition='NOT = { has_character_modifier = mam_cen_restrained }',
            ai='base = 10 '+trait('sadistic', 110)+trait('arbitrary', 65)+trait('vengeful', 45)+trait('callous', 45)+' modifier = { factor = 0.05 OR = { has_trait = just has_trait = compassionate } }',
            stress='just = 20 honest = 15 compassionate = 20'),
        opt('decline', 'There is no need to pursue this inspection.', filefx(close(14)),
            'Close without penalties or a finding of guilt. The subject cannot be repeatedly selected to farm rewards.', ai='base = 8 '+trait('lazy', 45)+trait('craven', 20)),
    ], extra='triggered_desc = { trigger = { scope:mam_cen_file = { exists = var:mam_cen_originator var:mam_cen_originator = title:h_china.holder } } desc = mam_cen.imperial_request }')
    loc('imperial_request', '\n\nThe emperor has requested scrutiny. The request names a subject, not a predetermined guilty verdict.')

    event(2, 'An Answer Under Seal',
          'Your administration of [scope:mam_cen_office.GetName] is under inspection. Send an account of your conduct and the relevant records. I will hear your explanation before deciding what to put before the throne.', [
        opt('cooperate', 'Send the papers. I will answer for my decisions.',
            filefx(setv('response', 1)+'mam_censor_examine_effect = yes'),
            'Cooperate. Any existing supported appointment record can be corroborated. Lawful public payments and ordinary mistakes do not become crimes.',
            ai='base = 85 '+trait('honest', 100)+trait('just', 60)+trait('craven', 25)+' modifier = { add = 70 has_trait = craven scope:mam_cen_file.var:mam_cen_style = 3 }'),
        opt('contest', 'I will answer, but first put the limits of this demand in writing.',
            filefx(setv('response', 2)+setv('safeguards', 1)+'mam_censor_examine_effect = yes'),
            'Challenge the inspection\'s scope while providing an answer. This is not recorded as obstruction. The Chancellor or another eligible petitioner can take up the dispute.',
            ai='base = 35 '+trait('just', 40)+trait('arrogant', 30)+' modifier = { add = 100 scope:mam_cen_file.var:mam_cen_abuse = 1 }'),
        opt('withhold', 'Turn away the messengers. These papers will not leave my office.',
            filefx(setv('response', 3)+setv('obstruction', 1)+setv('concealed', 1)+'mam_censor_examine_effect = yes'),
            'Deliberately obstruct the inspection. This new act is recorded separately. If appointment papers are concealed, the current chance of recovering them is [scope:mam_cen_payment_chance|0]%, based on the inspector\'s and your relevant skills and traits. Failure does not prove the original allegation.',
            ai='base = 8 '+trait('deceitful', 75)+trait('arrogant', 30)+' modifier = { factor = 0.05 OR = { has_trait = honest has_trait = just } }',
            stress='honest = 20 just = 15'),
        opt('admit', 'The private payment was connected to the appointment. Let me explain.',
            filefx(setv('response', 4)+setv('admission', 1)+setv('proof', 1)+move(3, 14)),
            'Admit the documented exchange. The admission supports a finding, but correction, censure and imperial protection remain possible. No money is confiscated.',
            condition='scope:mam_cen_file.var:mam_cen_document = 1',
            ai='base = 15 '+trait('honest', 70)+trait('humble', 35)+trait('craven', 20), stress='arrogant = 15'),
    ], letter=True)

    event(3, 'Who Watches the Watcher?',
          'The inspection of [scope:mam_cen_subject.GetShortUIName] has reached my door. Some officials fear that resistance will be called guilt; others fear that protection will become a license for abuse. My intervention could steady this inquiry, or turn it into a contest between offices.', [
        opt('back_inquiry', 'The Censor must be allowed to ask difficult questions.',
            filefx(setv('backing', 1)+move(4)),
            'Support independent scrutiny without declaring the subject guilty. Your intervention is retained for the findings and imperial review.',
            ai='base = 55 '+trait('just', 60)+trait('diligent', 35)+' modifier = { add = 40 scope:mam_cen_file.var:mam_cen_abuse = 0 }'),
        opt('defend', 'I will put my name behind #bold [scope:mam_cen_subject.GetShortUIName]#!.',
            filefx(setv('backing', -1)+setv('defender', 'root')+move(4))+
            'scope:mam_cen_censor = { add_opinion = { target = root modifier = mam_cen_abandoned_me } } '+
            'scope:mam_cen_subject = { add_opinion = { target = root modifier = mam_cen_defended_me } }',
            'The official gains 20 Opinion of you for 5 years; the Censor loses 15 Opinion of you for 3 years. Your defense does not erase records and is weighed in the imperial response.',
            ai='base = 25 '+trait('compassionate', 35)+' modifier = { add = 100 has_relation_friend = scope:mam_cen_subject } modifier = { add = 70 house ?= scope:mam_cen_subject.house } modifier = { add = 45 mam_censor_shared_bloc_trigger = { OTHER = scope:mam_cen_subject } } modifier = { add = 50 mam_censor_shared_faction_trigger = { OTHER = scope:mam_cen_subject } } modifier = { add = 80 scope:mam_cen_file.var:mam_cen_abuse = 1 }'),
        opt('safeguards', 'Produce the facts, and stop governing through fear.',
            filefx(setv('safeguards', 1)+setv('challenger', 'root')+move(4)),
            'Demand safeguards and preserve a counter-petition about the inspection. The Censor can respect it or deliberately continue; the emperor can judge recorded abuses.',
            ai='base = 30 '+trait('just', 45)+trait('compassionate', 45)+' modifier = { add = 100 scope:mam_cen_file.var:mam_cen_abuse = 1 }'),
    ], extra=facts)

    event(4, 'The Papers Between Us',
          'The reply from [scope:mam_cen_subject.GetShortUIName] lies beside the interventions it has stirred. I can examine what survives, seek an independent view, or use the weight of my office to make resistance costly. The next step will be mine to defend.', [
        opt('verify', 'Check the records before I reach a finding.',
            filefx('mam_censor_check_return_effect = yes '+move(6, 21)),
            'Allow three weeks for comparison. If a false return exists, the current chance of exposing it is [scope:mam_cen_return_chance|0]%. Intrigue, Stewardship, Learning and relevant traits on both sides matter; Martial also matters for War/Marshal returns. Honest papers never become false because of a failed check.',
            ai='base = 70 '+trait('diligent', 55)+trait('patient', 35)+trait('paranoid', 50)),
        opt('public_compare', 'Examine the lawful grounds before I judge their fitness for office.',
            filefx('mam_censor_public_check_effect = yes '+move(6, 14)),
            'Record whether the emperor or current liege actually has a native imprisonment reason against this official. A verified, still-current reason can justify an administrative censure or recommendation to leave office. It does not prove the alleged crime, create another criminal reason or release a prisoner.',
            condition='scope:mam_cen_file = { has_variable = mam_cen_public_case NOT = { has_variable = mam_cen_public_checked } }',
            ai='base = 120 '+trait('just', 60)+trait('diligent', 60)),
        opt('consult', 'Ask Justice what these facts can actually support.',
            filefx(move(5, 14)),
            'Request a reasoned advisory opinion from the current Justice minister, or the emperor if Justice is implicated or unavailable. This is not a trial and grants no imprisonment reason.',
            condition='scope:mam_cen_file = { NOT = { has_variable = mam_cen_consulted } }',
            ai='base = 35 '+trait('just', 55)+trait('humble', 30)),
        opt('connected', 'Hear #bold [scope:mam_cen_connected.GetShortUIName]#! about the appointment.',
            filefx(move(8, 14)),
            'Hear the actual recorded payer. An evasive denial can be challenged with a current [scope:mam_cen_witness_chance|0]% chance, comparing your Intrigue/Learning with their Intrigue/Diplomacy and relevant traits. Admitted proof cannot be erased by eloquence. Kinship and faction alone are not evidence.',
            condition='scope:mam_cen_file.var:mam_cen_document = 1 scope:mam_cen_file.var:mam_cen_connected_heard = 0 exists = scope:mam_cen_connected scope:mam_cen_connected = { is_alive = yes is_imprisoned = no top_liege = scope:mam_cen_emperor }',
            ai='base = 50 '+trait('diligent', 50)),
        opt('coerce', 'They will confess before I put down my brush.',
            'mam_censor_record_abuse_effect = yes '+filefx(setv('coerced', 1)+move(6, 14)),
            'Gain 10 Dread and renew Feared Censor for 3 years (+10 Dread baseline, -10 General Opinion). Record coercion against you. A pressured confession does not supply independent proof and may provoke imperial restraint.',
            condition='NOT = { has_character_modifier = mam_cen_restrained } scope:mam_cen_file = { NOT = { has_variable = mam_cen_coerced } }',
            ai='base = 8 '+trait('sadistic', 100)+trait('arbitrary', 60)+trait('vengeful', 35)+trait('callous', 50)+' modifier = { factor = 0.02 OR = { has_trait = just has_trait = compassionate } }',
            stress='just = 25 honest = 20 compassionate = 25'),
        opt('bargain', 'A private obligation might settle this more quietly.',
            filefx(setv('settlement_attempted', 1)+setv('bargainer', 'root')+move(11, 7)),
            'Ask the official to owe you a favor in exchange for withholding this custom report. They can refuse or reveal the demand. No Gold or Treasury changes hands; known native secrets remain known.',
            condition='NOT = { has_character_modifier = mam_cen_restrained } scope:mam_cen_subject = { is_imprisoned = no } scope:mam_cen_file = { var:mam_cen_imperial_seen = 0 NOT = { has_variable = mam_cen_settlement_attempted } } NOT = { has_hook = scope:mam_cen_subject }',
            ai='base = 5 '+trait('greedy', 60)+trait('deceitful', 50)+' modifier = { factor = 0 OR = { has_trait = honest has_trait = just } }',
            stress='honest = 25 just = 25'),
    ], extra=facts)

    event(5, 'A Finding Is Not a Sentence',
          'I ask for your assessment of the inspection concerning [scope:mam_cen_subject.GetShortUIName]. State what the admitted facts can support, and where my conclusions run ahead of them. Your reply will accompany any memorial; it will not replace the emperor\'s judgment.', [
        opt('public_legal_check', 'Examine the lawful grounds without prejudging the charge.',
            filefx('mam_censor_public_check_effect = yes '+setv('consulted', 1)+setv('legal_reviewer', 'root')+move(6, 14)),
            'Check whether the emperor or the official\'s current liege presently holds a native imprisonment reason. Record your own review. This can support an administrative fitness recommendation while the grounds remain; it does not prove the alleged act or create a conviction, release or new criminal reason.',
            condition='scope:mam_cen_file = { has_variable = mam_cen_public_case }',
            ai='base = 140 '+trait('just', 80)+trait('diligent', 50)),
        opt('legal_check', 'Compare the original papers before I give my opinion.',
            filefx('mam_censor_independent_check_effect = yes '+setv('consulted', 1)+setv('legal_reviewer', 'root')+move(6, 14)),
            'Carry out an independent check using your own Learning, Stewardship, Intrigue and traits against the official\'s abilities. Current chance to uncover each actual concealed linkage or false return: [scope:mam_cen_justice_chance|0]%. No wrongdoing is generated when the record is honest.',
            ai='base = 60 '+trait('diligent', 50)+trait('just', 35)+' modifier = { add = 40 learning >= 15 }'),
        opt('legal_support', 'There is a supported matter for the throne to consider.',
            filefx(setv('legal', 1)+setv('consulted', 1)+setv('legal_reviewer', 'root')+move(6, 14)),
            'Support an administrative referral on the recorded facts. This adds no criminal secret, lawful arrest reason or sentence.', condition=SUPPORTED,
            ai='base = 65 '+trait('just', 50)+trait('honest', 30)),
        opt('legal_caution', 'Separate what is proved from what is merely suspected.',
            filefx(setv('legal', -1)+setv('consulted', 1)+setv('legal_reviewer', 'root')+move(6, 14)),
            'Record caution about the legal framing. The Censor can still impeach or remonstrate, but the emperor will see this disagreement.',
            ai='base = 40 '+trait('just', 35)+' modifier = { add = 100 '+UNSUPPORTED+' } modifier = { add = 70 '+ABUSE+' }'),
        opt('legal_protect', 'I will stand against proceedings against this official.',
            filefx(setv('legal', -2)+setv('consulted', 1)+setv('legal_reviewer', 'root')+move(6, 14))+
            'scope:mam_cen_subject = { add_opinion = { target = root modifier = mam_cen_defended_me } }',
            'The official gains 20 Opinion of you for 5 years. Your personal intervention is recorded; it cannot erase documents or prevent direct imperial reporting.',
            ai='base = 8 modifier = { add = 120 has_relation_friend = scope:mam_cen_subject } modifier = { add = 80 house ?= scope:mam_cen_subject.house }',
            stress='just = 15', stress_if=SUPPORTED),
    ], extra=facts, letter=True)

    event(6, 'What Shall the Court Hear?',
          'The inspection of [scope:mam_cen_office.GetName] is ready for my seal. The record does not speak for itself: I must decide what deserves correction, what merits public censure, and what should put an official\'s place before the emperor. My own conduct may now be part of that decision.', [
        opt('clear', 'Close the inspection of #bold [scope:mam_cen_subject.GetShortUIName]#! without a sanction.',
            'scope:mam_cen_subject = { add_opinion = { target = root modifier = mam_cen_fair_hearing } } '+filefx(close(1)),
            'Close with no sanction or payment. The official gains 15 Opinion of you for 3 years. Closing does not erase independently known secrets or actual historical acts.',
            ai='base = 10 modifier = { add = 100 '+UNSUPPORTED+' } '+trait('honest', 40)+trait('compassionate', 25),
            stress='just = 15 diligent = 10', stress_if=SUPPORTED),
        opt('correct', 'Accept a correction instead of breaking their career.',
            'scope:mam_cen_subject = { add_character_modifier = { modifier = mam_cen_reformed years = 1 } add_opinion = { target = root modifier = mam_cen_fair_hearing } } '+filefx(author()+close(2)),
            'Resolve the supported administrative fault without removing office or moving money. The official gains 15 Opinion of you for 3 years and Reconciled with Oversight for 1 year (-10% Stress gain).', condition=SUPPORTED+' scope:mam_cen_file = { NOT = { has_variable = mam_cen_native_fact } }',
            ai='base = 45 '+trait('compassionate', 80)+trait('forgiving', 60)),
        opt('censure', 'Censure #bold [scope:mam_cen_subject.GetShortUIName]#! publicly.',
            filefx(author()+'mam_censor_censure_effect = yes '+close(3)),
            'For a supported finding: the official loses 50 Influence and gains Publicly Censured for 2 years (-15% monthly Influence, -5 General Opinion), and loses 25 Opinion of you for 5 years. No title, appointment score or Treasury changes.', condition=SUPPORTED,
            ai='base = 50 '+trait('just', 40)+trait('wrathful', 35)+' modifier = { factor = 0.5 has_trait = craven scope:mam_cen_file.var:mam_cen_backing = -1 }'),
        opt('public_censure', 'Censure #bold [scope:mam_cen_subject.GetShortUIName]#!\'s continuance in office under these grounds.',
            filefx(author()+setv('public_censure', 1)+'mam_censor_censure_effect = yes '+close(3)),
            'On separately reviewed, still-current native legal grounds, impose the administrative censure detailed below. This is not proof of the original crime or a criminal sentence. No discovery reward is granted.',
            condition=PUBLIC_FITNESS+' '+UNSUPPORTED+' scope:mam_cen_subject = { NOT = { has_character_modifier = mam_cen_censured } }',
            ai='base = 55 '+trait('just', 35)+trait('wrathful', 35)),
        opt('impeach', 'Put #bold [scope:mam_cen_subject.GetShortUIName]#!\'s tenure before the emperor.',
            filefx(author()+move(7, 14)),
            'Submit the facts, defenses, advisory opinion and recorded methods directly to the emperor. Removal, protection, censure, further scrutiny and a rebuke to the investigator are possible. No punishment happens merely on submission.', condition=SUPPORTED,
            ai='base = 55 '+trait('ambitious', 60)+trait('diligent', 30)+' modifier = { add = 60 scope:mam_cen_file.var:mam_cen_proof = 1 } modifier = { factor = 0.5 has_trait = just scope:mam_cen_file.var:mam_cen_legal < 0 }'),
        opt('remonstrate', 'The appointment or policy deserves an answer, even without a charge.',
            filefx(author()+setv('remonstrance', 1)+move(7, 14)),
            'Submit a political objection, explicitly distinguished from a proved crime. The emperor can defend the official or act politically. This does not veto Personnel or Revenue.', condition=UNSUPPORTED,
            ai='base = 10 '+trait('ambitious', 45)+trait('vengeful', 55)),
        opt('misrepresent', 'Present my suspicion as an established charge.',
            filefx(author()+setv('fabricator', 'root')+setv('abuse', 1)+setv('abuser', 'root')+move(7, 14)),
            'Knowingly overstate an unsupported accusation. This records your misrepresentation, not the subject\'s guilt. An arbitrary emperor may still act politically; an adverse review can discredit or remove you.',
            condition=UNSUPPORTED+' NOT = { has_character_modifier = mam_cen_restrained }',
            ai='base = 2 '+trait('deceitful', 40)+trait('vengeful', 45)+trait('arbitrary', 25)+' modifier = { factor = 0 OR = { has_trait = honest has_trait = just } }',
            stress='honest = 30 just = 30 compassionate = 15'),
    ], extra=facts+' triggered_desc = { trigger = { exists = scope:mam_cen_abuser scope:mam_cen_abuser != root } desc = mam_cen.facts_inherited }')

    event(7, 'An Office Under Accusation',
          'The inspection of [scope:mam_cen_subject.GetShortUIName] has become a question for the throne. The Censor seeks an answer; the official and those who defend them expect one too. I may uphold a supported finding, protect a useful servant, require further scrutiny, or turn my attention to how the accusation was pursued.', [
        opt('public_imperial_check', 'Examine the current lawful grounds before deciding.',
            filefx('mam_censor_public_check_effect = yes '+move(7, 7)),
            'Check the current native imprisonment grounds once, without treating the accusation as a conviction. If verified grounds remain when you act, they can support an administrative censure or guarded removal. No prisoner is released and no crime is created.',
            condition='scope:mam_cen_file = { has_variable = mam_cen_public_case NOT = { has_variable = mam_cen_public_checked } }',
            ai='base = 160 '+trait('just', 90)+trait('diligent', 60)),
        opt('imperial_censure', 'Uphold the supported censure of #bold [scope:mam_cen_subject.GetShortUIName]#!.',
            filefx('mam_censor_censure_effect = yes '+close(4)),
            'The official loses 50 Influence, receives Publicly Censured for 2 years (-15% monthly Influence, -5 General Opinion), and loses 25 Opinion of the Censor for 5 years. No imprisonment, title transfer, money or candidate score change.', condition=SUPPORTED,
            ai='base = 70 '+trait('just', 50)+' modifier = { add = 50 scope:mam_cen_file.var:mam_cen_proof = 1 } modifier = { factor = 0.4 has_relation_friend = scope:mam_cen_subject }'),
        opt('public_imperial_censure', 'Uphold an administrative censure under the current lawful grounds.',
            filefx(setv('public_censure', 1)+'mam_censor_censure_effect = yes '+close(4)),
            'The separately reviewed native legal grounds remain current: impose the administrative censure detailed below. This does not convict the official of the original charge or create another criminal reason. There is no discovery reward.',
            condition=PUBLIC_FITNESS+' '+UNSUPPORTED+' scope:mam_cen_subject = { NOT = { has_character_modifier = mam_cen_censured } }',
            ai='base = 80 '+trait('just', 40)),
        opt('remove_official', 'Require #bold [scope:mam_cen_subject.GetShortUIName]#! to leave public office.',
            'save_scope_value_as = { name = mam_cen_removal_grounded value = 0 } '+
            'if = { limit = { OR = { '+SUPPORTED+' '+PUBLIC_FITNESS+' } } save_scope_value_as = { name = mam_cen_removal_grounded value = 1 } } '+
            'scope:mam_cen_subject = { mam_censor_retire_effect = { OFFICE = scope:mam_cen_file.var:mam_cen_office } } '+
            'if = { limit = { scope:mam_cen_file = { exists = var:mam_cen_retired var:mam_cen_retired = scope:mam_cen_subject } } if = { limit = { scope:mam_cen_removal_grounded = 0 } add_tyranny = 10 } '+filefx(close(5))+' } else = { '+filefx(setv('removal_blocked', 1)+move(7, 7))+' }',
            'On verified removal, impose a 3-year native appointment timeout. Supported senior governors enter Personnel custody with their jurisdiction; lower governors retire through the native engine; ministers yield through the native heir handoff. Failed removal gives no success or timeout. Without supported misconduct or separately reviewed current native legal grounds, you gain 10 Tyranny only after removal. Prisoners cannot use this guarded retirement path.',
            condition='scope:mam_cen_file = { NOT = { has_variable = mam_cen_removal_blocked } } scope:mam_cen_subject = { mam_censor_can_retire_trigger = { OFFICE = scope:mam_cen_file.var:mam_cen_office } }',
            ai='base = 10 modifier = { add = 85 scope:mam_cen_file.var:mam_cen_proof = 1 } modifier = { add = 100 scope:mam_cen_file = { has_variable = mam_cen_native_fact var:mam_cen_native_fact >= 4 } } modifier = { add = 50 '+PUBLIC_FITNESS+' } '+trait('arbitrary', 25)+' modifier = { factor = 0.02 '+UNJUSTIFIED+' NOT = { has_trait = arbitrary } } modifier = { factor = 0.1 has_relation_friend = scope:mam_cen_subject }'),
        opt('protect', 'I will retain #bold [scope:mam_cen_subject.GetShortUIName]#!.',
            'scope:mam_cen_subject = { add_character_modifier = { modifier = mam_cen_protected years = 3 } add_opinion = { target = root modifier = mam_cen_defended_me } } '+filefx('if = { limit = { has_variable = mam_cen_recused } '+close(6)+' } else = { '+move(9, 14)+' }'),
            'The official gains 20 Opinion of you for 5 years and 3 years of protection from random inspection selection. An unconflicted Censor can accept, renew the memorial once or offer resignation. If the Censor is the accused, your decision closes the review. Protection neither erases facts nor blocks a genuinely new discovery.',
            ai='base = 35 modifier = { add = 100 has_relation_friend = scope:mam_cen_subject } modifier = { add = 60 house ?= scope:mam_cen_subject.house } modifier = { add = 80 '+UNSUPPORTED+' } modifier = { add = 35 scope:mam_cen_file.var:mam_cen_backing = -1 } modifier = { add = 35 scope:mam_cen_file.var:mam_cen_legal < 0 } '+trait('forgiving', 30)),
        opt('rebuke', 'The investigator must answer for these methods.',
            '''scope:mam_cen_file.var:mam_cen_abuser ?= { if = { limit = { is_alive = yes }
              add_character_modifier = { modifier = mam_cen_discredited years = 3 }
              add_character_modifier = { modifier = mam_cen_restrained years = 2 } change_influence = -75
             } } '''+filefx(close(7)),
            'The recorded author of the threats, coercion or false charge loses 75 Influence, is Discredited for 3 years (-20% monthly Influence, -10 General Opinion), and is Restrained for 2 years (-10% monthly Influence; harsh/custom bargaining methods blocked). A successor does not inherit their guilt.',
            condition=ABUSE+' exists = scope:mam_cen_file.var:mam_cen_abuser scope:mam_cen_file.var:mam_cen_abuser = { is_alive = yes }',
            ai='base = 25 '+trait('just', 65)+trait('compassionate', 45)+' modifier = { add = 80 scope:mam_cen_file = { has_variable = mam_cen_fabricator } }'),
        opt('return', 'There is one point that still needs a proper answer.',
            filefx(setv('returned', 1)+move(4, 30)),
            'Return once for a further examination, advisory opinion or connected testimony. This does not declare either official guilty and cannot repeat indefinitely.',
            condition='scope:mam_cen_file = { var:mam_cen_returned = 0 NOT = { has_variable = mam_cen_recused } }', ai='base = 15 '+trait('patient', 35)),
    ], extra=facts+' triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_removal_blocked } } desc = mam_cen.facts_handoff }')

    event(8, 'The Name in the Margin',
          'Your name appears in the record connecting a private payment to an appointment handled by [scope:mam_cen_subject.GetShortUIName]. I require your account of that exchange. You are being heard as a connected participant; an accusation against another official is not proof against you.', [
        opt('confirm_link', 'I will confirm the exchange, and explain why I agreed.',
            filefx(setv('proof', 1)+setv('connected_heard', 1)+setv('testimony', 'root')+move(6, 14)),
            'Corroborate the actual recorded payment and appointment linkage. No new accusation or personal sanction is automatically created against you.',
            ai='base = 70 '+trait('honest', 90)+trait('craven', 35)),
        opt('deny_link', 'Deny the connection. Let them prove it without me.',
            filefx(setv('connected_heard', 1)+setv('denial', 'root')+'mam_censor_test_denial_effect = yes '+move(6, 14)),
            'Your Intrigue and Diplomacy oppose the inspector\'s Intrigue and Learning. If the linkage is not yet corroborated, there is a current [scope:mam_cen_witness_chance|0]% chance your denial is defeated by the existing record. Already admitted proof is never erased.',
            ai='base = 25 '+trait('deceitful', 75)+' modifier = { factor = 0.05 has_trait = honest }', stress='honest = 20 just = 10'),
        opt('link_protest', 'I will answer, but I will also report these threats.',
            filefx(setv('connected_heard', 1)+setv('safeguards', 1)+move(6, 14)),
            'Put a procedural complaint on record. It does not automatically disprove the payment or condemn the Censor. Recorded threats will accompany the final memorial.',
            ai='base = 15 modifier = { add = 100 '+ABUSE+' } '+trait('brave', 25)),
    ], letter=True)

    event(9, 'The Throne Has Answered',
          'The emperor will retain [scope:mam_cen_subject.GetShortUIName]. My memorial has not vanished, but neither has it prevailed. I must decide whether accepting this answer serves the empire, whether the court should hear my objection, or whether I can continue to hold my own seal.', [
        opt('accept_answer', 'The Dragon Throne has spoken. I will let the matter rest.', filefx(close(6)),
            'Close the dispute without further sanctions. Recorded facts and the emperor\'s protection remain; disagreement is not erased.',
            ai='base = 65 '+trait('content', 70)+trait('craven', 50)+trait('patient', 25)),
        opt('press', 'Let my objection be heard openly, once more.',
            filefx(author()+setv('pressed', 1)+move(10, 14)),
            'Renew the memorial publicly once. The emperor can yield, insist on the decision, mediate, or remove you through a valid native handoff. This is a political risk, not automatic victory.',
            ai='base = 20 '+trait('brave', 70)+trait('stubborn', 70)+' modifier = { add = 50 scope:mam_cen_file.var:mam_cen_proof = 1 }'),
        opt('resign_offer', 'If my seal carries no weight, I offer to return it.',
            filefx(author()+setv('resigner', 'root')+setv('pressed', 1)+move(10, 14)),
            'Offer resignation. The emperor may uphold a censure, accept through the safe native minister handoff, or settle the disagreement. Your office is not removed merely by sending the offer.',
            ai='base = 5 '+trait('just', 35)+trait('honest', 30)+trait('stubborn', 25)+' modifier = { factor = 0.1 '+UNSUPPORTED+' }'),
    ], extra=facts)

    event(10, 'Two Seals Before the Throne',
          '[scope:mam_cen_censor.GetShortUIName] has renewed the objection to retaining [scope:mam_cen_subject.GetShortUIName]. The dispute now concerns how this government can work together. Yielding may vindicate a necessary warning; standing firm may preserve a useful servant, or teach the court that protection matters more than an answer.', [
        opt('yield', 'Uphold the supported censure, and let the matter rest.',
            filefx('mam_censor_censure_effect = yes '+close(4)),
            'Apply the supported censure once: -50 Influence, 2 years of Publicly Censured (-15% monthly Influence, -5 General Opinion), and -25 Opinion of the Censor for 5 years. Retain the official\'s titles.', condition=SUPPORTED,
            ai='base = 45 '+trait('just', 35)+' modifier = { add = 70 scope:mam_cen_file.var:mam_cen_proof = 1 }'),
        opt('stand_firm', 'My decision stands. We will not reopen it again.',
            'scope:mam_cen_file.var:mam_cen_author ?= { if = { limit = { is_alive = yes } add_opinion = { target = root modifier = mam_cen_abandoned_me } } } '+filefx(close(6)),
            'End this dispute. The current Censor loses 15 Opinion of you for 3 years. No automatic punishment, office loss or realm-wide stability penalty follows disagreement.',
            ai='base = 50 '+trait('stubborn', 60)+' modifier = { add = 70 has_relation_friend = scope:mam_cen_subject }'),
        opt('remove_censor', 'Then return the seal of the Censorate.',
            'scope:mam_cen_censor = { mam_censor_retire_effect = { OFFICE = title:e_minister_censor } } if = { limit = { scope:mam_cen_file = { exists = var:mam_cen_retired var:mam_cen_retired = scope:mam_cen_censor } } '+filefx(close(9))+' } else = { '+filefx(setv('censor_removal_blocked', 1)+move(10, 7))+' }',
            'Remove the current Censor using the native heir handoff and a 3-year appointment timeout. This requires a safe, eligible successor and no mixed territorial holdings. The common fund and the investigated official\'s titles are untouched.',
            condition='scope:mam_cen_file = { exists = var:mam_cen_author var:mam_cen_author = scope:mam_cen_censor NOT = { has_variable = mam_cen_censor_removal_blocked } } scope:mam_cen_censor = { mam_censor_can_retire_trigger = { OFFICE = title:e_minister_censor } }',
            ai='base = 10 '+trait('arbitrary', 35)+' modifier = { add = 65 scope:mam_cen_file = { has_variable = mam_cen_resigner } } modifier = { add = 50 '+ABUSE+' }'),
        opt('mediate', 'Retain both offices, under a narrower understanding.',
            'mam_censor_mediation_effect = yes scope:mam_cen_file.var:mam_cen_author ?= { if = { limit = { is_alive = yes } add_character_modifier = { modifier = mam_cen_restrained years = 2 } } } '+filefx(close(12)),
            'Retain both officials. Restrict the responsible Censor\'s harsh/custom bargaining methods for 2 years (-10% monthly Influence). Your Diplomacy also determines whether the settlement restores goodwill or leaves resentment. Lawful scrutiny and native spying remain available.',
            ai='base = 30 '+trait('patient', 45)+trait('compassionate', 35)),
    ], extra=facts+' triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_censor_removal_blocked } } desc = mam_cen.facts_handoff }')

    event(11, 'The Price of Quiet',
          'A private accommodation has been suggested: an obligation to [scope:mam_cen_bargainer.GetShortUIName], and this custom report need not reach the court. The offer does not alter the papers. I can accept the debt, refuse it, or carry the demand to the emperor myself.', [
        opt('owe_favor', 'I will owe the favor. Let this report end here.',
            'scope:mam_cen_file.var:mam_cen_bargainer = { add_hook = { type = favor_hook target = root } } '+filefx(setv('compromised', 1)+close(11)),
            'The named bargainer receives one native Favor Hook on you in exchange for withholding this custom report. No Gold/Treasury moves and no native secret is concealed. The settlement is retained in the institutional record.',
            condition='exists = scope:mam_cen_file.var:mam_cen_bargainer scope:mam_cen_file.var:mam_cen_bargainer = { mam_censor_officer_trigger = yes NOT = { has_hook = root } }',
            ai='base = 25 '+trait('craven', 60)+trait('deceitful', 35)+' modifier = { factor = 0.05 has_trait = just }', stress='honest = 15 just = 15'),
        opt('refuse_favor', 'I will answer the inspection, not owe a private debt.',
            filefx(move(6, 14)),
            'Refuse. No hook or payment is created. The Censor must decide the report without this private agreement.', ai='base = 65 '+trait('just', 70)+trait('brave', 35)),
        opt('expose_demand', 'Put that demand before the emperor, with my name on it.',
            filefx(setv('abuse', 1)+setv('abuser', 'scope:mam_cen_file.var:mam_cen_bargainer')+author()+setv('reported_demand', 1)+move(7, 7)),
            'Report the actual demand against its author. The emperor reviews both the original matter and the investigator\'s conduct. No guilt is assigned to a successor.',
            ai='base = 25 '+trait('just', 70)+trait('brave', 55)),
    ], letter=True)

    # A live procedural dilemma produces new conduct, not retroactive random theft.
    themes = {
        'e_minister_of_personnel': 'The request concerns the reasons given for recommendations and the credentials behind them. A qualified relative is not automatically an unfit appointee; a certified false return is another matter.',
        'e_minister_of_revenue': 'The request concerns public accounts. Common funds, the imperial treasury and personal Gold must remain distinct. A legitimate payment is not a theft, and a missing explanation is not a missing sum.',
        'e_minister_of_works': 'The request concerns the administration of public works. Field reports and authorizations may arrive at different times; a project delay by itself establishes neither dishonesty nor diversion.',
        'e_minister_of_war': 'The request concerns military administration. A poor outcome is not a false return, and this demand gives the Censor no command over armies.',
        'e_minister_grand_marshal': 'The request concerns the account given of military service. The Marshal retains command; the truth of an official attestation remains open to scrutiny.',
        'e_minister_of_rites': 'The request concerns the performance of ceremonial and cultural duties. The Censor cannot rewrite examination honors or assume that appearing at an examination made this ministry its payer.',
        'e_minister_of_justice': 'The request concerns how official procedures have been described. It neither retries an existing criminal case nor transfers Justice\'s native powers to the Censor.',
        'e_minister_chancellor': 'The request reaches the government\'s own coordinating office. Defending a programme is legitimate; certifying an account known to be unchecked is a different choice.',
    }
    theme_desc = []
    for office, text in themes.items():
        key = loc('return_'+office, '\n\n'+text)
        theme_desc.append(f'triggered_desc = {{ trigger = {{ scope:mam_cen_subject = {{ has_title = title:{office} }} }} desc = {key} }}')
    event(12, 'The Signature They Require',
          'The papers requested for [scope:mam_cen_office.GetName] do not all arrive together. The Censor wants a signed return, while clerks warn that some details still need checking. I can admit the limits of the record, take time to verify it, or certify more than I can honestly establish.', [
        opt('return_check', 'Ask for time, and verify every assertion before signing.',
            filefx(setv('checked_reply', 1)+move(3, 28)),
            'Take four weeks to verify the response. No misconduct is created. A slower answer is not obstruction, although political opponents may still complain.',
            ai='base = 70 '+trait('diligent', 80)+trait('honest', 60)+trait('patient', 40)),
        opt('return_limits', 'State plainly what these papers cannot establish.',
            filefx(setv('limited_reply', 1)+move(3, 14)),
            'Submit a limited but honest return. The uncertainty remains visible and cannot become a supported charge by itself.',
            ai='base = 55 '+trait('honest', 60)+trait('humble', 30)),
        opt('return_false', 'Certify it all. My seal will have to stand for the missing checks.',
            filefx(setv('false_return', 1)+setv('false_return_date', 'current_date')+setv('return_writer', 'root')+move(3, 14)),
            'Knowingly sign beyond the checked record. This creates a new false official attestation, not a theft or a past crime. A proper comparison by the Censor may uncover it; it is not automatically known or proved.',
            ai='base = 8 '+trait('deceitful', 70)+trait('lazy', 40)+trait('arrogant', 25)+' modifier = { factor = 0 OR = { has_trait = honest has_trait = just } }',
            stress='honest = 25 just = 20'),
    ], letter=True, extra=' '.join(theme_desc))

    # Results are immutable archival correspondence, not a live commitment menu.
    results = {
        1: ('The Inspection Closed', 'The inspection of [scope:mam_cen_office.GetName] has closed without a sanction. This is a disposition of the present record, not a claim that every decision was wise or that known secrets have ceased to exist.'),
        2: ('A Correction, Not a Ruined Career', 'The fault recorded in the inspection has been settled through an administrative correction. [scope:mam_cen_subject.GetShortUIName] remains in office. No public money was seized and no appointment was reversed.'),
        3: ('The Censor\'s Reprimand', '[scope:mam_cen_subject.GetShortUIName] has been publicly censured on a supported finding. The loss of Influence and standing is real, but the inspection has not transferred a title or created a criminal sentence.'),
        4: ('A Memorial Upheld', 'The throne has upheld a supported censure of [scope:mam_cen_subject.GetShortUIName]. The official retains the office under a public reprimand. The inquiry and the responses of those who intervened remain on record.'),
        5: ('A Seal Returned', 'The emperor has required [scope:mam_cen_subject.GetShortUIName] to leave public office through the native retirement procedure. The official receives a three-year appointment timeout. The Censor has not selected a replacement.'),
        6: ('Protected by the Throne', 'The emperor retains [scope:mam_cen_subject.GetShortUIName]. The political dispute has ended for now. Protection does not erase the inspection\'s record or turn disagreement into a criminal judgment.'),
        7: ('The Investigator Rebuked', 'The recorded author of abusive methods has been discredited and restrained. The sanction belongs to that person, not whoever happens to hold the Censorate now. The original accusation has not thereby become a proved crime.'),
        9: ('The Censor Returns the Seal', 'The emperor has ended this confrontation by removing the current Censor through the native ministry handoff. The investigated official remains in place. The office\'s institutional record survives its holder.'),
        10: ('An Inspection Overtaken', 'Death, departure, unavailable authority or the outer time limit has ended the inspection of [scope:mam_cen_office.GetName] without a new sanction. Uncertainty has not been converted into guilt or a payment.'),
        11: ('A Report Kept Quiet', 'This custom report will not be put before the court. Any agreed private obligation and the disposition remain in the institutional record. No known native secret or public payment record has been erased.'),
        12: ('An Uneasy Accommodation', 'Both officials remain. The Censor\'s harsh methods are restrained for two years, while lawful scrutiny and native intelligence work continue. The settlement ends the confrontation without pretending that everyone agreed.'),
        13: ('The Handoff Could Not Be Confirmed', 'The intended removal did not satisfy its handoff checks. No successful retirement or new appointment timeout is claimed. Check the current office and Personnel custody before attempting another removal; no substitute title grant or payment was made.'),
        14: ('An Inspection Declined', 'The Censor has declined to pursue the proposed inspection of [scope:mam_cen_office.GetName]. No examination or clearance is claimed, and no penalty follows simply from having been selected.'),
    }
    body = []; titles = []
    for n, (title, prose) in results.items():
        loc(f'result_{n}_title', title)
        loc(f'result_{n}_desc', prose)
        body.append(f'triggered_desc = {{ trigger = {{ scope:mam_cen_file.var:mam_cen_result = {n} }} desc = mam_cen.result_{n}_desc }}')
        titles.append(f'triggered_desc = {{ trigger = {{ scope:mam_cen_file.var:mam_cen_result = {n} }} desc = mam_cen.result_{n}_title }}')
    loc('result_title', 'Concerning an Inspection')
    loc('result_unavailable', 'The disposition cannot be read from these papers. No new action is taken.')
    loc('result_private_public', 'The Censorate has closed the inspection of [scope:mam_cen_office.GetName] without proposing a sanction. This notice establishes no clearance or conviction.')
    loc('result_public_censure', '[scope:mam_cen_subject.GetShortUIName] has received an administrative censure for continuing in office under separately reviewed native legal grounds. Influence and standing are reduced. This disposition neither proves the original criminal accusation nor creates another criminal reason, imprisonment or release.')
    loc('received', 'I have received the account.')
    outsider = 'root != scope:mam_cen_censor root != scope:mam_cen_subject scope:mam_cen_file.var:mam_cen_result = 11'
    redact = 'triggered_desc = { trigger = { '+outsider+' } desc = mam_cen.result_private_public }'
    redacted_title = 'triggered_desc = { trigger = { '+outsider+' } desc = mam_cen.result_1_title }'
    EVENTS.append('''mam_censor.90 = { type = letter_event sender = scope:mam_cen_result_sender title = { first_valid = { '''+redacted_title+' '+' '.join(titles)+''' desc = mam_cen.result_title } }
     opening = { desc = mam_cen.opening }
     desc = { first_valid = { '''+redact+''' triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_public_censure } } desc = mam_cen.result_public_censure } '''+' '.join(body)+''' desc = mam_cen.result_unavailable } }
     option = { name = mam_cen.received ai_chance = { base = 100 } }
    }''')


def generate(root):
    root = Path(root).resolve()
    parent = Path(os.environ.get('MAM_BUILD_STAGING_DIR', __import__('tempfile').gettempdir())).resolve()
    if not (root.parent.name.startswith('mam-cf-build-') and root.parent.parent == parent):
        raise RuntimeError('Censor generation is restricted to the isolated full builder stage.')
    LOC.clear(); EVENTS.clear()
    def write(rel, text):
        p = root/rel; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text.strip()+'\n', encoding='utf-8-sig' if p.suffix in {'.txt', '.yml'} else 'utf-8')
    templates = root/'tools/templates/censor'
    for name, output in [('triggers','common/scripted_triggers/mam_censor_triggers.txt'),
                         ('effects','common/scripted_effects/mam_censor_effects.txt')]:
        write(output, (templates/f'{name}.txt').read_text(encoding='utf-8'))
    for block in (templates/'support.txt').read_text(encoding='utf-8').split('@@ ')[1:]:
        rel, text = block.split('\n', 1); write(rel.strip(), text)
    for template in ('intelligence.txt', 'public_crime.txt'):
        for block in (templates/template).read_text(encoding='utf-8').split('@@ ')[1:]:
            rel, text = block.split('\n', 1)
            rel = rel.strip()
            write(rel, (root/rel).read_text(encoding='utf-8-sig')+'\n'+text)
    make_events()
    for stage in (4,6):
        referral=opt('refer_justice_'+str(stage),'Refer the matter concerning #bold [scope:mam_cen_subject.GetShortUIName]#! to Justice.',
          'mam_justice_from_censor_effect = yes '+filefx('if = { limit = { has_variable = mam_cen_justice_referred } '+move(stage,7)+' }'),
          'Create an independent judicial proceeding without declaring guilt or closing this administrative inspection. Justice hears the accused and must respect native grounds, judicial authority and actual custody. Existing Personnel succession remains separate.',
          condition='scope:mam_cen_subject = { mam_justice_senior_trigger = yes NOT = { exists = var:mam_jus_case } } scope:mam_cen_file = { NOT = { has_variable = mam_cen_justice_referred } } NOT = { title:h_china = { any_in_list = { variable = mam_jus_queue count >= 8 always = yes } } }',
          ai='base = 35 modifier = { add = 60 '+SUPPORTED+' } modifier = { add = 40 has_trait = just }')
        for i,s in enumerate(EVENTS):
            if s.startswith(f'mam_censor.{stage} ='):
                EVENTS[i]=s.replace('option = { name = mam_cen.stale',referral+' option = { name = mam_cen.stale',1)
    from build_censor_intelligence import author as intelligence_events
    intelligence_facts = intelligence_events(loc, EVENTS)
    # Shared facts must describe a real native discovery before the generic
    # lack-of-payment paragraph; no secret is relabelled as a paid appointment.
    EVENTS[:] = [s.replace('first_valid = {\n      triggered_desc',
                           'first_valid = {\n      '+intelligence_facts+'\n      triggered_desc')
                 if 'scope:mam_cen_file.var:mam_cen_proof = 1' in s else s for s in EVENTS]
    # Opening/answering the inspection also names the actual allegation.
    for i, s in enumerate(EVENTS):
        for n in (1, 2):
            if s.startswith(f'mam_censor.{n} ='):
                prefix = f'desc = {{ desc = mam_cen.{n}_desc'
                EVENTS[i] = s.replace(prefix, prefix+' first_valid = { '+intelligence_facts+' }', 1)
        if s.startswith(('mam_censor.1 =', 'mam_censor.2 =')):
            EVENTS[i] = EVENTS[i].replace('desc = { ', 'desc = { triggered_desc = { trigger = { scope:mam_cen_file = { has_variable = mam_cen_public_case } } desc = mam_cen.facts_public } ', 1)
    # One shared contextual preview for all censure choices; it shows rivalry
    # only for eligible traits/relations and trust only for an untainted finding.
    for i in range(len(EVENTS)):
        for key in ('censure', 'imperial_censure', 'yield'):
            EVENTS[i] = EVENTS[i].replace('custom_tooltip = mam_cen.'+key+'_tt', 'mam_censor_censure_tooltip_effect = yes')
        for key in ('public_censure','public_imperial_censure'):
            EVENTS[i] = EVENTS[i].replace('custom_tooltip = mam_cen.'+key+'_tt',
                'custom_tooltip = mam_cen.'+key+'_tt mam_censor_censure_tooltip_effect = yes')
    for key, value in {
        'mam_censor_inspect_interaction': 'Censor: Inspect Public Conduct',
        'mam_censor_inspect_interaction_desc': 'Open an inspection of this official. The current Censor chooses the approach; the subject and other officials can answer, resist or intervene. An inspection is not a declaration of guilt.',
        'mam_censor_petition_interaction': 'Censor: Demand Safeguards',
        'mam_censor_petition_interaction_desc': 'Intervene in the active inspection. Ask for fair limits, defend an official or support scrutiny. One additional petition may interrupt an inspection before an imperial memorial is submitted.',
        'mam_censor_begin_decision': 'Censor: Begin an Inspection',
        'mam_censor_begin_decision_desc': 'Choose a senior official for scrutiny. County and duchy officials can be selected through the Ministry interaction on their character.',
        'mam_censor_intelligence_decision': 'Censor: Review Confidential Discoveries',
        'mam_censor_refer_crime_interaction': 'Censor: Refer a Criminal Accusation',
        'mam_censor_refer_crime_interaction_desc': 'Refer an actual native legal reason against this senior official to the Censorate. The official may answer, and the Censor may seek Justice\'s advice or report to the throne. This files an accusation, not a conviction; no new crime, arrest, release or payment occurs.',
        'mam_cen.public_no_duplicate': 'This continuing criminal matter has not already been referred. A pending, completed or declined referral is not repeated while the same grounds or custody continue.',
        'mam_cen.public_queue_room': 'The Censorate has room for another referral in its eight-entry queue.',
        'mam_censor_intelligence_decision_desc': 'Review relevant known official secrets and imperial plot warnings. Only one referral or inspection is presented at a time. The emperor reviews an independently known allegation against the Censor. Discoveries normally arrive within seven days.',
        'mam_cen.intel_confirm': 'Bring the confidential papers.',
        'mam_cen_guarded': 'Under the Censorate\'s Protection',
        'mam_cen_guarded_desc': 'Closer protection makes hostile scheme phases against this character take 5 additional days. It is not immunity from plots.',
        'mam_censor_resume_decision': 'Censor: Resume My Pending Business',
        'mam_censor_resume_decision_desc': 'Recall the current stage addressed to you. This does not repeat a decision already made or transfer another official\'s authority.',
        'mam_cen.begin_confirm': 'Consider whom to inspect',
        'mam_cen.resume_confirm': 'Bring the papers',
        'mam_cen.only_one_tt': 'The Censorate can pursue one major inspection at a time.',
        'mam_cen.current_censor_tt': 'The living Censor must hold both the ministry and its council seat.',
        'mam_cen.cooldown_tt': 'This official has not been selected for an inspection in the past two years.',
        'mam_cen.retired_reason': 'Removed from public office after a censorial confrontation',
        'mam_cen_feared': 'Feared Censor', 'mam_cen_feared_desc': 'This inspector has made threats part of government. Officials may submit, but resentment and appeals can follow.',
        'mam_cen_trusted': 'Trusted Inspector', 'mam_cen_trusted_desc': 'This official has earned confidence through a supported and measured disposition.',
        'mam_cen_censured': 'Publicly Censured', 'mam_cen_censured_desc': 'A supported finding has damaged this official\'s political standing without transferring their office.',
        'mam_cen_restrained': 'Censorial Methods Restrained', 'mam_cen_restrained_desc': 'Imperial limits prohibit new threats, coerced confessions and private demands in the custom inspection system. Lawful scrutiny and native spying continue.',
        'mam_cen_protected': 'Protected by the Throne', 'mam_cen_protected_desc': 'The emperor has retained this official. Automatic inspections pass over them for three years; records are not erased.',
        'mam_cen_reformed': 'Reconciled with Oversight', 'mam_cen_reformed_desc': 'An administrative fault was resolved without destroying the official\'s career.',
        'mam_cen_discredited': 'Discredited Investigator', 'mam_cen_discredited_desc': 'The investigator\'s own methods have become the subject of an adverse imperial finding.',
        'mam_cen_resentment': 'Resented Censorial Pressure', 'mam_cen_fair_hearing': 'Granted a Fair Hearing',
        'mam_cen_defended_me': 'Defended My Position', 'mam_cen_abandoned_me': 'Rejected My Memorial',
        'mam_cen_exposed_abuse': 'Exposed My Abuse',
        'mam_cen_skillful_mediation': 'Settled Our Dispute Skillfully',
        'mam_cen_rival_reason': 'Their confrontation over a public inspection hardened into a lasting rivalry.',
        'mam_cen.censure_consequences': 'Once on a supported finding: -50 Influence; Publicly Censured for 2 years (-15% monthly Influence, -5 General Opinion). No money, title, imprisonment reason or candidate score changes.',
        'mam_cen.censure_resentment': 'The official loses 25 Opinion of the living Censor for 5 years.',
        'mam_cen.censure_rival': 'Because of the official\'s temperament, this confrontation creates a native Rivalry with the Censor.',
        'mam_cen.trust_consequences': 'The actual deciding/reporting Censor gains Trusted Inspector for 3 years (+10% monthly Influence, +5 General Opinion) if alive; the modifier does not stack.',
        'mam_cen.mediation_skilled_tt': 'Your Diplomacy is at least 15: the official and the living memorial author each gain 10 Opinion of you for 3 years.',
        'mam_cen.mediation_unskilled_tt': 'Your Diplomacy is below 8: the living memorial author loses 15 Opinion of you for 3 years.',
    }.items():
        assert key not in LOC; LOC[key] = value
    # Three stable, clickable choices; explicit interaction remains the full target selector.
    agenda = []
    loc('agenda_title', 'Where Shall I Look?')
    loc('agenda_desc', 'An inspection can reach a powerful ministry or a provincial administration. These are candidates for scrutiny, not a list of guilty officials. I may also inspect an eligible official directly through their Ministry interaction.')
    for i in range(1, 4):
        key = loc(f'agenda_{i}', f'Inspect #bold [scope:mam_cen_pick_{i}.GetShortUIName]#! in [scope:mam_cen_pick_{i}.GetPrimaryTitle.GetName].')
        agenda.append(f'''option = {{ name = {key} trigger = {{ mam_censor_officer_trigger = yes exists = scope:mam_cen_pick_{i} }}
          if = {{ limit = {{ mam_censor_officer_trigger = yes title:h_china = {{ NOT = {{ exists = var:mam_cen_active }} }}
           scope:mam_cen_pick_{i} = {{ mam_censor_subject_trigger = {{ EMPEROR = title:h_china.holder CENSOR = root }} NOT = {{ has_character_flag = mam_cen_recent_inspection }} }} }}
           hidden_effect = {{ scope:mam_cen_pick_{i} = {{ save_scope_as = mam_cen_subject }} save_scope_as = mam_cen_originator mam_censor_start_effect = yes }}
          }} ai_chance = {{ base = 0 }} }}''')
    loc('agenda_cancel', 'I will choose another official myself.')
    EVENTS.append('mam_censor.100 = { type = character_event theme = intrigue title = mam_cen.agenda_title desc = mam_cen.agenda_desc '+
                  ' '.join(agenda)+' option = { name = mam_cen.agenda_cancel ai_chance = { base = 100 } } }')
    write('events/mam_censor_events.txt', 'namespace = mam_censor\n\n'+'\n\n'.join(EVENTS))
    # CK3 DATA expressions use [name.GetName], not script-side [scope:name...].
    LOC.update({k: re.sub(r'\[scope:(mam_cen_\w+)', r'[\1', v) for k,v in LOC.items()})
    write('localization/english/mam_censor_l_english.yml', 'l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v, ensure_ascii=False) for k,v in LOC.items()))
    d = root/'descriptor.mod'
    d.write_text(re.sub(r'version="[^"]+"', 'version="0.4.0-alpha.20-dev.65"', d.read_text(encoding='utf-8'), count=1), encoding='utf-8')
    print(f'Censorate generated: {len(EVENTS)} events; {len(LOC)} localization keys. No native overrides.')


if __name__ == '__main__':
    import subprocess, sys
    raise SystemExit(subprocess.call([sys.executable, str(ROOT/'tools/build_common_fund.py')]))
