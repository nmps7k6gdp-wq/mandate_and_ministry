"""Engine-log fixes and readable statements for the generated common-fund module.

Called after build_common_fund.py. All writes stay inside this mod.
"""
from pathlib import Path
import json
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]
parse=runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']
ROSTER=['e_minister_chancellor','e_minister_censor','e_minister_grand_marshal',
        'e_minister_of_personnel','e_minister_of_war','e_minister_of_rites',
        'e_minister_of_works','e_minister_of_revenue','e_minister_of_justice']

def read(rel): return (ROOT/rel).read_text(encoding='utf-8-sig')
def write(rel,s): (ROOT/rel).write_text(s.rstrip()+'\n',encoding='utf-8-sig')
def edit(rel,key,fn):
    s=read(rel); n=next(n for n in parse(s) if n.key==key)
    write(rel,s[:n.start]+fn(s[n.start:n.end])+s[n.end:])
def append(rel,s): write(rel,read(rel)+'\n'+s)
def insert_effect(rel,key,extra): edit(rel,key,lambda s:s[:-1]+'\n'+extra+'\n}')

values='common/script_values/mam_revenue_common_values.txt'
append(values,r'''
# Scripted-effect arguments must be atomic references, not inline value blocks.
mam_revenue_fund_imperial_topup_quote = {
 value = title:h_china.var:mam_cf_unfunded add = title:h_china.var:mam_cf_claims_due
 add = title:e_minister_of_revenue.mam_revenue_fund_cash_target
 subtract = title:e_minister_of_revenue.holder.treasury
 min = 200 max = 1000 max = { value = treasury subtract = 500 min = 0 }
}
''')
rel='common/scripted_effects/mam_revenue_common_initiative_effects.txt'
s=read(rel)
for top in reversed(parse(s)):
    for n in sorted([n for n in top.walk() if n.key=='mam_revenue_fund_request_effect'],key=lambda n:n.start,reverse=True):
        amount=next((c for c in n.children if c.key=='AMOUNT' and c.children),None)
        if amount:
            s=s[:amount.start]+'AMOUNT = mam_revenue_fund_imperial_topup_quote'+s[amount.end:]
write(rel,s)

events='events/mam_revenue_common_events.txt'
s=read(events).replace('base = mam_revenue_fund_support_weight',
                     'base = 0 modifier = { add = mam_revenue_fund_support_weight }')
# current_heir is a TITLE link; this event's root is a character. The native
# eligibility expressions here do not need founder_heir at all.
s=s.replace('current_heir ?= { save_scope_as = founder_heir }','')
write(events,s)
op='common/opinion_modifiers/mam_revenue_common_opinions.txt'
write(op,read(op).replace('decaying = yes','years = 2 decaying = yes'))

# Hide implementation-only predicates when the engine builds option tooltips.
# Visible requirements receive meaningful text instead of variable/lease names.
interactions='common/character_interactions/mam_revenue_common_interactions.txt'
requirements={
 'mam_revenue_fund_review_operations_interaction':'mam_cf.operations_ready_tt',
 'mam_revenue_fund_request_operations_interaction':'mam_cf.operations_ready_tt',
 'mam_revenue_fund_petition_interaction':'mam_cf.petition_ready_tt',
 'mam_revenue_fund_remittance_interaction':'mam_cf.remittance_ready_tt',
 'mam_revenue_fund_project_interaction':'mam_cf.project_ready_tt',
 'mam_revenue_fund_appeal_interaction':'mam_cf.appeal_ready_tt',
 'mam_revenue_fund_supplement_interaction':'mam_cf.supplement_ready_tt',
}
s=read(interactions)
for top in reversed(parse(s)):
    valid=next((n for n in top.children if n.key=='is_valid'),None)
    if valid and top.key in requirements:
        opening=s.index('{',valid.start)
        body=s[opening+1:valid.end-1]
        replacement='is_valid = { custom_tooltip = { text = '+requirements[top.key]+' hidden_trigger = {'+body+'\n} } }'
        s=s[:valid.start]+replacement+s[valid.end:]
write(interactions,s)

