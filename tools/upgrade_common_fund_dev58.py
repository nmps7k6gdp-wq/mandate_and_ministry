"""Quiet pending invoices, safe native UI guards and campaign war feedback.

Apply through the full builder. No project cancellation, war recreation, save
editing, extra payment or uncertain-account reset is performed here.
"""
from pathlib import Path
import json
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]
parse=runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']


def read(rel):return (ROOT/rel).read_text(encoding='utf-8-sig')


def write(rel,text):
    (ROOT/rel).write_text(text.rstrip()+'\n',encoding='utf-8-sig' if Path(rel).suffix in {'.txt','.yml'} else 'utf-8')


def edit(rel,key,fn):
    text=read(rel);node=next(n for n in parse(text) if n.key==key)
    write(rel,text[:node.start]+fn(text[node.start:node.end])+text[node.end:])


triggers='common/scripted_triggers/mam_revenue_common_triggers.txt'
def guarded_location(s):
    node=next(n for n in parse(s)[0].children if n.key=='primary_title')
    inner=s[s.index('{',node.start)+1:node.end-1]
    return '''mam_revenue_fund_project_location_trigger = {
 primary_title = {
  has_variable = mam_cf_project_type
  trigger_if = { limit = { has_variable = mam_cf_project_type }
'''+inner+'\n}\n}\n}'
edit(triggers,'mam_revenue_fund_project_location_trigger',guarded_location)
edit(triggers,'mam_revenue_fund_contribution_trigger',lambda s:r'''mam_revenue_fund_contribution_trigger = {
 save_temporary_scope_value_as = { name = mam_cf_required_contribution_cost value = $COST$ }
 exists = scope:great_project
 primary_title = {
  NOT = { has_variable = mam_cf_payment_hold }
  OR = {
   AND = { has_variable = mam_pc_executing_project
    trigger_if = { limit = { has_variable = mam_pc_executing_project }
     var:mam_pc_executing_project = scope:great_project
    }
   }
   AND = {
    has_variable = mam_cf_project_instance has_variable = mam_cf_project_until has_variable = mam_cf_project_cash
    trigger_if = { limit = { has_variable = mam_cf_project_instance has_variable = mam_cf_project_until has_variable = mam_cf_project_cash }
     var:mam_cf_project_instance = scope:great_project
     var:mam_cf_project_until > current_date
     var:mam_cf_project_cash >= scope:mam_cf_required_contribution_cost
    }
   }
  }
 }
 trigger_if = { limit = { scope:great_project = { great_project_type = grand_campaign_project } }
  scope:great_project = { OR = {
   AND = { has_variable = mam_pc_launch_authorized
    trigger_if = { limit = { has_variable = mam_pc_launch_authorized } var:mam_pc_launch_authorized = 1 }
   }
   any_contribution = { contribution_id = attack_1 contribution_is_funded = yes }
  } }
 }
}''')

effects='common/scripted_effects/mam_revenue_common_project_orders.txt'
text=read(effects).replace('trigger_event = mam_fund.34','mam_revenue_fund_show_invoice_status_effect = yes')
write(effects,text+r'''
# Background discovery must never raise a modal merely because a request waits
# in the approval queue. Every scheduled worker resets this value to zero.
mam_revenue_fund_show_invoice_status_effect = {
 if = { limit = { is_ai = no scope:mam_cf_manual_invoice_action = 1 }
  trigger_event = mam_fund.34
 }
}
# Great-project scope. A campaign war is led by its native Marshal contributor.
# This once-only nonmodal notice also explains existing wars on save reload.
mam_revenue_fund_notify_campaign_war_effect = {
 if = { limit = {
  great_project_type = grand_campaign_project
  has_variable = grand_campaign_war exists = var:grand_campaign_war
  NOT = { has_variable = mam_pc_war_notice }
  title:h_china.holder = { is_ai = no }
 }
  save_scope_as = mam_cf_campaign_notice_project
  clear_saved_scope = mam_cf_campaign_notice_marshal
  every_contribution = { limit = { contribution_id = attack_1 contribution_is_funded = yes }
   contributor = { save_scope_as = mam_cf_campaign_notice_marshal }
  }
  if = { limit = { exists = scope:mam_cf_campaign_notice_marshal }
   set_variable = { name = mam_pc_war_notice value = 1 }
   title:h_china.holder = {
    send_interface_toast = { type = event_toast_effect_good title = mam_pc.campaign_underway
     left_icon = scope:mam_cf_campaign_notice_marshal right_icon = scope:mam_cf_campaign_notice_marshal
     custom_tooltip = mam_pc.campaign_underway_tt
    }
   }
  }
 }
}
''')
edit(effects,'mam_revenue_fund_choose_invoice_effect',lambda s:s.replace(
    'save_scope_as = mam_cf_contributor','save_scope_value_as = { name = mam_cf_manual_invoice_action value = 1 }\n save_scope_as = mam_cf_contributor',1))
