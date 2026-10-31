"""Project-scoped contribution envelopes, native invoices and campaign launch.

Run after dev.54. Native sources are read-only. Templates are the authored
runtime; the native eligibility/price bridge is generated and hash-audited.
"""
from pathlib import Path
import hashlib,json,re,runpy
ROOT=Path(__file__).resolve().parents[1]
parse=runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']
ROSTER=['e_minister_chancellor','e_minister_censor','e_minister_grand_marshal',
 'e_minister_of_personnel','e_minister_of_war','e_minister_of_rites',
 'e_minister_of_works','e_minister_of_revenue','e_minister_of_justice']
def read(rel):return (ROOT/rel).read_text(encoding='utf-8-sig')
def write(rel,s):
 p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(s.rstrip()+'\n',encoding='utf-8-sig' if p.suffix in {'.txt','.yml'} else 'utf-8')
def edit(rel,key,fn):
 s=read(rel);n=next(n for n in parse(s) if n.key==key)
 write(rel,s[:n.start]+fn(s[n.start:n.end])+s[n.end:])
def append(rel,s):write(rel,read(rel)+'\n'+s)
def body(s,n):return s[s.index('{',n.start)+1:n.end-1]

manifest_path='docs/COMMON-FUND-NATIVE-PROJECTS.json'
manifest=json.loads(read(manifest_path)); native_cache={}; invoices=[]; elig=[]; weights=[]; binder=[]
registry_path='docs/COMMON-FUND-CONTRIBUTION-KEYS.json'
registry=json.loads(read(registry_path)) if (ROOT/registry_path).exists() else {}
for cost_key,entry in manifest['contribution_costs'].items():
 project=entry['project'];slot=entry['contribution'];sourcefile=manifest['definitions'][project]['native_source']
 identity=project+'::'+slot
 if identity not in registry:registry[identity]=max(registry.values(),default=0)+1
 number=registry[identity]
 s=native_cache.setdefault(sourcefile,Path(sourcefile).read_text(encoding='utf-8-sig'))
 native=next(n for n in parse(s) if n.key==project)
 contributions=next(n for n in native.children if n.key=='project_contributions')
 contribution=next(n for n in contributions.children if n.key==slot)
 clauses=[]
 for c in contribution.children:
  if c.key in {'is_shown','contributor_is_valid'}:clauses.append(body(s,c))
 # Direct root references must still name the actual contributor when scanned
 # through a realm/project iterator. Native helper calls run in a member event.
 conditions=re.sub(r'\broot\b','scope:mam_cf_contributor','\n'.join(clauses))
 elig.append(f'mam_revenue_fund_invoice_eligible_{number}_trigger = {{\n{conditions}\n}}')
 ai=next((n for n in contribution.children if n.key=='ai_will_do'),None)
 weights.append(f'mam_revenue_fund_invoice_weight_{number} = {{\n'+(body(s,ai) if ai else 'value = 1')+'\n}')
 binder.append(f'''{'if' if not binder else 'else_if'} = {{ limit = {{
 scope:great_project = {{ great_project_type = {project} }}
 scope:mam_cf_contribution = {{ contribution_id = {slot} }}
 }}
 save_scope_value_as = {{ name = mam_cf_invoice_key value = {number} }}
 save_scope_value_as = {{ name = mam_cf_invoice_price value = {cost_key} }}
 save_scope_value_as = {{ name = mam_cf_invoice_weight value = mam_revenue_fund_invoice_weight_{number} }}
 if = {{ limit = {{ mam_revenue_fund_invoice_eligible_{number}_trigger = yes }}
  save_scope_value_as = {{ name = mam_cf_invoice_eligible value = 1 }}
 }}
}}''')
 invoices.append({'key':number,'project':project,'slot':slot,'price':cost_key,
  'native_source':sourcefile,'native_eligibility':conditions,
  'native_contribution_sha256':hashlib.sha256(s[contribution.start:contribution.end].encode()).hexdigest()})