def hide_option_gates(rel):
    s=read(rel); edits=[]
    for top in parse(s):
        for option in (n for n in top.children if n.key=='option'):
            trigger=next((n for n in option.children if n.key=='trigger'),None)
            if trigger:
                opening=s.index('{',trigger.start)
                body=s[opening+1:trigger.end-1]
                edits.append((trigger.start,trigger.end,'trigger = { hidden_trigger = {'+body+'\n} }'))
    for a,b,t in sorted(edits,reverse=True): s=s[:a]+t+s[b:]
    write(rel,s)
hide_option_gates(events)
# Visible conditional effects also contribute requirements to automatic tooltips.
s=read(events); inserts=[]
for top in parse(s):
    for option in (n for n in top.children if n.key=='option'):
        for n in option.walk():
            if n.key!='limit': continue
            ancestors=[]; parent=n.parent
            while parent is not option and parent is not None:
                ancestors.append(parent.key); parent=parent.parent
            if any(k in ancestors for k in ['hidden_effect','ai_chance','trigger']): continue
            opening=s.index('{',n.start)
            inserts += [(opening+1,' hidden_trigger = { '),(n.end-1,' } ')]
for at,code in sorted(inserts,reverse=True): s=s[:at]+code+s[at:]
write(events,s)
preview='common/scripted_effects/mam_revenue_common_preview_effects.txt'
s=read(preview); edits=[]
for top in parse(s):
    for n in top.walk():
        if n.key=='limit':
            opening=s.index('{',n.start)
            edits.append((n.start,n.end,'limit = { hidden_trigger = {'+s[opening+1:n.end-1]+'\n} }'))
for a,b,t in sorted(edits,reverse=True): s=s[:a]+t+s[b:]
write(preview,s)

# These purpose IDs are earned-claim records, not ordinary per-title slots.
queue='common/scripted_effects/mam_revenue_common_queue_effects.txt'
s=read(queue); top=next(n for n in parse(s) if n.key=='mam_revenue_fund_close_effect')
cuts=[]
for n in top.children:
    if n.key=='if' and any(c.key=='var:mam_cf_kind' and c.value in {'8','10','11'} for c in n.walk()): cuts.append((n.start,n.end))
for a,b in sorted(cuts,reverse=True): s=s[:a]+s[b:]
write(queue,s)

# Real collection/refill figures. A statement covers the scheduled settlement,
# not estimated native income, outside grants or cash created by an alias.
cash='common/scripted_effects/mam_revenue_common_cash_effects.txt'
insert_effect(cash,'mam_revenue_fund_init_office_effect',r'''
 if = { limit = { NOT = { has_variable = mam_cf_statement_collected } }
  set_variable = { name = mam_cf_statement_collected value = 0 }
  set_variable = { name = mam_cf_statement_received value = 0 }
 }
''')
edit(cash,'mam_revenue_fund_sweep_effect',lambda s:s.replace('mam_revenue_fund_transfer_effect = yes',r'''
  mam_revenue_fund_transfer_effect = yes
  if = { limit = { title:h_china = { has_variable = mam_cf_recording_statement } scope:mam_cf_paid > 0 }
   change_variable = { name = mam_cf_statement_collected add = scope:mam_cf_paid }
   title:h_china = { change_variable = { name = mam_cf_statement_collected add = scope:mam_cf_paid } }
  }
'''))
edit(cash,'mam_revenue_fund_refill_effect',lambda s:s.replace(
 'change_variable = { name = mam_cf_issued add = scope:mam_cf_paid }',r'''
 change_variable = { name = mam_cf_issued add = scope:mam_cf_paid }
 if = { limit = { title:h_china = { has_variable = mam_cf_recording_statement } scope:mam_cf_paid > 0 }
  change_variable = { name = mam_cf_statement_received add = scope:mam_cf_paid }
  title:h_china = { change_variable = { name = mam_cf_statement_advanced add = scope:mam_cf_paid } }
 }
'''))
begin=r'''
 title:h_china = {
  set_variable = { name = mam_cf_recording_statement value = 1 }
  set_variable = { name = mam_cf_statement_collected value = 0 }
  set_variable = { name = mam_cf_statement_advanced value = 0 }
  set_variable = { name = mam_cf_statement_opening value = title:e_minister_of_revenue.holder.treasury }
 }
'''
for t in ROSTER:
    begin+='title:'+t+' = { set_variable = { name = mam_cf_statement_collected value = 0 } set_variable = { name = mam_cf_statement_received value = 0 } }\n'
