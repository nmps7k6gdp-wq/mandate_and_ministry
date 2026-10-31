"""Separate standing expenses from discretionary caps; fund AI project readiness."""
from pathlib import Path
import json,re,runpy
ROOT=Path(__file__).resolve().parents[1]
parse=runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']
ROSTER=['e_minister_chancellor','e_minister_censor','e_minister_grand_marshal',
 'e_minister_of_personnel','e_minister_of_war','e_minister_of_rites','e_minister_of_works',
 'e_minister_of_revenue','e_minister_of_justice']
def read(rel):return (ROOT/rel).read_text(encoding='utf-8-sig')
def write(rel,s):(ROOT/rel).write_text(s.rstrip()+'\n',encoding='utf-8-sig' if Path(rel).suffix in {'.txt','.yml'} else 'utf-8')
def edit(rel,key,fn):
 s=read(rel);n=next(n for n in parse(s) if n.key==key)
 write(rel,s[:n.start]+fn(s[n.start:n.end])+s[n.end:])
def roster(code):return '\n'.join(f'title:{t} = {{ if = {{ limit = {{ exists = holder holder = {{ mam_revenue_ministry_trigger = yes }} }} {code} }} }}' for t in ROSTER)

values='common/script_values/mam_revenue_common_values.txt'
write(values,read(values)+r'''
# Standing native bills cannot wait behind a discretionary allowance review.
# Keep the approved cost record separate; observing a bill does not approve a
# project, a new recruit purchase, or a greater discretionary allowance.
mam_revenue_fund_service_cost = {
 value = var:mam_cf_cost
 if = { limit = { exists = holder } min = holder.mam_revenue_fund_observed_cost }
}
mam_revenue_fund_essential_target = {
 value = mam_revenue_fund_service_cost multiply = 2 add = var:mam_cf_project_cash
}
mam_revenue_fund_shortfall = {
 value = mam_revenue_fund_cash_target subtract = holder.treasury min = 0
 max = { value = mam_revenue_fund_essential_target subtract = holder.treasury min = 0 add = var:mam_cf_remaining }
}
''')
edit(values,'mam_revenue_fund_target',lambda s:'''mam_revenue_fund_target = {
 value = mam_revenue_fund_service_cost multiply = 2 add = var:mam_cf_headroom add = var:mam_cf_special_target
}''')
cash='common/scripted_effects/mam_revenue_common_cash_effects.txt'
edit(cash,'mam_revenue_fund_init_office_effect',lambda s:s.replace('var:mam_cf_cost multiply = 5 add = 150','var:mam_cf_headroom').replace('var:mam_cf_cost multiply = 3 add = var:mam_cf_headroom','var:mam_cf_headroom')[:-1]+r'''
 # Existing saves retain spent advances; only the discretionary cap migrates.
 if = { limit = { NOT = { has_variable = mam_cf_payroll_model } }
  set_variable = { name = mam_cf_remaining value = { value = var:mam_cf_headroom subtract = var:mam_cf_issued min = 0 max = var:mam_cf_remaining } }
  set_variable = { name = mam_cf_payroll_model value = 1 }
 }
}''')
edit(cash,'mam_revenue_fund_start_effect',lambda s:s.replace('var:mam_cf_cost multiply = 5 add = 150','var:mam_cf_headroom')[:-1]+r'''
 mam_revenue_fund_ensure_payroll_effect = yes
}''')
edit(cash,'mam_revenue_fund_count_effect',lambda s:'''mam_revenue_fund_count_effect = {
 save_scope_value_as = { name = mam_cf_service_cost value = mam_revenue_fund_service_cost }
 title:h_china = { change_variable = { name = mam_cf_total_cost add = scope:mam_cf_service_cost } }
 if = { limit = { this != title:e_minister_of_revenue }
  save_scope_value_as = { name = mam_cf_shortfall value = mam_revenue_fund_shortfall }
  title:h_china = { change_variable = { name = mam_cf_unfunded add = scope:mam_cf_shortfall } }
 }
}''')
edit(cash,'mam_revenue_fund_count_essential_effect',lambda s:s.replace('var:mam_cf_cost multiply = 2 add = var:mam_cf_project_cash','mam_revenue_fund_essential_target').replace('min = 0 max = var:mam_cf_remaining','min = 0'))
edit(cash,'mam_revenue_fund_refill_effect',lambda s:'''mam_revenue_fund_refill_effect = {
 if = { limit = { this != title:e_minister_of_revenue }
  save_scope_value_as = { name = mam_cf_goal value = mam_revenue_fund_essential_target }
  save_scope_value_as = { name = mam_cf_floor value = title:e_minister_of_revenue.mam_revenue_fund_cash_target }
  if = { limit = { always = $EXTRA$ }
   save_scope_value_as = { name = mam_cf_goal value = mam_revenue_fund_cash_target }
   save_scope_value_as = { name = mam_cf_floor value = { value = scope:mam_cf_floor add = title:h_china.var:mam_cf_reserve } }
  }
  save_scope_value_as = { name = mam_cf_amount value = {
   value = scope:mam_cf_goal subtract = holder.treasury min = 0
   max = { value = title:e_minister_of_revenue.holder.treasury subtract = scope:mam_cf_floor min = 0 }
  } }
  if = { limit = { always = $EXTRA$ }
   save_scope_value_as = { name = mam_cf_amount value = { value = scope:mam_cf_amount max = var:mam_cf_remaining } }
  }
  else_if = { limit = { title:h_china.var:mam_cf_essential_due > 0 }
   save_scope_value_as = { name = mam_cf_amount value = { value = scope:mam_cf_amount
    max = { value = title:h_china.var:mam_cf_essential_cash
     multiply = { value = scope:mam_cf_goal subtract = holder.treasury min = 0 }
     divide = title:h_china.var:mam_cf_essential_due }
   } }
  }
  holder = { save_scope_as = mam_cf_payee }
  title:e_minister_of_revenue.holder = { save_scope_as = mam_cf_payer }
  mam_revenue_fund_transfer_effect = yes
  if = { limit = { always = $EXTRA$ }
   change_variable = { name = mam_cf_remaining subtract = scope:mam_cf_paid }
   change_variable = { name = mam_cf_issued add = scope:mam_cf_paid }
  }
  if = { limit = { title:h_china = { has_variable = mam_cf_recording_statement } scope:mam_cf_paid > 0 }
   change_variable = { name = mam_cf_statement_received add = scope:mam_cf_paid }
   title:h_china = { change_variable = { name = mam_cf_statement_advanced add = scope:mam_cf_paid } }
  }
  else_if = { limit = { scope:mam_cf_paid > 0 }
   title:h_china = { change_variable = { name = mam_cf_interim_advances add = scope:mam_cf_paid } }
  }
 }
}''')
edit(cash,'mam_revenue_fund_month_effect',lambda s:s.replace('set_variable = { name = mam_cf_statement_advanced value = 0 }','set_variable = { name = mam_cf_statement_advanced value = 0 }\n set_variable = { name = mam_cf_interim_advances value = 0 }'))