assert max(registry.values())<100000, 'Increase the menu sentinel through an explicit saved-key migration.'
write(registry_path,json.dumps(registry,indent=2))
write('common/scripted_triggers/mam_revenue_common_invoice_eligibility.txt','\n\n'.join(elig))
write('common/script_values/mam_revenue_common_invoice_weights.txt','\n\n'.join(weights))
write('common/scripted_effects/mam_revenue_common_invoice_bindings.txt',r'''
# Character scope; great_project and mam_cf_contribution are bound by the caller.
mam_revenue_fund_bind_invoice_effect = {
 save_scope_as = mam_cf_contributor
 save_scope_value_as = { name = mam_cf_invoice_key value = 0 }
 save_scope_value_as = { name = mam_cf_invoice_price value = 0 }
 save_scope_value_as = { name = mam_cf_invoice_weight value = 0 }
 save_scope_value_as = { name = mam_cf_invoice_eligible value = 0 }
'''+ '\n'.join(binder)+'\n}')
write('docs/COMMON-FUND-CONTRIBUTIONS-MANIFEST.json',json.dumps({'build':'dev.55','invoices':invoices},indent=2))

for name in ['triggers','effects','events','interactions']:
 destination={'triggers':'common/scripted_triggers/mam_revenue_common_project_orders.txt',
  'effects':'common/scripted_effects/mam_revenue_common_project_orders.txt',
  'events':'events/mam_revenue_common_project_orders.txt',
  'interactions':'common/character_interactions/mam_revenue_common_project_orders.txt'}[name]
 template=read('tools/templates/revenue_projects_'+name+'.txt')
 dispatch='\n'.join(f'title:{t}.holder ?= {{ if = {{ limit = {{ mam_revenue_ministry_trigger = yes }} trigger_event = {{ id = mam_fund.31 days = 1 }} }} }}' for t in ROSTER)
 if name=='effects':
  menu=[]
  for label in ['one','two','three']:
   previous={'one':None,'two':'one','three':'two'}[label]
   lower='var:mam_pc_menu_offset' if previous is None else 'scope:mam_cf_menu_key_'+previous
   menu.append(f'''save_scope_value_as = {{ name = mam_cf_menu_key_{label} value = 100000 }}
scope:mam_cf_selected_project = {{ every_contribution = {{ limit = {{ contribution_is_funded = no }}
 save_scope_as = mam_cf_contribution save_scope_as = contribution
 scope:mam_cf_contributor = {{
  mam_revenue_fund_bind_invoice_effect = yes
  if = {{ limit = {{ scope:mam_cf_invoice_eligible = 1 scope:mam_cf_invoice_price > 0
   scope:mam_cf_invoice_key > {lower} scope:mam_cf_invoice_key < scope:mam_cf_menu_key_{label} }}
   scope:mam_cf_contribution = {{ save_scope_as = mam_cf_menu_slot_{label} }}
   save_scope_value_as = {{ name = mam_cf_menu_key_{label} value = scope:mam_cf_invoice_key }}
   save_scope_value_as = {{ name = mam_cf_menu_price_{label} value = scope:mam_cf_invoice_price }}
  }}
 }}
}} }}''')
  template=template.replace('@BUILD_INVOICE_PICKER@','\n'.join(menu))
 returns='\n'.join(f'title:{t} = {{ if = {{ limit = {{ has_variable = mam_pc_mobilization_project var:mam_pc_mobilization_project = scope:mam_cf_closed_project }} mam_revenue_fund_return_mobilization_effect = yes }} }}' for t in ROSTER)
 write(destination,template.replace('@DISPATCH_MEMBERS@',dispatch).replace('@RETURN_MOBILIZATION@',returns))