s=read(cash); top=next(n for n in parse(s) if n.key=='mam_revenue_fund_month_effect')
part=s[top.start:top.end]
first_sweep=part.index('title:e_minister_chancellor = { if = { limit = { exists = holder holder = { mam_revenue_ministry_trigger = yes } } mam_revenue_fund_sweep_effect = yes')
part=part[:first_sweep]+begin+part[first_sweep:]
part=part.replace('mam_revenue_fund_refresh_totals_effect = yes',r'''
 title:h_china = {
  set_variable = { name = mam_cf_statement_closing value = title:e_minister_of_revenue.holder.treasury }
  set_variable = { name = mam_cf_statement_date value = current_date }
  remove_variable = mam_cf_recording_statement
 }
 mam_revenue_fund_refresh_totals_effect = yes
''',1)
write(cash,s[:top.start]+part+s[top.end:])

# Dashboard presentation values are rebound in each event's own immediate block.
# Correspondence uses saved event scopes; localization uses the DATA syntax
# [name.GetName]/[name|0], never the script syntax [scope:name...].
append('common/scripted_effects/mam_revenue_common_queue_effects.txt',r'''
mam_revenue_fund_bind_accounts_effect = {
 mam_revenue_fund_refresh_totals_effect = yes
 title:h_china.holder = { save_scope_as = mam_cf_emperor }
 save_scope_value_as = { name = mam_cf_fund_balance value = 0 }
 if = { limit = { mam_revenue_fund_custodian_trigger = yes }
  title:e_minister_of_revenue.holder = { save_scope_value_as = { name = mam_cf_fund_balance value = treasury } }
 }
 save_scope_value_as = { name = mam_cf_reserve value = title:h_china.var:mam_cf_reserve }
 save_scope_value_as = { name = mam_cf_free value = title:h_china.mam_revenue_fund_available }
 save_scope_value_as = { name = mam_cf_monthly value = title:h_china.var:mam_cf_total_cost }
 save_scope_value_as = { name = mam_cf_collected value = 0 }
 save_scope_value_as = { name = mam_cf_advanced value = 0 }
 save_scope_value_as = { name = mam_cf_opening_balance value = 0 }
 save_scope_value_as = { name = mam_cf_closing_balance value = 0 }
 if = { limit = { title:h_china = { has_variable = mam_cf_statement_date } }
  save_scope_value_as = { name = mam_cf_collected value = title:h_china.var:mam_cf_statement_collected }
  save_scope_value_as = { name = mam_cf_advanced value = title:h_china.var:mam_cf_statement_advanced }
  save_scope_value_as = { name = mam_cf_opening_balance value = title:h_china.var:mam_cf_statement_opening }
  save_scope_value_as = { name = mam_cf_closing_balance value = title:h_china.var:mam_cf_statement_closing }
 }
 if = { limit = { mam_revenue_ministry_trigger = yes }
  save_scope_value_as = { name = mam_cf_local value = treasury }
  save_scope_value_as = { name = mam_cf_gold value = gold }
  save_scope_value_as = { name = mam_cf_cost value = primary_title.var:mam_cf_cost }
  save_scope_value_as = { name = mam_cf_headroom value = primary_title.var:mam_cf_headroom }
  save_scope_value_as = { name = mam_cf_target_balance value = primary_title.mam_revenue_fund_target }
  save_scope_value_as = { name = mam_cf_special value = primary_title.var:mam_cf_special_target }
  save_scope_value_as = { name = mam_cf_earmark value = primary_title.var:mam_cf_project_cash }
  save_scope_value_as = { name = mam_cf_left value = primary_title.var:mam_cf_remaining }
 }
}
''')

def set_immediate(s,code):
    node=parse(s)[0]; old=next((n for n in node.children if n.key=='immediate'),None)
    if old: return s[:old.start]+'immediate = { '+code+' }'+s[old.end:]
    return s[:-1]+'\n immediate = { '+code+' }\n}'