# One small weekly check for the nine offices. It does not sweep cash, award
# projects or bypass payment holds. A due-date lease prevents duplicate runs.
write(cash,read(cash)+r'''
mam_revenue_fund_ensure_payroll_effect = {
 if = { limit = { mam_revenue_emperor_trigger = yes mam_revenue_fund_enabled_trigger = yes }
  save_scope_as = mam_cf_payroll_sovereign
  save_scope_value_as = { name = mam_cf_schedule_payroll value = 0 }
  title:h_china = {
   if = { limit = { NOT = { has_variable = mam_cf_interim_advances } }
    set_variable = { name = mam_cf_interim_advances value = 0 }
   }
   if = { limit = { NOT = { has_variable = mam_cf_payroll_due } }
    save_scope_value_as = { name = mam_cf_schedule_payroll value = 1 }
   }
   else_if = { limit = { NOT = { has_variable = mam_cf_payroll_owner } }
    save_scope_value_as = { name = mam_cf_schedule_payroll value = 1 }
   }
   else_if = { limit = { var:mam_cf_payroll_due < current_date }
    save_scope_value_as = { name = mam_cf_schedule_payroll value = 1 }
   }
   else_if = { limit = { var:mam_cf_payroll_owner != scope:mam_cf_payroll_sovereign }
    save_scope_value_as = { name = mam_cf_schedule_payroll value = 1 }
   }
  }
  if = { limit = { scope:mam_cf_schedule_payroll = 1 }
   title:h_china = {
    set_variable = { name = mam_cf_payroll_due value = { value = current_date add = 1 } }
    set_variable = { name = mam_cf_payroll_owner value = scope:mam_cf_payroll_sovereign }
   }
   trigger_event = { id = mam_fund.95 days = 1 }
  }
 }
}
mam_revenue_fund_payroll_effect = {
 if = { limit = { mam_revenue_emperor_trigger = yes mam_revenue_fund_enabled_trigger = yes
  title:h_china = { has_variable = mam_cf_payroll_due var:mam_cf_payroll_due <= current_date }
 }
  save_scope_as = mam_cf_payroll_sovereign
  if = { limit = { mam_revenue_fund_ready_trigger = yes }
'''+roster('mam_revenue_fund_init_office_effect = yes')+r'''
   title:h_china = {
    set_variable = { name = mam_cf_essential_due value = 0 }
    set_variable = { name = mam_cf_essential_cash value = { value = title:e_minister_of_revenue.holder.treasury
     subtract = title:e_minister_of_revenue.mam_revenue_fund_cash_target min = 0 } }
   }
'''+roster('mam_revenue_fund_count_essential_effect = yes')+'\n'+roster('mam_revenue_fund_refill_effect = { EXTRA = no }')+r'''
   mam_revenue_fund_refresh_totals_effect = yes
  }
  title:h_china = {
   set_variable = { name = mam_cf_payroll_due value = { value = current_date add = 7 } }
   set_variable = { name = mam_cf_payroll_owner value = scope:mam_cf_payroll_sovereign }
  }
  trigger_event = { id = mam_fund.95 days = 7 }
 }
}
''')
choices='common/scripted_effects/mam_revenue_common_choice_effects.txt'
write(choices,read(choices).replace('var:mam_cf_cost multiply = 3 add = var:mam_cf_headroom subtract = var:mam_cf_issued','var:mam_cf_headroom subtract = var:mam_cf_issued').replace('# Newly observed commitments become protected only through this approval.','# Approval records reported commitments and sets discretionary headroom.'))
events='events/mam_revenue_common_events.txt'
write(events,read(events)+'\nmam_fund.95 = { type = character_event hidden = yes immediate = { mam_revenue_fund_payroll_effect = yes } }\n')