write('common/story_cycles/mam_revenue_common_invoice_receipt_story.txt',r'''
# Passive financial receipts, not a Censor/Justice case system.
mam_revenue_project_receipt_story = {
 visible = no on_setup = { }
 on_owner_death = {
  clear_saved_scope = mam_cf_receipt_heir
  title:h_china.holder ?= { if = { limit = { is_alive = yes } save_scope_as = mam_cf_receipt_heir } }
  if = { limit = { NOT = { exists = scope:mam_cf_receipt_heir } }
   title:h_china.current_heir ?= { if = { limit = { is_alive = yes } save_scope_as = mam_cf_receipt_heir } }
  }
  if = { limit = { exists = scope:mam_cf_receipt_heir } make_story_owner = scope:mam_cf_receipt_heir }
 }
 effect_group = { days = 90 triggered_effect = { trigger = { always = yes } effect = {
  if = { limit = { has_variable = mam_pc_date var:mam_pc_date <= { value = current_date subtract = 1825 } }
   save_scope_as = mam_cf_old_receipt
   title:h_china = { remove_list_variable = { name = mam_pc_receipts target = scope:mam_cf_old_receipt } }
   end_story = yes
  }
 } } }
}
''')

# Project-aware access token preserves native rules and retained paid legacy
# allowances. A project envelope alone never enables an unfinanced native click.
triggers='common/scripted_triggers/mam_revenue_common_triggers.txt'
edit(triggers,'mam_revenue_fund_contribution_trigger',lambda s:r'''mam_revenue_fund_contribution_trigger = {
 save_temporary_scope_value_as = { name = mam_cf_required_contribution_cost value = $COST$ }
 exists = scope:great_project
 primary_title = {
  NOT = { has_variable = mam_cf_payment_hold }
  OR = {
   AND = { has_variable = mam_pc_executing_project
    var:mam_pc_executing_project = scope:great_project }
   AND = { var:mam_cf_project_instance = scope:great_project
    var:mam_cf_project_until > current_date
    var:mam_cf_project_cash >= scope:mam_cf_required_contribution_cost }
  }
 }
 trigger_if = { limit = { scope:great_project = { great_project_type = grand_campaign_project } }
  scope:great_project = { OR = {
   var:mam_pc_launch_authorized = 1
   any_contribution = { contribution_id = attack_1 contribution_is_funded = yes }
  } }
 }
}''')
# K13 is a project envelope, not a one-per-office cash payment.
edit(triggers,'mam_revenue_fund_live_case_trigger',lambda s:s[:-1]+r'''
 trigger_if = { limit = { var:mam_cf_kind = 13 }
  var:mam_cf_requester = { is_alive = yes mam_revenue_ministry_trigger = yes }
  var:mam_pc_request_office.holder = var:mam_cf_requester
  exists = var:mam_cf_project_instance
  var:mam_cf_project_instance = { great_project_owner = title:h_china.holder NOT = { has_variable = mam_pc_closed } }
 }
}''')
edit(triggers,'mam_revenue_fund_delegated_trigger',lambda s:s.replace('var:mam_cf_kind = 3 var:mam_cf_kind = 9','var:mam_cf_kind = 3 var:mam_cf_kind = 9 var:mam_cf_kind = 13')[:-1]+r'''
 trigger_if = { limit = { var:mam_cf_kind = 13 }
  var:mam_cf_project_instance = {
   var:mam_pc_spent <= { value = 500 subtract = scope:mam_cf_quote }
  }
 }
}''')
# Use the file amount, not a stale UI quote, inside the story authority trigger.
edit(triggers,'mam_revenue_fund_delegated_trigger',lambda s:s.replace('scope:mam_cf_quote','prev.var:mam_cf_amount'))