for eid in ['mam_fund.1','mam_fund.2','mam_fund.3','mam_fund.4','mam_fund.8','mam_fund.20']:
    edit(events,eid,lambda s:set_immediate(s,'mam_revenue_fund_bind_effect = yes'))
edit(events,'mam_fund.6',lambda s:set_immediate(s,'mam_revenue_fund_bind_accounts_effect = yes'))

# An available project and a new project are distinct entry points. Do not show
# an empty selection as though a request could be made.
decisions='common/decisions/mam_revenue_common_decisions.txt'
edit(decisions,'mam_revenue_fund_contribution_decision',lambda s:s.replace(
 'is_shown = {','is_shown = { any_great_project = { great_project_owner = { top_liege = title:h_china.holder } }',1))
# All ministers can discover the same supplementary request via their Decisions.
edit(decisions,'mam_revenue_fund_supplement_decision',lambda s:s.replace(
 'is_shown = { is_ai = no mam_revenue_fund_enabled_trigger = yes mam_revenue_officer_trigger = yes',
 'is_shown = { is_ai = no mam_revenue_fund_enabled_trigger = yes mam_revenue_ministry_trigger = yes'))

# Keep the dashboard compact. Detailed own-office data has its own native event.
edit(events,'mam_fund.6',lambda s:s.replace('desc = mam_cf.accounts_minister_desc','desc = mam_cf.accounts_desc'))
extra=r'''
 option = { name = mam_cf.view_own trigger = { hidden_trigger = { mam_revenue_ministry_trigger = yes } }
  hidden_effect = { trigger_event = mam_fund.10 }
 }
 option = { name = mam_cf.view_flow hidden_effect = { trigger_event = mam_fund.9 } }
 option = { name = mam_cf.view_departments trigger = { hidden_trigger = { mam_revenue_authority_trigger = yes } }
  hidden_effect = { trigger_event = mam_fund.11 }
 }
'''
# Move the actionable operating review into the own-office page to keep 6 small.
s=read(events); top=next(n for n in parse(s) if n.key=='mam_fund.6')
own_review=next(n for n in top.children if n.key=='option' and any(c.key=='name' and c.value=='mam_cf.review_mine' for c in n.children))
review_code=s[own_review.start:own_review.end]
s=s[:own_review.start]+s[own_review.end:]; write(events,s)
insert_effect(events,'mam_fund.6',extra)
append(events,r'''
mam_fund.9 = {
 type = character_event theme = stewardship title = mam_cf.flow_title desc = mam_cf.flow_desc
 immediate = { mam_revenue_fund_bind_accounts_effect = yes }
 left_portrait = { character = root animation = reading }
 option = { name = mam_cf.accounts_close }
}
mam_fund.10 = {
 type = character_event theme = stewardship title = mam_cf.own_title
 desc = { first_valid = {
  triggered_desc = { trigger = { has_title = title:e_minister_of_revenue } desc = mam_cf.own_revenue_desc }
  desc = mam_cf.own_desc
 } }
 immediate = { mam_revenue_fund_bind_accounts_effect = yes }
 left_portrait = { character = root animation = reading }
 option = { name = mam_cf.accounts_close }
}
''')
insert_effect(events,'mam_fund.10',review_code)

# Three real pages of three offices: balance, authorised working target, and the
# last scheduled collection/advance. No custom GUI or fictional second account.
for page in range(3):
    immediate=['mam_revenue_fund_bind_accounts_effect = yes']
    for index,t in enumerate(ROSTER[page*3:page*3+3],page*3+1):
        immediate += [f'''title:{t} = {{ save_scope_as = mam_cf_dept_{index} }}
 save_scope_value_as = {{ name = mam_cf_cash_{index} value = 0 }}
 save_scope_value_as = {{ name = mam_cf_goal_{index} value = 0 }}
 save_scope_value_as = {{ name = mam_cf_in_{index} value = 0 }}
 save_scope_value_as = {{ name = mam_cf_out_{index} value = 0 }}
 title:{t} = {{ if = {{ limit = {{ exists = holder holder = {{ mam_revenue_ministry_trigger = yes }} }}
 save_scope_value_as = {{ name = mam_cf_cash_{index} value = holder.treasury }}
 save_scope_value_as = {{ name = mam_cf_goal_{index} value = mam_revenue_fund_target }}
 if = {{ limit = {{ has_variable = mam_cf_statement_received }}
 save_scope_value_as = {{ name = mam_cf_in_{index} value = var:mam_cf_statement_received }}
 save_scope_value_as = {{ name = mam_cf_out_{index} value = var:mam_cf_statement_collected }}
 }}
 }} }}''']
    eid=11+page
    buttons='option = { name = mam_cf.accounts_close }'
    if page<2: buttons+=f'\n option = {{ name = mam_cf.next_accounts hidden_effect = {{ trigger_event = mam_fund.{eid+1} }} }}'
    if page>0: buttons+=f'\n option = {{ name = mam_cf.previous_accounts hidden_effect = {{ trigger_event = mam_fund.{eid-1} }} }}'
    append(events,f'''mam_fund.{eid} = {{
 type = character_event theme = stewardship title = mam_cf.departments_title desc = mam_cf.departments_{page}
 immediate = {{ {' '.join(immediate)} }}
 left_portrait = {{ character = root animation = reading }}
 {buttons}
}}''')