# One project proposal per monthly initiative, instead of one random ministry
# every quarter. Native project eligibility and the approval queue still apply.
initiative='common/scripted_effects/mam_revenue_common_initiative_effects.txt'
s=read(initiative);top=next(n for n in parse(s) if n.key=='mam_revenue_fund_initiative_effect')
proposal=next(n for n in top.walk() if n.key=='random_vassal_or_below' and 'id = mam_fund.96' in s[n.start:n.end])
code=s[proposal.start:proposal.end].replace('NOT = { has_trait = lazy }','''NOT = { has_trait = lazy }
   primary_title = { NOT = { has_variable = mam_cf_return_pending }
    trigger_if = { limit = { has_variable = mam_cf_next_project_request } var:mam_cf_next_project_request <= current_date }
   }''').replace('has_title = title:e_minister_of_works has_title = title:e_minister_of_rites','has_title = title:e_minister_grand_marshal has_title = title:e_minister_of_works has_title = title:e_minister_of_rites')
s=s[:proposal.start]+s[proposal.end:];write(initiative,s)
edit(initiative,'mam_revenue_fund_initiative_effect',lambda s:s[:-1]+'\n # Fund one eligible project proposal each monthly review.\n'+code+'\n}')

# Native Works gives a financial-readiness bonus at 20,000 treasury. A matching
# paid grant supplies the same bonus without requiring a private 20,000 hoard.
# Insert before native trait/culture/war multipliers, so their zeroes still win.
manifest_path='docs/COMMON-FUND-NATIVE-PROJECTS.json'
manifest=json.loads(read(manifest_path));name='minister_project_development';entry=manifest['definitions'][name]
native=Path(entry['native_source']).read_text(encoding='utf-8-sig');node=next(n for n in parse(native) if n.key==name)
ai=next(n for n in node.children if n.key=='ai_will_do');base=next(n for n in ai.children if n.key=='value')
bonus='''
 # MAM COMMON FUND: a paid matching project grant satisfies financial readiness.
 if = { limit = { mam_revenue_fund_member_trigger = yes treasury < 20000
  mam_revenue_fund_project_start_trigger = { TYPE = 3 COST = mam_revenue_fund_start_cost_3 }
 } add = 70 }
'''
entry['insertions'].append({'at':base.end-node.start,'text':bonus})
original=native[node.start:node.end]
for item in sorted(entry['insertions'],key=lambda e:(e['at'],e['text']),reverse=True):
 at=item['at'];original=original[:at]+item['text']+original[at:]