queue='common/scripted_effects/mam_revenue_common_queue_effects.txt'
edit(queue,'mam_revenue_fund_close_effect',lambda s:s[:-1]+r'''
 if = { limit = { var:mam_cf_kind = 13 exists = var:mam_cf_project_instance }
  save_scope_as = mam_cf_closed_budget
  var:mam_cf_project_instance = {
   if = { limit = { var:mam_pc_pending = scope:mam_cf_closed_budget } remove_variable = mam_pc_pending }
   if = { limit = { scope:mam_cf_closed_budget.var:mam_cf_result != 1 }
    set_variable = { name = mam_pc_retry_after value = { value = current_date add = 30 } }
   }
  }
 }
}''')
edit(queue,'mam_revenue_fund_bind_effect',lambda s:s[:-1]+r'''
 save_scope_value_as = { name = mam_cf_mobilization value = 0 }
 if = { limit = { scope:mam_cf_file = { has_variable = mam_pc_mobilization_quote } }
  save_scope_value_as = { name = mam_cf_mobilization value = scope:mam_cf_file.var:mam_pc_mobilization_quote }
 }
 if = { limit = { scope:mam_cf_file.var:mam_cf_kind = 13 exists = scope:mam_cf_selected_project }
  scope:mam_cf_file.var:mam_cf_requester = { save_scope_as = mam_cf_subject }
  scope:mam_cf_file.var:mam_pc_request_office = { save_scope_as = mam_cf_title }
  save_scope_value_as = { name = mam_cf_max value = {
   value = scope:mam_cf_free add = scope:mam_cf_selected_project.var:mam_pc_budget
  } }
 }
}''')
edit(queue,'mam_revenue_fund_show_request_effect',lambda s:s.replace(
 'scope:mam_cf_file.var:mam_cf_stage = 0','OR = { scope:mam_cf_file.var:mam_cf_stage = 0 scope:mam_cf_file.var:mam_cf_kind = 13 }'))

choices='common/scripted_effects/mam_revenue_common_choice_effects.txt'
# Keep the old commit as a compatibility branch, guarded by the new dispatcher.
s=read(choices);node=next(n for n in parse(s) if n.key=='mam_revenue_fund_commit_effect')
original=s[node.start:node.end].replace('mam_revenue_fund_commit_effect = {','mam_revenue_fund_legacy_commit_effect = {',1)
write(choices,s[:node.start]+original+s[node.end:])
append(choices,r'''
mam_revenue_fund_commit_effect = {
 if = { limit = { var:mam_cf_kind = 13 } mam_revenue_fund_commit_project_budget_effect = yes }
 else = { mam_revenue_fund_legacy_commit_effect = yes }
}
''')
edit(choices,'mam_revenue_fund_legacy_commit_effect',lambda s:s.replace(
 'add = title:h_china.var:mam_cf_reserve add = title:h_china.var:mam_cf_unfunded',
 'add = title:h_china.var:mam_cf_reserve add = title:h_china.var:mam_cf_unfunded add = title:h_china.var:mam_pc_commitments'))
edit(choices,'mam_revenue_fund_notify_effect',lambda s:s.replace(
 'is_alive = yes is_ai = no this != scope:mam_cf_outcome.var:mam_cf_requester',
 'is_alive = yes is_ai = no this != scope:mam_cf_outcome.var:mam_cf_requester scope:mam_cf_outcome.var:mam_cf_kind != 13'))
preview='common/scripted_effects/mam_revenue_common_preview_effects.txt'
edit(preview,'mam_revenue_fund_preview_effect',lambda s: 'mam_revenue_fund_preview_effect = {\n if = { limit = { scope:mam_cf_file.var:mam_cf_kind = 13 } custom_tooltip = mam_pc.reserve_budget_tt }\n else = {\n'+body(s,parse(s)[0])+'\n}\n}')