# Relevant instructions belong in tooltips, not in letters signed by officials.
# CK3 has custom_tooltip/custom_description triggers, not hidden_trigger.
# Replace the construction shorthand before writing the final source.
for rel in [events,interactions,preview]:
    write(rel,read(rel).replace('hidden_trigger = {',
        'custom_tooltip = { text = mam_cf.context_tt'))
local='localization/english/mam_revenue_common_l_english.yml'
loc={}
for line in read(local).splitlines()[1:]:
    match=re.fullmatch(r' ([\w.]+):0 (".*")',line)
    if match: loc[match[1]]=json.loads(match[2])
loc.update({
 'mam_cf.context_tt':'The current circumstances allow this choice.',
 'mam_cf.opening':'Concerning the public accounts,',
 'mam_cf.relief_desc':"[mam_cf_subject.GetShortUIName] asks for #high [mam_cf_quote|0]#! [treasury_i] for #high [mam_cf_title.GetName]#!.\n\nThe ministry has placed this request before me. Shall the common fund meet the expense?",
 'mam_cf.supplement_desc':"The ordinary provision for #high [mam_cf_title.GetName]#! will not cover its work. [mam_cf_subject.GetShortUIName] asks for an additional #high [mam_cf_quote|0]#! [treasury_i].\n\nShall the common fund provide the money?",
 'mam_cf.project_desc':"[mam_cf_subject.GetShortUIName] proposes a great project in #high [mam_cf_project_target.GetName]#! and requests #high [mam_cf_quote|0]#! [treasury_i].\n\nThe common fund would provide the starting expense. Shall this work receive our support?",
 'mam_cf.contribution_desc':"[mam_cf_subject.GetShortUIName] requests #high [mam_cf_quote|0]#! [treasury_i] towards #high [mam_cf_selected_project.GetName]#!.\n\nThis allowance would support further work on the project. Shall the common fund meet it?",
 'mam_cf.topup_desc':"The ministries seek an additional #high [mam_cf_quote|0]#! [treasury_i] from the imperial treasury.\n\nThe money would enter the common fund in Revenue's custody. Shall I grant this provision?",
 'mam_cf.remit_desc':"A contribution of #high [mam_cf_quote|0]#! [treasury_i] is proposed from #high [mam_cf_title.GetName]#! to the common fund.\n\nThe province must consent and retain sufficient money for its own affairs.",
 'mam_cf.debt_desc':"#high [mam_cf_title.GetName]#! seeks up to #high [mam_cf_quote|0]#! [treasury_i] to settle its public debt.\n\nThe common fund would pay only the debt still outstanding. Shall I authorize the request?",
 'mam_cf.programme_result_desc':"The spending programme has received the required seal. Revenue will follow these priorities when allocating public funds. Existing commitments remain in force.",
 'mam_cf.operations_result_desc':"The provision for #high [mam_cf_title.GetName]#! is approved: #high [mam_cf_cost|1]#! [treasury_i] in monthly recurring costs and #high [mam_cf_headroom|0]#! [treasury_i] in ordinary headroom.\n\nThe office will receive any funded shortfall at the next reconciliation.",
 'mam_cf.refused_result_desc':"The request concerning #high [mam_cf_title.GetName]#! has been refused. No money was released.\n\nExisting provision continues. A material operating refusal may be appealed once.",
 'mam_cf.paid_result_desc':"#high [mam_cf_result_amount|0]#! [treasury_i] has passed from #high [mam_cf_result_payer_title.GetName]#! to #high [mam_cf_result_payee_title.GetName]#!.\n\nBoth account changes are recorded. The approved measure has taken effect.",
 'mam_cf.reserved_result_desc':"#high [mam_cf_result_amount|0]#! [treasury_i] within the common fund is reserved for Revenue's approved project.\n\nThe money remains in custody until the project expense is paid.",
 'mam_cf.supplement_self_result_desc':"Revenue may use an additional #high [mam_cf_result_amount|0]#! [treasury_i] for its operations over the next 90 days.\n\nThis provision remains within the common account; no self-payment was made.",
 'mam_cf.unpaid_result_desc':"The proposed measure concerning #high [mam_cf_title.GetName]#! could not be completed. No successful payment is recorded.\n\nThe papers must be reviewed against the current accounts before money is released.",
 'mam_cf.accounts_desc':"Revenue holds #high [mam_cf_fund_balance|0]#! [treasury_i] in the common fund. After commitments and reserves, #high [mam_cf_free|0]#! [treasury_i] is available.\n\nLast reconciliation: #P [mam_cf_collected|0]#! [treasury_i] collected from departments; #N [mam_cf_advanced|0]#! [treasury_i] advanced for operations.\n\nProgramme: #high [mam_cf_emperor.Custom('MamRevenueFundProgramme')]#!. Authority: #high [mam_cf_emperor.Custom('MamRevenueFundAuthority')]#!.",
 'mam_cf.accounts_minister_desc':'$mam_cf.accounts_desc$',
 'mam_cf.operations_desc':"#high [mam_cf_title.GetName]#! reports #high [mam_cf_cost|1]#! [treasury_i] in recurring monthly expenses. Its proposed ordinary headroom is #high [mam_cf_headroom|0]#! [treasury_i].\n\nI must decide what provision its work deserves. Existing project advances are accounted for separately.",
 'mam_cf.programme_desc':"The common fund holds #high [mam_cf_fund_balance|0]#! [treasury_i]. Recurring commitments total #high [mam_cf_monthly|1]#! [treasury_i] a month; #high [mam_cf_reserve|0]#! [treasury_i] is protected.\n\nWhat should the government's remaining resources accomplish in the coming year?",
 'mam_cf.flow_title':'How the Public Funds Move',
 'mam_cf.flow_desc':"Native ministry income still reaches each office. At reconciliation, the office retains its approved operating balance and project advances; surplus passes to Revenue. The common fund then pays funded operating shortfalls.\n\nLast reconciliation moved #high [mam_cf_collected|0]#! [treasury_i] into custody and #high [mam_cf_advanced|0]#! [treasury_i] back to operations. Other grants, native income and expenses can change the balance between reconciliations.\n\nRevenue's treasury is the common bank. Its own operating permission is a smaller authorization within that bank. Personal Gold remains separate.",
 'mam_cf.own_title':'The Provision for My Office',
 'mam_cf.own_desc':"My public treasury holds #high [mam_cf_local|0]#! [treasury_i]. The approved operating target is #high [mam_cf_target_balance|0]#! [treasury_i], with #high [mam_cf_left|0]#! [treasury_i] left in ordinary advances this quarter.\n\nRecurring costs: [mam_cf_cost|1] [treasury_i] per month.\nProject funds: [mam_cf_earmark|0] [treasury_i].\nSupplementary provision: [mam_cf_special|0] [treasury_i].\n\nMy personal purse holds [mam_cf_gold|0] [gold_i]; it is separate from these public accounts.",
 'mam_cf.own_revenue_desc':"The #high [mam_cf_local|0]#! [treasury_i] in my native treasury is the #high common fund#!, not Revenue's private departmental budget.\n\nRevenue's own operating target is #high [mam_cf_target_balance|0]#! [treasury_i]. Its approved costs are [mam_cf_cost|1] [treasury_i] a month, with [mam_cf_earmark|0] [treasury_i] reserved for a project and [mam_cf_special|0] [treasury_i] in supplementary provision.\n\nMy personal purse holds [mam_cf_gold|0] [gold_i]. Gold, public cash and operating permission are different figures.",
 'mam_cf.view_own':'Examine the provision for my office.',
 'mam_cf.view_flow':'Explain the movement of public funds.',
 'mam_cf.view_departments':'Examine the departmental accounts.',
 'mam_cf.departments_title':'The Departmental Accounts',
 'mam_cf.next_accounts':'Bring the next accounts.',
 'mam_cf.previous_accounts':'Return to the previous accounts.',
 'mam_cf.operations_ready_tt':'The office must be qualified, have no unresolved operating review, and be outside its 90-day review interval.',
 'mam_cf.petition_ready_tt':'A qualified senior civilian office must have public debt or recovery needs, no pending petition, and no active relief cooldown. The common-fund administration must be available.',
 'mam_cf.remittance_ready_tt':'The province must be able to retain its protected 200 treasury, have no recovery need or unresolved contribution, and be outside its contribution cooldown.',
 'mam_cf.project_ready_tt':'The office must be eligible, have no unresolved or unreturned project advance, and be outside its 90-day allowance interval. Select a senior jurisdiction suitable for the native project.',
 'mam_cf.appeal_ready_tt':'The current holder must have a recent material cut or refusal, with no pending or previously used appeal for that decision.',
 'mam_cf.supplement_ready_tt':'The office must be qualified, have no pending supplementary request or active 90-day supplementary provision, and have access to the common-fund administration.',
})
for page in range(3):
    rows=[]
    for i in range(page*3+1,page*3+4):
        rows.append(f'#high [mam_cf_dept_{i}.GetName]#!\nCash: [mam_cf_cash_{i}|0] [treasury_i]; operating target: [mam_cf_goal_{i}|0] [treasury_i].\nLast reconciliation: [mam_cf_out_{i}|0] collected; [mam_cf_in_{i}|0] advanced.')
    loc[f'mam_cf.departments_{page}']='\n\n'.join(rows)+'\n\nOnly a qualified holder\'s primary-office treasury is shown. A vacant or unsynchronized office is reported as zero.'