edit(effects,'mam_revenue_fund_process_project_invoice_effect',lambda s:s.replace(
    'else = { mam_revenue_fund_open_project_budget_effect = yes }',
    'else_if = { limit = { scope:mam_cf_selected_project = { NOT = { has_variable = mam_pc_pending } } } mam_revenue_fund_open_project_budget_effect = yes }',1))
edit(effects,'mam_revenue_fund_project_driver_effect',lambda s:s.replace(
    '  title:h_china = { set_variable = { name = mam_pc_next_scan',
    '''  every_great_project = { limit = { great_project_owner = title:h_china.holder great_project_type = grand_campaign_project }
   mam_revenue_fund_notify_campaign_war_effect = yes
  }
  title:h_china = { set_variable = { name = mam_pc_next_scan''',1))

events='events/mam_revenue_common_project_orders.txt'
edit(events,'mam_fund.31',lambda s:s.replace(' immediate = {',' immediate = {\n  save_scope_value_as = { name = mam_cf_manual_invoice_action value = 0 }',1))
for eid in ['mam_fund.32','mam_fund.35']:
    def manual_options(s):
        names={'mam_pc.choose_one','mam_pc.choose_two','mam_pc.choose_three','mam_pc.launch'}
        edits=[]
        for option in (n for n in parse(s)[0].children if n.key=='option'):
            if any(n.key=='name' and n.value in names for n in option.children):
                hidden=next(n for n in option.children if n.key=='hidden_effect')
                edits.append(s.index('{',hidden.start)+1)
        for at in sorted(edits,reverse=True):
            s=s[:at]+'\n save_scope_value_as = { name = mam_cf_manual_invoice_action value = 1 }\n'+s[at:]
        return s
    edit(events,eid,manual_options)
edit(events,'mam_fund.34',lambda s:s.replace(' left_portrait =',
    ''' immediate = { if = { limit = { NOT = { has_variable = mam_pc_menu_offset } } set_variable = { name = mam_pc_menu_offset value = 0 } } }
 left_portrait =''',1))

local='localization/english/mam_revenue_common_l_english.yml'
loc={}
for line in read(local).splitlines()[1:]:
    m=re.fullmatch(r' ([\w.]+):0 (".*")',line)
    if m:loc[m[1]]=json.loads(m[2])
loc.update({
 'mam_pc.campaign_underway':'The Grand Campaign Is Under Way',
 'mam_pc.campaign_underway_tt':'[mam_cf_campaign_notice_marshal.GetShortUIName] has fulfilled the required pledge for [mam_cf_campaign_notice_project.GetName] and leads its Grand Campaign war. The campaign remains a native imperial project; inspect the Marshal’s war to follow the fighting.'
})
write(local,'l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items()))
p=ROOT/'descriptor.mod'
p.write_text(re.sub(r'version="[^"]+"','version="0.4.0-alpha.20-dev.58"',read('descriptor.mod'),count=1),encoding='utf-8')
print('Applied dev.58 quiet pending-invoice retries, guarded UI reads and once-only imperial campaign-war feedback.')
