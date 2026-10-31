"""Natural-language Justice hearings and explicit authority/receipt presentation."""


def author(loc,event,opt,fx,move,close,events,labels):
    events.append('''mam_justice.11 = { type = character_event hidden = yes
     trigger = { exists = scope:mam_jus_case scope:mam_jus_case = { mam_justice_live_trigger = yes
      var:mam_jus_stage = 11 var:mam_jus_serial = scope:mam_jus_token } }
     immediate = { scope:mam_jus_case = {
      remove_variable = mam_jus_worker_until
      mam_justice_native_bind_effect = yes
      if = { limit = { exists = scope:mam_jus_performer scope:mam_jus_performer = root
       var:mam_jus_serial = scope:mam_jus_token var:mam_jus_stage = 11 mam_justice_live_trigger = yes }
       mam_justice_commit_effect = yes
      }
     } }
    }''')
    loc('opening','Concerning a matter of justice,')
    loc('stale','These papers have been overtaken by events.')
    loc('custody_fact','\n\n[scope:mam_jus_subject.GetShortUIName] is in custody. Detention is recorded separately from guilt; this hearing alone grants no release.')
    loc('referral_fact','\n\nThe Censorate\'s inspection accompanies the papers. Its observations, objections and any supported findings remain distinct from a judicial disposition.')
    loc('private_fact','\n\nA private approach is recorded between its actual participants. A later minister cannot inherit another person\'s promised payment or favor.')
    loc('mitigation_fact','\n\nThe official has presented a persuasive case for consideration. That may weigh in favor of mercy; it does not erase the grounds or establish innocence.')
    loc('evidence_judicial','\n\nThe Censorate has corroborated a recorded judicial demand or unauthorized measure attributable to [scope:mam_jus_subject.GetShortUIName]. The exercise of public authority is itself in question.')
    loc('evidence_certification','\n\nThe checked returns identify a knowingly false official certification made under [scope:mam_jus_subject.GetShortUIName]\'s seal. The limits of the original inquiry were not honestly stated.')
    loc('evidence_appointment','\n\nThe Censorate\'s papers link an actual payment to an appointment made under [scope:mam_jus_subject.GetShortUIName]\'s authority. This is more than a complaint about favoring a friend.')
    for i,text in {1:'[scope:mam_jus_performer.GetShortUIName] would take the official into custody.',
                   2:'[scope:mam_jus_performer.GetShortUIName] would pardon [scope:mam_jus_pardon_authority.GetShortUIName]\'s current criminal rights together; other authorities may retain theirs. This does not release a prisoner.',
                   3:'[scope:mam_jus_performer.GetShortUIName] would release the prisoner without a separate pardon.',
                   4:'[scope:mam_jus_performer.GetShortUIName] would carry out the proposed execution under existing native grounds.',
                   5:'[scope:mam_jus_performer.GetShortUIName] would carry out native banishment, if the prisoner accepts its terms.',
                   6:'Only the separate imperial warrant would be withdrawn. Other criminal rights and existing custody would remain.',
                   7:'A three-year imperial warrant would establish an imprisonment reason for documented abuse of office. It grants no execution, banishment or revocation right.'}.items():
        loc('proposal_'+str(i),'\n\n'+text)
    loc('conditional_effects','If the proposed native action is eventually executed, its native consequences apply. Approval alone moves no money and does not arrest, release, pardon or kill anyone.')
    common_cost='Actual native costs for the currently proposed performer: [scope:mam_jus_cost_treasury|0] @treasury_icon!, [scope:mam_jus_cost_gold|0] @gold_icon!, [scope:mam_jus_cost_influence|0] Influence, [scope:mam_jus_cost_prestige|0] Prestige and [scope:mam_jus_cost_piety|0] Piety. Costs and permissions are checked again before execution. '
    event(1,'A Matter for the Ministry of Justice',
          'The conduct and circumstances of #bold [scope:mam_jus_subject.GetShortUIName]#! require a decision. I must distinguish an accusation from an established act, and a lawful ground for proceeding from the punishment someone wishes to impose.',[
        opt('hear','Let #bold [scope:mam_jus_subject.GetShortUIName]#! answer.',fx(move(2)),
            'Send a hearing letter. The accused may answer from custody. No guilt, criminal reason or punishment is created.',ai='base = 130 modifier = { add = 80 has_trait = just } modifier = { add = 60 has_trait = diligent }'),
        opt('request_censor','Ask the Censor to examine what these papers do not establish.',fx('mam_justice_request_censor_effect = yes'),
            'Request one independent inspection if the Censor can take the subject. A busy desk is retried quietly for at most 60 days. The Censor can decline; the request neither proves guilt nor forces a finding.',
            condition='scope:mam_jus_case = { NOT = { has_variable = mam_jus_requested_censor } } scope:mam_jus_subject = { mam_censor_subject_trigger = { EMPEROR = title:h_china.holder CENSOR = title:e_minister_censor.holder } }',
            ai='base = 30 modifier = { add = 40 has_trait = patient }'),
        opt('decline','These papers do not require criminal proceedings.',fx(close(1)),
            'Decline this custom proceeding without a conviction, pardon, release or erasure of known facts. Native legal rights remain. This does not reverse the Censor\'s administrative work.',
            ai='base = 15 modifier = { add = 90 scope:mam_jus_subject = { mam_justice_native_ground_trigger = no is_imprisoned = no } } modifier = { add = 40 has_trait = lazy }'),
    ])
    event(2,'An Answer to the Ministry',
          'I ask for your answer concerning these accusations and your treatment. State what you dispute, what should be examined, and whether you ask the government for clemency. This demand for an answer is not a finding of guilt.',[
        opt('answer','I will answer the charge and provide what I know.',fx('set_variable = { name = mam_jus_answer value = 1 } mam_justice_hearing_effect = yes '+move(3)),
            'Cooperate without admitting an unproved offense. Your Diplomacy and Learning affect how persuasively you present mitigation. Justice\'s Learning, and Intrigue against a deceitful defense, affect its assessment. This affects discretionary mercy, never proof or legal rights.',ai='base = 100 modifier = { add = 70 has_trait = honest }'),
        opt('contest','Show me the lawful grounds for proceeding.',fx('set_variable = { name = mam_jus_contested value = 1 } mam_justice_hearing_effect = yes '+move(3)),
            'Dispute the grounds or handling. A lawful objection is not obstruction and creates no new offense. Skills affect the presentation of mitigation, not the existence of a criminal reason.',ai='base = 60 modifier = { add = 60 has_trait = just } modifier = { add = 50 has_trait = brave }'),
        opt('mercy','I ask for mercy, whatever the court decides.',fx('set_variable = { name = mam_jus_plea value = 1 } mam_justice_hearing_effect = yes '+move(3)),
            'Ask for clemency without creating proof of guilt. Mercy, native pardon and release remain different decisions.',ai='base = 30 modifier = { add = 100 has_trait = craven }'),
        opt('surrender','If lawful custody is required, I will submit to it.',fx('set_variable = { name = mam_jus_surrender value = scope:mam_jus_arrest_performer } if = { limit = { has_variable = mam_jus_failed_action var:mam_jus_failed_action = 1 } remove_variable = mam_jus_failed_action } '+move(3)),
            'Consent to custody by the currently named judge if native permissions permit it. A different officeholder cannot inherit this personal consent. This does not admit guilt.',
            condition='is_imprisoned = no scope:mam_jus_subject = { mam_justice_native_ground_trigger = yes }',
            ai='base = 35 modifier = { add = 80 has_trait = craven } modifier = { add = 35 has_trait = honest }'),
    ],letter=True)
    event(3,'An Official Takes an Interest',
          'The proceeding against #bold [scope:mam_jus_subject.GetShortUIName]#! has consequences beyond one household. I may defend the official, support lawful scrutiny, or insist that Justice state its reasons.',[
        opt('support','Justice should pursue what the actual grounds support.',fx('set_variable = { name = mam_jus_advocacy value = 1 } '+move(4)),
            'Record support, not a verdict. No new criminal right or penalty follows.',ai='base = 70 modifier = { add = 70 has_trait = just }'),
        opt('defend','This official deserves a fair hearing and consideration for mercy.',
            'scope:mam_jus_subject = { add_opinion = { target = root modifier = mam_jus_advocated } } '+fx('set_variable = { name = mam_jus_advocacy value = -1 } '+move(4)),
            'The official gains 20 Opinion of you for 3 years. Your intervention influences the minister\'s choices but does not erase evidence or bind the emperor.',
            ai='base = 35 modifier = { add = 120 has_relation_friend = scope:mam_jus_subject } modifier = { add = 70 is_close_or_extended_family_of = scope:mam_jus_subject } modifier = { add = 50 has_trait = compassionate }'),
        opt('scrutiny','Put the handling of this matter before the throne.',fx('set_variable = { name = mam_jus_action value = 0 } '+move(5)),
            'Seek procedural imperial review. It does not authorize an arrest or punishment and does not declare either party guilty.',ai='base = 15 modifier = { add = 50 has_trait = paranoid }'),
    ])
    choices=[]
    names={1:'Seek lawful custody of #bold [scope:mam_jus_subject.GetShortUIName]#!.',
           2:'Propose a pardon for #bold [scope:mam_jus_subject.GetShortUIName]#!.',
           3:'Propose the release of #bold [scope:mam_jus_subject.GetShortUIName]#!.',
           4:'Put a capital recommendation before the emperor.',
           5:'Recommend native banishment under the existing grounds.',
           6:'Ask to withdraw the separate imperial warrant.',
           7:'Ask the emperor for a warrant for documented abuse of public office.'}
    tips={
        1:'Propose custody using existing grounds and native permissions. The Justice minister\'s native privilege is retained; central ministers and protected imperial family use the emperor as enforcer, requiring native automatic acceptance or genuine surrender. Current arrest costs: [scope:mam_jus_arrest_cost|0] @treasury_icon! and [scope:mam_jus_arrest_prestige|0] Prestige. Arrest does not convict the accused. ',
        2:'[scope:mam_jus_pardon_performer.GetShortUIName] would grant this pardon, clearing [scope:mam_jus_pardon_authority.GetShortUIName]\'s current imprisonment, execution, banishment and revocation reasons together. Other authorities may retain their own rights. This does not itself release a prisoner. Current costs for that performer: [scope:mam_jus_pardon_cost|0] @treasury_icon! and [scope:mam_jus_pardon_influence|0] Influence. ',
        3:'Release requires the actual custodian\'s consent when someone else holds the prisoner. Ordinary release does not clear unrelated criminal rights. ',
        4:'Capital punishment always requires the current emperor\'s seal, the actual custodian\'s consent and a current native execution reason. A custom corruption warrant grants no execution reason. ',
        5:'Banishment always requires imperial approval, actual custody, native banishment permissions and the prisoner\'s agreement to these terms. Native forfeiture/title consequences, where applicable, remain native. ',
        6:'Withdraw only this mod\'s identifiable warrant opinion from its current imperial issuer. Unrelated native reasons are preserved. This does not release a prisoner or erase the finding. ',
        7:'The emperor must explicitly review actual, corroborated appointment-for-payment, detected knowingly false official certification, or documented judicial solicitation/abuse. Mere accusations, kinship and legitimate spending do not qualify. A warrant grants only a three-year native imprisonment reason; never an execution, banishment or title-revocation right. ',
    }
    ai={1:'base = 70 modifier = { add = 45 has_trait = diligent } modifier = { add = 60 has_trait = vengeful has_relation_rival = scope:mam_jus_subject }',
        2:'base = 35 modifier = { add = 65 has_trait = forgiving } modifier = { add = 80 has_relation_friend = scope:mam_jus_subject } modifier = { add = 60 is_close_or_extended_family_of = scope:mam_jus_subject } modifier = { add = 50 has_trait = compassionate }',
        3:'base = 65 modifier = { add = 80 has_trait = compassionate } modifier = { add = 60 has_trait = forgiving } modifier = { add = 80 scope:mam_jus_subject = { mam_justice_native_ground_trigger = no } }',
        4:'base = 5 modifier = { add = 70 has_trait = sadistic } modifier = { add = 70 has_trait = vengeful has_relation_rival = scope:mam_jus_subject } modifier = { factor = 0.05 has_trait = compassionate }',
        5:'base = 10 modifier = { add = 50 has_trait = callous } modifier = { add = 40 has_trait = wrathful }',
        6:'base = 25 modifier = { add = 70 has_trait = forgiving } modifier = { add = 80 has_relation_friend = scope:mam_jus_subject }',
        7:'base = 100 modifier = { add = 80 has_trait = just } modifier = { add = 60 has_trait = diligent }'}
    for action in range(1,8):
        condition=f'mam_justice_action_{action}_available = yes scope:mam_jus_case = {{ trigger_if = {{ limit = {{ has_variable = mam_jus_failed_action }} var:mam_jus_failed_action != {action} }} }}'
        weight=ai[action]
        if action in (2,3,6):
            weight+=' modifier = { add = 50 scope:mam_jus_case = { has_variable = mam_jus_mitigation } } modifier = { add = 30 scope:mam_jus_case = { has_variable = mam_jus_plea } } modifier = { add = 40 scope:mam_jus_case.var:mam_jus_advocacy = -1 } modifier = { add = 30 exists = scope:mam_jus_advocate scope:mam_jus_advocate = { diplomacy >= 15 } scope:mam_jus_case.var:mam_jus_advocacy = -1 }'
        if action in (1,7):
            weight+=' modifier = { add = 35 learning >= 15 } modifier = { add = 35 scope:mam_jus_case.var:mam_jus_advocacy = 1 }'
        choices.append(opt('action_'+str(action),names[action],fx('remove_variable = mam_jus_shadow '+f'mam_justice_propose_effect = {{ ACTION = {action} }}'),tips[action]+'Approval, consent, costs and current permissions are rechecked before execution.',condition,weight))
    choices.extend([
        opt('seek_surrender','Ask #bold [scope:mam_jus_subject.GetShortUIName]#! to submit to lawful custody.',fx('set_variable = { name = mam_jus_surrender_requested value = scope:mam_jus_arrest_performer } '+move(2)),
            'Ask for genuine consent to the currently named enforcer. This is useful when a new warrant or a changed enforcer makes the earlier answer insufficient. Refusal does not create another crime.',
            condition='scope:mam_jus_subject = { is_imprisoned = no mam_justice_native_ground_trigger = yes } scope:mam_jus_case = { OR = { NOT = { exists = var:mam_jus_surrender_requested } var:mam_jus_surrender_requested != scope:mam_jus_arrest_performer } }',
            ai='base = 45 modifier = { add = 40 learning >= 15 }'),
        opt('gold_offer','A private payment might secure a favorable decision.',fx('mam_justice_offer_effect = { KIND = 1 }'),
            'Offer a conditional private bargain for 100 personal Gold. The accused may refuse or report it. No money moves now. Payment occurs only once after an agreed, actually executed pardon or release. Soliciting this exchange is a documented abuse of office.',
            condition='mam_justice_officer_trigger = yes NOT = { has_character_modifier = mam_jus_restrained } scope:mam_jus_case = { NOT = { has_variable = mam_jus_offer_author } } OR = { AND = { mam_justice_action_2_available = yes scope:mam_jus_pardon_performer = root } scope:mam_jus_subject = { is_imprisoned_by = root } }',
            ai='base = 5 modifier = { add = 70 has_trait = greedy } modifier = { add = 50 has_trait = deceitful } modifier = { factor = 0 OR = { has_trait = honest has_trait = just } }',stress='honest = 25 just = 25'),
        opt('favor_offer','An obligation to me might settle this more quietly.',fx('mam_justice_offer_effect = { KIND = 2 }'),
            'Offer a conditional native Favor Hook for an actual pardon or release. No hook is created before agreement and successful execution. A successor cannot collect it. The demand can be reported to the Censor.',
            condition='mam_justice_officer_trigger = yes NOT = { has_character_modifier = mam_jus_restrained } scope:mam_jus_case = { NOT = { has_variable = mam_jus_offer_author } } OR = { AND = { mam_justice_action_2_available = yes scope:mam_jus_pardon_performer = root } scope:mam_jus_subject = { is_imprisoned_by = root } } NOT = { has_hook = scope:mam_jus_subject } can_add_hook = { target = scope:mam_jus_subject type = favor_hook }',
            ai='base = 5 modifier = { add = 55 has_trait = ambitious } modifier = { add = 55 has_trait = deceitful } modifier = { factor = 0 OR = { has_trait = honest has_trait = just } }',stress='honest = 25 just = 25'),
        opt('shadow','I will act on my own seal, despite the instructions.',fx(move(9)),
            'Consider an explicitly unauthorized arrest, pardon or release. Native permissions and real costs still apply. Actual unauthorized conduct is attributable to you and can provoke Censor scrutiny, restraint or an imperial warrant. Capital punishment and banishment cannot use this bypass.',
            condition='mam_justice_officer_trigger = yes NOT = { has_character_modifier = mam_jus_restrained }',
            ai='base = 3 modifier = { add = 35 has_trait = arbitrary } modifier = { add = 30 has_trait = vengeful has_relation_rival = scope:mam_jus_subject } modifier = { factor = 0 OR = { has_trait = just has_trait = honest } }'),
        opt('defer','I need more time before deciding.',fx('change_variable = { name = mam_jus_delay add = 1 } '+move(4,30)),
            'Defer once for 30 days. Older delayed business can trigger a coordination appeal. No native deadline becomes an automatic guilty verdict.',
            condition='scope:mam_jus_case.var:mam_jus_delay = 0',ai='base = 5 modifier = { add = 40 has_trait = lazy } modifier = { add = 25 has_trait = craven }'),
        opt('retain','Leave the existing custody to the native process for now.',fx(close(8)),
            'Close this custom hearing without changing custody, criminal rights or punishment. The prisoner remains where the native game holds them. A single petition may challenge the handling; no new conviction is recorded.',
            condition='scope:mam_jus_subject = { is_imprisoned = yes }',ai='base = 10 modifier = { add = 45 has_trait = callous } modifier = { add = 65 has_trait = vengeful has_relation_rival = scope:mam_jus_subject }',stress='compassionate = 10'),
        opt('return_admin','The remaining question is administrative, not a criminal sentence.',fx(close(1)),
            'End this proceeding without changing native criminal rights, custody or the Censor\'s findings. Unsupported allegations do not become convictions.',ai='base = 15 modifier = { add = 60 scope:mam_jus_subject = { mam_justice_native_ground_trigger = no is_imprisoned = no } }'),
    ])
    event(4,'What Shall Justice Do?',
          'I have heard the matter concerning #bold [scope:mam_jus_subject.GetShortUIName]#!. The next decision will determine how the law is used, who benefits from mercy, and who must answer for the exercise of this office.',choices)
    event(5,'A Judicial Memorial Before the Throne',
          'Justice has brought the matter concerning #bold [scope:mam_jus_subject.GetShortUIName]#! before me. My seal authorizes a particular measure, not a verdict written in advance. The current law, the actual custodian and native permissions must still be respected.',[
        opt('approve','Authorize the proposed measure under my seal.',fx('mam_justice_native_bind_effect = yes mam_justice_approve_effect = yes '+move(11,1)),
            common_cost+'Authorize only the current proposal. A changed emperor, law, custodian, payer balance or legal eligibility can require renewed review. Native execution effects apply only if the measure is actually carried out.',
            condition='scope:mam_jus_case = { var:mam_jus_action > 0 trigger_if = { limit = { var:mam_jus_action = 7 } mam_justice_selected_offense_trigger = yes } }',
            ai='base = 90 modifier = { add = 40 has_trait = just scope:mam_jus_subject = { mam_justice_native_ground_trigger = yes } } modifier = { factor = 0.2 has_relation_friend = scope:mam_jus_subject scope:mam_jus_case.var:mam_jus_action = 4 }',preview=True),
        opt('return','Hear the matter again, with my supervision.',fx('set_variable = { name = mam_jus_supervised value = 1 } remove_variable = mam_jus_shadow '+move(4)),
            'Require imperial approval for further measures in this case. Return it to the current unconflicted judge. No crime, pardon, release or title change occurs.',
            condition='scope:mam_jus_case = { NOT = { has_variable = mam_jus_receipt_review } }',ai='base = 35 modifier = { add = 50 has_trait = paranoid }'),
        opt('refuse','This matter needs no further action under my seal.',fx(close(9)),
            'Refuse and end this custom proposal. Existing native custody and criminal rights remain; no failed recommendation is reported as a completed action.',ai='base = 35 modifier = { add = 80 has_relation_friend = scope:mam_jus_subject }'),
        opt('rebuke','This minister must answer for the recorded handling.',fx('mam_justice_rebuke_effect = yes '+close(11)),
            'The actual living author of a recorded private solicitation or unauthorized act loses 75 Influence and is restrained for 2 years (-10% monthly Influence, -5 General Opinion). A later minister does not inherit that sanction. This does not reverse a pardon or revive consumed criminal reasons.',
            condition='scope:mam_jus_case = { NOT = { has_variable = mam_jus_rebuked } mam_justice_known_misconduct_trigger = yes OR = { exists = var:mam_jus_offer_author exists = var:mam_jus_violation_author } }',
            ai='base = 65 modifier = { add = 70 has_trait = just } modifier = { factor = 0.3 exists = scope:mam_jus_offer_author has_relation_friend = scope:mam_jus_offer_author }'),
    ])
    event(6,'A Measure Requiring My Consent',
          'The government asks you to act concerning #bold [scope:mam_jus_subject.GetShortUIName]#!. Your own authority and consent are required before the measure can proceed.',[
        opt('custodian_accept','I will carry out the authorized measure.',fx('set_variable = { name = mam_jus_custodian_consent value = root } '+move(11,1)),
            common_cost+'Consent as the actual performer. A pardon consumes the identified authority\'s full current bundle. Custody and any required prisoner agreement remain necessary for release or punishment.',ai='base = 110 modifier = { add = 50 has_trait = loyal }'),
        opt('custodian_refuse','I will not consent to this measure.',
            'add_opinion = { target = scope:mam_jus_judge modifier = mam_jus_defied } '+fx('set_variable = { name = mam_jus_failed_action value = var:mam_jus_action } '+move(4)),
            'Refuse your consent and lose 20 Opinion of the deciding judge for 5 years. Custody is unchanged. Refusal is recorded, not automatically converted into a new crime.',ai='base = 20 modifier = { add = 80 has_relation_friend = scope:mam_jus_subject } modifier = { add = 45 has_trait = stubborn }'),
    ],letter=True)
    event(7,'A Price for Mercy',
          'I may be able to bring your matter to a favorable end. Before I put my seal to it, I require something in return. You know what my office can do, and what further delays might cost.',[
        opt('accept_gold','I will pay the agreed 100 Gold if the promised act is carried out.',fx('set_variable = { name = mam_jus_offer_agreed value = 1 } mam_justice_propose_effect = { ACTION = var:mam_jus_offer_action }'),
            'Agree conditionally. Exactly 100 of your personal Gold transfers to the actual proposer only after an actual agreed pardon/release, if they still hold Justice and both parties remain eligible. Public Treasury is not used. No payment occurs now.',
            condition='scope:mam_jus_case = { var:mam_jus_offer_kind = 1 mam_justice_offer_valid_trigger = yes } gold >= 100',
            ai='base = 35 modifier = { add = 80 has_trait = craven } modifier = { factor = 0.1 has_trait = just }',stress='honest = 15 just = 15'),
        opt('accept_favor','I will owe the agreed favor if the promised act is carried out.',fx('set_variable = { name = mam_jus_offer_agreed value = 1 } mam_justice_propose_effect = { ACTION = var:mam_jus_offer_action }'),
            'Agree conditionally to one native Favor Hook for the actual current proposer after a successful agreed pardon/release. If that pardon itself grants a native Loyalty Hook, it fulfills the obligation without a second hook. A successor cannot collect it; no hook is created now.',
            condition='scope:mam_jus_case = { var:mam_jus_offer_kind = 2 mam_justice_offer_valid_trigger = yes }',ai='base = 35 modifier = { add = 80 has_trait = craven }',stress='honest = 15 just = 15'),
        opt('refuse_offer','I will not purchase this decision.',fx('set_variable = { name = mam_jus_offer_void value = 1 } '+move(4)),
            'Refuse without a payment, hook, pardon or punishment. The demand remains the responsibility of its actual author.',ai='base = 60 modifier = { add = 80 has_trait = just }'),
        opt('report_offer','The throne and the Censor should hear this demand.',fx('set_variable = { name = mam_jus_offer_reported value = 1 } set_variable = { name = mam_jus_offer_void value = 1 } set_variable = { name = mam_jus_action value = 0 } '+move(5)),
            'Report the actual recorded solicitation to the emperor. It may support Censor scrutiny of its author; it does not automatically convict anyone, erase evidence or remove their office.',ai='base = 50 modifier = { add = 80 has_trait = just } modifier = { add = 50 has_trait = brave }'),
    ],letter=True)
    event(8,'Justice Cannot Remain Unanswered',
          'The handling of #bold [scope:mam_jus_subject.GetShortUIName]#!\'s matter has prompted a petition. I can press for a timely answer or bring the complaint before the throne. Coordination does not give me the right to erase evidence or judge my own interests.',[
        opt('expedite','Justice must give a timely, reasoned answer.',fx('set_variable = { name = mam_jus_advocacy value = -1 } '+move(4,1)),
            'Return unfinished business for an answer. This is pressure, not approval of a punishment. A completed disposition cannot be replayed through this option.',
            condition='scope:mam_jus_case = { NOT = { has_variable = mam_jus_receipt_review } }',ai='base = 100 modifier = { add = 50 has_trait = diligent }'),
        opt('appeal_throne','Let the emperor hear the complaint.',fx('set_variable = { name = mam_jus_action value = 0 } '+move(5)),
            'Escalate one procedural appeal. Completed pardons, releases and punishments remain completed; consumed native rights are not recreated.',ai='base = 65 modifier = { add = 50 has_trait = just }'),
        opt('uphold','The recorded disposition should stand.',fx(close(9)),
            'Close this review without a new native action or punishment. This does not declare that every earlier choice was wise.',ai='base = 25 modifier = { add = 60 has_trait = content }'),
    ])
    shadow=[]
    for action,text in ((1,'Take custody on my own authority.'),(2,'Grant the native pardon on my own authority.'),(3,'Release my prisoner on my own authority.')):
        shadow.append(opt('shadow_'+str(action),text,fx('set_variable = { name = mam_jus_shadow value = 1 } '+f'mam_justice_propose_effect = {{ ACTION = {action} }}'),
                          'Explicitly bypass reserved approval for this noncapital measure. Real native permissions, acceptance, custody and costs still apply. If executed, the breach is recorded against you and can be investigated. No criminal reason is fabricated to make an arrest lawful.',
                          condition=f'mam_justice_officer_trigger = yes mam_justice_action_{action}_available = yes'+(' scope:mam_jus_subject = { is_imprisoned_by = root }' if action==3 else ' scope:mam_jus_pardon_performer = root' if action==2 else ' scope:mam_jus_arrest_performer = root')+' OR = { scope:mam_jus_emperor = { has_realm_law = mam_justice_authority_reserved } scope:mam_jus_case = { has_variable = mam_jus_supervised } scope:mam_jus_subject = { tgp_is_any_minister = yes }'+(' scope:mam_jus_subject = { mam_justice_native_ground_trigger = no }' if action==1 else ' scope:mam_jus_pardon_authority = { has_extra_criminal_reason_against_trigger = { CRIMINAL = scope:mam_jus_subject } }' if action==2 else '')+' }',
                          ai='base = 30 modifier = { add = 40 has_trait = arbitrary }',stress='just = 25 honest = 20'))
    shadow.append(opt('shadow_back','I will return to the lawful choices.',fx(move(4)),
                      'Return without an action or breach.',ai='base = 80 modifier = { add = 60 has_trait = just }'))
    event(9,'The Reach of My Own Seal','I can try to exercise the ministry\'s native powers without the required higher authority. Doing so would be my decision, recorded against me; it would not turn an accusation into truth.',shadow)
    event(10,'Terms of Banishment','The proposed terms would release you through native banishment. Do you accept these terms? Imperial authorization does not stand in for your agreement, and the current custodian must still consent.',[
        opt('accept_terms','I accept these terms.',fx('set_variable = { name = mam_jus_terms_consent value = scope:mam_jus_performer } '+move(11,1)),
            'Consent to the currently named custodian\'s native banishment terms. Eligibility and imperial approval are rechecked. Native forfeiture/title consequences may apply; no action occurs until commitment.',ai='base = 75 modifier = { add = 60 has_trait = craven }'),
        opt('reject_terms','I will not agree to these terms.',fx('set_variable = { name = mam_jus_failed_action value = 5 } '+move(4)),
            'Refuse. No banishment or forfeiture occurs, and your refusal does not create a crime.',ai='base = 35 modifier = { add = 70 has_trait = stubborn } modifier = { add = 50 has_trait = brave }'),
    ],letter=True)
    loc('result_title','The Judicial Disposition')
    loc('result_subject','Concerning #bold [scope:mam_jus_subject.GetShortUIName]#! and the proceeding begun at [scope:mam_jus_office.GetName]:\n\n')
    loc('result_costs','\n\nThe last completed measure was carried out by [scope:mam_jus_last_performer.GetShortUIName]. Native costs charged for that measure: [scope:mam_jus_paid_treasury|0] @treasury_icon!, [scope:mam_jus_paid_gold|0] @gold_icon!, [scope:mam_jus_paid_influence|0] Influence, [scope:mam_jus_paid_prestige|0] Prestige and [scope:mam_jus_paid_piety|0] Piety. Other native consequences remain in effect.')
    loc('result_external','\n\nAn independent native action resolved the pending proposal. Its native interface handled its costs and consequences; the custom proceeding did not charge or execute it again.')
    loc('result_desc','The ministry has recorded its disposition concerning [scope:mam_jus_subject.GetShortUIName]. Native actions, if completed, retain their actual effects. A closed hearing is not automatically a conviction or pardon. The disposition and its responsible participants remain on record.')
    result_text={1:'This proceeding ended without a new punishment. Native criminal rights and any existing custody were not cleared.',
                 2:'The original native pardon was carried out. It clears the affected authority\'s native criminal reasons as that action specifies; it does not itself release a prisoner or erase historical facts.',
                 3:'The agreed native release was carried out. The former custodian no longer holds this prisoner. Other criminal grounds were not automatically pardoned.',
                 4:'The authorized native execution was carried out by the actual custodian. Its native consequences and succession now apply.',
                 5:'The authorized, agreed native banishment was carried out. Its native release, forfeiture and title consequences, where applicable, remain in effect.',
                 6:'Only the separate imperial warrant created by this module was withdrawn. Unrelated native criminal reasons remain.',
                 8:'The custom hearing ended without altering the existing custody. This is not a new conviction or sentence.',
                 9:'The proposal or review was closed without another native action. No earlier completed pardon, release or punishment was replayed.',
                 10:'Death, changed jurisdiction, unavailable eligibility or the outer time limit ended the proceeding. No new success is claimed.',
                 11:'The recorded author of the handling was rebuked and restrained. This did not reverse a completed disposition or recreate a consumed criminal reason.'}
    branches=[]
    for n,text in result_text.items():
        key=loc('result_'+str(n),text)
        branches.append(f'triggered_desc = {{ trigger = {{ scope:mam_jus_case.var:mam_jus_result = {n} }} desc = {key} }}')
    loc('received','The decision is recorded.')
    events.append('''mam_justice.90 = { type = letter_event sender = scope:mam_jus_sender title = mam_jus.result_title
     opening = { desc = mam_jus.opening } desc = { desc = mam_jus.result_subject first_valid = { '''+' '.join(branches)+''' desc = mam_jus.result_desc }
      first_valid = {
       triggered_desc = { trigger = { scope:mam_jus_case = { has_variable = mam_jus_native_external } } desc = mam_jus.result_external }
       triggered_desc = { trigger = { exists = scope:mam_jus_last_performer scope:mam_jus_case = { has_variable = mam_jus_last_action } } desc = mam_jus.result_costs }
      }
     }
     option = { name = mam_jus.received ai_chance = { base = 100 } } }''')
    labels.update({
        'mam_justice_resume_decision':'Justice: Resume My Pending Business',
        'mam_justice_petition_decision':'Justice: Petition for Review of My Treatment',
        'mam_jus.petition':'Submit my petition.',
        'mam_justice_resume_decision_desc':'Recall the judicial matter currently addressed to you. This cannot repeat a completed disposition.',
        'mam_jus.resume':'Bring the papers.',
        'mam_jus.native_authority_tt':'This senior judicial measure requires the current authority and native permissions. Use the Ministry judicial interaction to propose a reserved action. Special mutilation, coerced vows and other exceptional release terms remain outside delegated Justice.',
        'mam_justice_authority_laws':'Judicial Authority',
        'mam_justice_authority_delegated':'Delegate Ordinary Justice',
        'mam_justice_authority_delegated_effects':'Justice may take ordinary senior custody, grant ordinary native pardons and arrange release within native permissions. Capital punishment, banishment, imperial warrants, severe pardons, central ministers and protected imperial family require the emperor. Actual custody and prisoner consent remain necessary. Selling appointments, knowingly false official certification, soliciting private benefit for judicial acts and unauthorized judicial coercion may support a documented imperial warrant; accusations alone do not.',
        'mam_justice_authority_reserved':'Reserve Senior Judicial Measures',
        'mam_justice_authority_reserved_effects':'Senior arrests, native pardons and releases also require the emperor\'s approval. Capital punishment, banishment and custom warrants remain reserved. Hearings and advice do not need a seal. A bypass uses actual native powers at the minister\'s own risk and creates an attributable record. No instruction turns suspicion into guilt.',
        'mam_jus_imperial_warrant':'Imperial Warrant for Abuse of Public Office',
        'mam_jus_grateful':'Granted Judicial Mercy',
        'mam_jus_resentment':'Subjected Me to Judicial Action',
        'mam_jus_advocated':'Spoke for Me in a Judicial Matter',
        'mam_jus_defied':'Disputed My Judicial Direction',
        'mam_jus_restrained':'Judicial Powers Restrained',
        'mam_jus_restrained_desc':'Ordinary senior measures require imperial review. Private judicial bargains and the unauthorized bypass are blocked. Monthly Influence: -10%; General Opinion: -5.',
        'mam_justice_review_interaction':'Justice: Refer a Judicial Matter',
        'mam_justice_review_interaction_desc':'Ask Justice to hear a supported senior criminal matter or review actual custody. A referral is not a conviction. The current minister or an unconflicted emperor handles it.',
        'mam_justice_petition_interaction':'Justice: Petition for Review',
        'mam_justice_petition_interaction_desc':'Petition once concerning this person\'s current or recent judicial proceeding. Eligible participants may seek coordination or imperial review. Completed actions are not undone or replayed.',
        'mam_jus.queue_room':'The judicial queue has room and this person has no active proceeding or recent duplicate referral.',
        'mam_jus.censor_referral':'Refer the senior matter to Justice without declaring guilt. Censor\'s administrative inspection remains independently completable.',
    })
    bullet=lambda rows:'\n'.join('$EFFECT_LIST_BULLET$#indent_newline:3 '+row+'#!' for row in rows)
    shared=['Capital punishment, banishment and custom imperial warrants always require the current emperor',
            'The actual custodian and any required prisoner consent are respected; no accusation automatically establishes guilt',
            'Actual appointment-for-payment, knowingly false official certification, judicial solicitation and unauthorized coercion may support an explicit imperial warrant under the new statute',
            'New custom offenses apply prospectively from this statute\'s adoption; earlier records remain available for administrative scrutiny',
            'Changes cost 150 Prestige, require peace and have a five-year cooldown']
    labels['mam_justice_authority_delegated_effects']=bullet(['Justice handles ordinary senior custody, native pardons and release within native permissions',
            'Central ministers, protected imperial family, severe pardons and supervised cases require the emperor']+shared)
    labels['mam_justice_authority_reserved_effects']=bullet(['Senior arrests, native pardons and releases also require imperial approval',
            'Hearings and advice remain independent; an unauthorized noncapital bypass creates a record against its actual author']+shared)
    labels['mam_justice_authority_laws_desc']='Determine how much senior judicial authority the emperor delegates to Justice.'
    labels['mam_justice_authority_delegated_desc']='Entrust ordinary proceedings to the minister while reserving grave measures and protected cases.'
    labels['mam_justice_authority_reserved_desc']='Require the imperial seal for senior measures while Justice prepares and hears the cases.'