loc['mam_cf.revise_tt']='Revise the proposed amount. This draft moves no money.'
loc['mam_cf.flow_desc'] += '\n\nRecorded opening: [mam_cf_opening_balance|0] [treasury_i]. Recorded closing: [mam_cf_closing_balance|0] [treasury_i]. Before the first reconciliation, these statement figures are zero.'
loc['mam_cf.recommend_tt']='Submit the proposal under the current fiscal law. Eligible delegated payments can be released directly; other measures require the proper superior. No payment may breach protected commitments.'
loc['mam_cf.approval_tt']+=' Supplementary provision lasts 90 days. Project advances bind their stated project or purpose and expire after one year; unused cash is reconciled. Existing salaries and standing obligations remain protected.'
loc['mam_revenue_fund_supplement_decision_desc']='Ask for a one-time public operating advance for a large expense. Choose the amount before submission. Revenue cannot approve its own increase; current authority and available cash determine who may release it.'
loc['mam_revenue_fund_contribution_decision_desc']='Request an allowance for an existing imperial project. For a new project, use Request Great Project Funding on an eligible senior governor.'
loc['mam_cf.contribution_choose_desc']='Which existing imperial project should receive an allowance for further contributions? Select a project below. A new project is proposed through the Ministry interaction on its intended senior governor.'
loc['mam_cf.project_request_tt']+=' The initial quote uses the native starting cost; treasury is advanced before planning. Native Influence and location requirements still apply.'
# Fix EVERY data-binding expression in this module, including button names.
loc={k:re.sub(r'\[scope:(mam_cf_\w+)',r'[\1',v) for k,v in loc.items()}
write(local,'l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items()))

# Build metadata only; native files are never written.
p=ROOT/'descriptor.mod'; text=p.read_text(encoding='utf-8-sig')
p.write_text(re.sub(r'version="[^"]+"','version="0.4.0-alpha.20-dev.50"',text,count=1),encoding='utf-8')
print('Applied dev.50 localization, compiler and statement fixes.')