for p in (ROOT/'common/great_projects/types').glob('zz_mam_revenue_common_*.txt'):
 source=p.read_text(encoding='utf-8-sig');match=next((n for n in parse(source) if n.key==name),None)
 if match:write(str(p.relative_to(ROOT)),source[:match.start]+original+source[match.end:]);break
write(manifest_path,json.dumps(manifest,indent=2))

locpath='localization/english/mam_revenue_common_l_english.yml';loc={}
for line in read(locpath).splitlines()[1:]:
 m=re.fullmatch(r' ([\w.]+):0 (".*")',line)
 if m:loc[m[1]]=json.loads(m[2])
for key in ['mam_cf.lean_tt','mam_cf.standard_tt','mam_cf.expanded_tt']:
 loc[key]+=' Standing native expenses receive separate automatic provision; the quarterly cap applies only to discretionary advances.'
loc['mam_cf.own_desc']=loc['mam_cf.own_desc'].replace('approved operating target','working target').replace('ordinary advances this quarter','discretionary advances this quarter')
loc['mam_cf.departments_all']=loc['mam_cf.departments_all'].replace('approved operating target','working target').replace('Targets exclude project earmarks.','Targets cover two months of approved or currently observed recurring costs, whichever is greater, plus headroom. Project earmarks are separate.')
loc['mam_cf.accounts_tt']+=' Essential cash needs are checked weekly. A depleted discretionary allowance does not stop recurring payroll; unverified payments still stop releases.'
loc['mam_cf.operations_desc']+=' Existing native bills remain covered while the discretionary provision is reviewed.'
loc['mam_cf.flow_desc']+=' Essential operating shortfalls are also checked weekly, without a new approval popup.'
loc['mam_cf.statement_done']+=" Additional essential advances since that settlement: #high [GetTitleByKey('h_china').MakeScope.Var('mam_cf_interim_advances').GetValue|0]#! [treasury_i]."
loc['mam_cf.refresh_accounts_tt']+=' Current cash may include weekly essential advances made after that settlement.'
write(locpath,'l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items()))
p=ROOT/'descriptor.mod';p.write_text(re.sub(r'version="[^"]+"','version="0.4.0-alpha.20-dev.52"',p.read_text(),count=1),encoding='utf-8')
print('Applied dev.52 essential-payroll and funded-project readiness fixes.')