cash='common/scripted_effects/mam_revenue_common_cash_effects.txt'
edit(cash,'mam_revenue_fund_refresh_totals_effect',lambda s:s[:-1]+'\n mam_revenue_fund_refresh_project_commitments_effect = yes\n}')
edit(cash,'mam_revenue_fund_payroll_effect',lambda s:s.replace('mam_revenue_fund_refresh_totals_effect = yes','mam_revenue_fund_refresh_totals_effect = yes\n mam_revenue_fund_project_driver_effect = yes',1))
edit(cash,'mam_revenue_fund_start_effect',lambda s:s[:-1]+'\n mam_revenue_fund_project_driver_effect = yes\n}')
edit(cash,'mam_revenue_fund_init_office_effect',lambda s:s[:-1]+r'''
 if = { limit = { has_variable = mam_pc_mobilization_until var:mam_pc_mobilization_until <= current_date }
  mam_revenue_fund_return_mobilization_effect = yes
 }
 if = { limit = { has_variable = mam_pc_mobilization_project NOT = { exists = var:mam_pc_mobilization_project } }
  mam_revenue_fund_return_mobilization_effect = yes
 }
}''')
values='common/script_values/mam_revenue_common_values.txt'
edit(values,'mam_revenue_fund_available',lambda s:s.replace('subtract = title:h_china.var:mam_cf_unfunded','subtract = title:h_china.var:mam_cf_unfunded subtract = title:h_china.var:mam_pc_commitments'))
edit(values,'mam_revenue_fund_target',lambda s:s[:-1]+r'''
 if = { limit = { has_variable = mam_pc_mobilization_until var:mam_pc_mobilization_until > current_date }
  add = var:mam_pc_mobilization_amount
 }
}''')
edit(values,'mam_revenue_fund_queue_score',lambda s:s[:-1]+r'''
 if = { limit = { has_variable = mam_pc_required_invoice } add = 1000000 }
 if = { limit = { has_variable = mam_pc_campaign_launch } add = 3000000 }
}''')

# Retire only the old contribution allowance entry. Unstarted project grants,
# old pending case kinds and their save identifiers remain intact.
initiative='common/scripted_effects/mam_revenue_common_initiative_effects.txt'
edit(initiative,'mam_revenue_fund_open_contribution_effect',lambda s:r'''
mam_revenue_fund_open_contribution_effect = {
 set_variable = { name = mam_pc_menu_offset value = 0 }
 mam_revenue_fund_choose_invoice_effect = yes
}
''')
decisions='common/decisions/mam_revenue_common_decisions.txt'
edit(decisions,'mam_revenue_fund_contribution_decision',lambda s:r'''
mam_revenue_fund_contribution_decision = {
 decision_group_type = mam_ministries ai_check_interval = 0
 picture = { reference = "gfx/interface/illustrations/event_scenes/tgp_study_asia.dds" }
 desc = mam_revenue_fund_contribution_decision_desc selection_tooltip = mam_revenue_fund_contribution_decision_desc confirm_text = mam_cf.open
 is_shown = { is_ai = no mam_revenue_fund_enabled_trigger = yes mam_revenue_ministry_trigger = yes
  any_great_project = { great_project_owner = title:h_china.holder } }
 is_valid = { custom_tooltip = { text = mam_cf.ready_tt mam_revenue_fund_ready_trigger = yes } }
 effect = { mam_revenue_fund_reset_project_menu_effect = yes trigger_event = mam_fund.7 }
 ai_potential = { always = no } ai_will_do = { base = 0 }
}
''')

# Native callbacks now distinguish the shared invoice executor from legacy paid
# office grants. Native costs, eligibility, rewards and government participation
# remain unchanged outside these explicit insertions.
for name,entry in manifest['definitions'].items():
 for insertion in entry['insertions']:
  text=insertion['text']
  match=re.search(r'name = mam_cf_native_cost value = (mam_revenue_fund_contribution_cost_\w+)',text)
  if match and 'name = mam_cf_project_cash subtract = scope:mam_cf_native_cost' in text:
   receipt='\n# MAM COMMON FUND native contribution receipt\nhidden_effect = {\nif = { limit = { mam_revenue_fund_member_trigger = yes }\n mam_revenue_fund_native_invoice_receipt_effect = { COST = '+match[1]+' }\n}\n}\n'
   # If vanilla has no callback, the base insertion owns its wrapper. Preserve
   # it rather than putting an illegal bare effect in a contribution database.
   insertion['text']=('on_contribution_funded = {\n'+receipt+'}\n') if 'on_contribution_funded = {' in text else receipt
 source=Path(entry['native_source']).read_text(encoding='utf-8-sig');n=next(n for n in parse(source) if n.key==name)
 for callback in ['on_cancel','on_complete']:
  original_callback=next((c for c in n.children if c.key==callback),None)
  if original_callback:entry['insertions'].append({'at':original_callback.end-1-n.start,'text':'\n# MAM project envelope closure\nhidden_effect = { mam_revenue_fund_project_order_closed_effect = yes }\n'})
  else:
   existing=next((e for e in entry['insertions'] if callback+' = {' in e['text']),None)
   assert existing, 'The base generator must supply the absent lifecycle callback.'
   closing=existing['text'].rfind('}')
   existing['text']=existing['text'][:closing]+'\n hidden_effect = { mam_revenue_fund_project_order_closed_effect = yes }\n'+existing['text'][closing:]
 changed=source[n.start:n.end]
 for item in sorted(entry['insertions'],key=lambda e:(e['at'],e['text']),reverse=True):
  at=item['at'];changed=changed[:at]+item['text']+changed[at:]
 for p in (ROOT/'common/great_projects/types').glob('zz_mam_revenue_common_*.txt'):
  text=p.read_text(encoding='utf-8-sig');existing=next((n for n in parse(text) if n.key==name),None)
  if existing:write(str(p.relative_to(ROOT)),text[:existing.start]+changed+text[existing.end:]);break
write(manifest_path,json.dumps(manifest,indent=2))

events='events/mam_revenue_common_events.txt'
for event in ['mam_fund.1','mam_fund.8']:
 edit(events,event,lambda s:s.replace('desc = { first_valid = {','desc = { first_valid = {\n triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_kind = 13 scope:mam_cf_file = { has_variable = mam_pc_campaign_launch } } desc = mam_pc.campaign_request_desc }\n triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_kind = 13 } desc = mam_pc.budget_request_desc }',1))
 def minimum_gate(s):
  changes=[]
  for option in (n for n in parse(s)[0].children if n.key=='option'):
   if any(c.key=='name' and c.value in {'mam_cf.recommend','mam_cf.approve'} for c in option.children):
    gate=next(c for c in option.children if c.key=='trigger')
    changes.append(gate.end-1)
  for at in sorted(changes,reverse=True):s=s[:at]+'\n trigger_if = { limit = { scope:mam_cf_file.var:mam_cf_kind = 13 } scope:mam_cf_quote >= scope:mam_cf_file.var:mam_pc_minimum }\n'+s[at:]
  return s
 edit(events,event,minimum_gate)
edit(events,'mam_fund.20',lambda s:s.replace('desc = { first_valid = {','desc = { first_valid = {\n triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_kind = 13 scope:mam_cf_file.var:mam_cf_result = 1 } desc = mam_pc.budget_approved_desc }',1))
local='localization/english/mam_revenue_common_l_english.yml';loc={}
for line in read(local).splitlines()[1:]:
 m=re.fullmatch(r' ([\w.]+):0 (".*")',line)
 if m:loc[m[1]]=json.loads(m[2])
loc.update(json.loads(read('tools/templates/revenue_projects_localization.json')))
loc['mam_revenue_fund_contribution_decision']='Revenue: Contribute to an Imperial Project'
loc['mam_revenue_fund_contribution_decision_desc']='Choose an existing project and an eligible contribution. Approved project budgets finance the native contribution automatically; uncovered costs request lawful approval. Required contributions do not wait for the new-project cooldown.'
loc['mam_cf.contribution_choose_desc']='Which imperial project shall my office support? Choose a project to review its eligible contribution. Funding and native execution follow the same order.'
loc['mam_cf.contribution_authorization_tt']='Use Revenue: Contribute to an Imperial Project to request and execute a funded pledge. The system preserves the native contributor and price; required continuation does not wait for the new-project cooldown.'
write(local,'l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items()))
p=ROOT/'descriptor.mod';p.write_text(re.sub(r'version="[^"]+"','version="0.4.0-alpha.20-dev.55"',p.read_text(),count=1),encoding='utf-8')
print('Applied dev.55 project-scoped contributions, campaign finance and native invoice bridge.')
