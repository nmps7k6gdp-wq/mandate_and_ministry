"""Native callback repairs and an explicit funded-AI planning continuation.

Run through build_common_fund.py. Vanilla is read only; generated location
predicates retain native conditions. This does not waive native costs or wars.
"""
from pathlib import Path
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']


def read(rel):
    return (ROOT/rel).read_text(encoding='utf-8-sig')


def write(rel,text):
    (ROOT/rel).write_text(text.rstrip()+'\n',encoding='utf-8-sig' if Path(rel).suffix in {'.txt','.yml'} else 'utf-8')


def edit(rel,key,fn):
    text=read(rel);node=next(n for n in parse(text) if n.key==key)
    write(rel,text[:node.start]+fn(text[node.start:node.end])+text[node.end:])


def body(text,key):
    n=next(n for n in parse(text) if n.key==key)
    return text[text.index('{',n.start)+1:n.end-1]


# A temporary target cannot reuse an existing permanent event target name.
# Expand the read-only coverage predicates with distinct story references.
triggers='common/scripted_triggers/mam_revenue_common_project_orders.txt'
text=read(triggers)
authority=body(text,'mam_revenue_fund_project_budget_authority_trigger')
sufficient=body(text,'mam_revenue_fund_invoice_budget_sufficient_trigger').replace(
    'mam_revenue_fund_project_budget_authority_trigger = yes', authority)
sufficient=sufficient.replace('scope:mam_cf_selected_project','scope:mam_cf_coverage_file.var:mam_cf_project_instance')
sufficient=sufficient.replace('scope:mam_cf_invoice_price','scope:mam_cf_coverage_file.var:mam_pc_minimum')
edit(triggers,'mam_revenue_fund_project_request_covered_trigger',lambda s:'''mam_revenue_fund_project_request_covered_trigger = {
 var:mam_cf_kind = 13 exists = var:mam_cf_project_instance
 exists = var:mam_cf_requester has_variable = mam_pc_minimum
 save_temporary_scope_as = mam_cf_coverage_file
 var:mam_cf_requester = {
'''+sufficient+'\n}\n}')

# Tooltip traversal does not execute set_variable. Check existence in story
# scope before reading the result; project scope has no such result variable.
queue='common/scripted_effects/mam_revenue_common_queue_effects.txt'
def close_repair(s):
    s=s.replace('''   if = { limit = { scope:mam_cf_closed_budget.var:mam_cf_result != 1 }
    set_variable = { name = mam_pc_retry_after value = { value = current_date add = 30 } }
   }''','')
    marker='''  var:mam_cf_project_instance = {
   if = { limit = { var:mam_pc_pending = scope:mam_cf_closed_budget } remove_variable = mam_pc_pending }'''
    return s.replace(marker,'''  if = { limit = { has_variable = mam_cf_result var:mam_cf_result != 1 }
   var:mam_cf_project_instance = { set_variable = { name = mam_pc_retry_after value = { value = current_date add = 30 } } }
  }
'''+marker)
edit(queue,'mam_revenue_fund_close_effect',close_repair)

# Campaign planning needs an exterior border location, not a county inside the
# granted province. The later pledge still requires its imperial launch order.
location='common/scripted_triggers/mam_revenue_common_triggers.txt'
edit(location,'mam_revenue_fund_project_location_trigger',lambda s:s.replace(
    'trigger_if = { limit = { var:mam_cf_project_type = 9 }', '''trigger_if = { limit = { var:mam_cf_project_type = 1 }
   exists = var:mam_cf_project_target.holder
   save_temporary_scope_as = mam_cf_border_office
   scope:province.county = {
    exists = holder holder.top_liege != title:h_china.holder
    any_neighboring_county = { holder = {
     OR = { this = scope:mam_cf_border_office.var:mam_cf_project_target.holder
      is_vassal_or_below_of = scope:mam_cf_border_office.var:mam_cf_project_target.holder }
    } }
   }
  }
  trigger_else_if = { limit = { var:mam_cf_project_type = 9 }''',1))

manifest=json.loads(read('docs/COMMON-FUND-NATIVE-PROJECTS.json'))
locations=[];branches=[];audit=[];preflight=[]
for name,entry in manifest['definitions'].items():
    index=None
    for insertion in entry['insertions']:
        match=re.search(r'TYPE = (\d+) COST = mam_revenue_fund_start_cost',insertion['text'])
        if match:index=int(match[1]);break
    if index is None:continue
    source=Path(entry['native_source']).read_text(encoding='utf-8-sig')
    node=next(n for n in parse(source) if n.key==name)
    native_location=next((n for n in node.children if n.key=='is_location_valid'),None)
    conditions=source[source.index('{',native_location.start)+1:native_location.end-1] if native_location else ''
    filt=next((n.value for n in node.children if n.key=='province_filter'),None)
    target=next((n.value for n in node.children if n.key=='province_filter_target'),None)
    if filt=='geographical_region':
        assert target
        conditions+='\nscope:province = { geographical_region = '+target+' }\n'
    locations.append(f'mam_revenue_fund_native_start_location_{index}_trigger = {{\n'+conditions+'\n}')
    candidate=f'''if = {{ limit = {{ NOT = {{ exists = scope:mam_cf_start_site }} has_holding = yes }}
 save_scope_as = province
 scope:mam_cf_start_actor = {{
  if = {{ limit = {{ mam_revenue_fund_native_start_location_{index}_trigger = yes mam_revenue_fund_project_location_trigger = yes }}
   scope:province = {{ save_scope_as = mam_cf_start_site }}
  }}
 }}
}}'''
    if filt=='top_liege_border_outer':
        search='''scope:mam_cf_start_target.holder = { every_sub_realm_county = {
 every_neighboring_county = { limit = { exists = holder holder.top_liege != title:h_china.holder }
 title_province = { '''+candidate+''' }
 }
} }'''
    elif filt is None:
        # Native global/capital projects have no selectable province filter.
        search='title:h_china.holder.capital_province = { '+candidate+' }'
    else:
        search='''scope:mam_cf_start_target.holder = { every_sub_realm_county = {
 every_county_province = { '''+candidate+''' }
} }'''
    preflight.append(f'''save_scope_value_as = {{ name = mam_cf_start_choice_{index} value = 0 }}
 clear_saved_scope = mam_cf_start_site
 if = {{ limit = {{ mam_revenue_fund_eligible_project_{index} = yes }}
 {search.replace(' mam_revenue_fund_project_location_trigger = yes','')}
 if = {{ limit = {{ exists = scope:mam_cf_start_site }}
  save_scope_value_as = {{ name = mam_cf_start_choice_{index} value = 1 }}
 }}
 }}''')
    branches.append(f'''{'if' if not branches else 'else_if'} = {{ limit = {{ primary_title.var:mam_cf_project_type = {index}
 mam_revenue_fund_eligible_project_{index} = yes
 can_plan_great_project = great_project_type:{name}
 treasury >= mam_revenue_fund_start_cost_{index}
 }}
 {search}
 if = {{ limit = {{ exists = scope:mam_cf_start_site }}
  save_scope_value_as = {{ name = mam_cf_start_before value = treasury }}
  save_scope_value_as = {{ name = mam_cf_start_price value = mam_revenue_fund_start_cost_{index} }}
  scope:mam_cf_start_site = {{ plan_great_project = {{
   founder = scope:mam_cf_start_actor great_project_type = {name} save_scope_as = mam_cf_auto_project
  }} }}
  mam_revenue_fund_check_auto_start_effect = yes
 }}
}}''')
    audit.append({'type':index,'project':name,'native_source':entry['native_source'],
                  'province_filter':filt,'filter_target':target,'native_location':conditions})
write('common/scripted_triggers/mam_revenue_common_start_locations.txt','\n\n'.join(locations))
write('docs/COMMON-FUND-AI-START-MANIFEST.json',json.dumps({'build':'dev.57','projects':audit},indent=2))
write('common/scripted_effects/mam_revenue_common_auto_start.txt',r'''
# AI proposals should not lock funds to a province with no eligible site.
mam_revenue_fund_preflight_project_choices_effect = {
 if = { limit = { is_ai = yes exists = scope:mam_cf_site_title.holder }
  save_scope_as = mam_cf_start_actor save_scope_as = founder
  title:h_china.holder = { save_scope_as = owner }
  scope:mam_cf_site_title = { save_scope_as = mam_cf_start_target }
'''+ '\n'.join(preflight)+r'''
  clear_saved_scope = mam_cf_start_site
 }
}
# Character-root continuation: an existing paid grant, never another payment.
mam_revenue_fund_auto_start_effect = {
 if = { limit = { is_ai = yes mam_revenue_ministry_trigger = yes mam_revenue_fund_ready_trigger = yes
  treasury >= 0 primary_title = {
   has_variable = mam_cf_project_type has_variable = mam_cf_project_target
   exists = var:mam_cf_project_target.holder var:mam_cf_project_cash > 0
   has_variable = mam_cf_project_until var:mam_cf_project_until > current_date
   NOT = { has_variable = mam_cf_project_instance } NOT = { has_variable = mam_cf_payment_hold }
   trigger_if = { limit = { has_variable = mam_cf_start_retry } var:mam_cf_start_retry <= current_date }
  }
 }
  mam_revenue_fund_prepare_project_budget_effect = yes
  save_scope_as = mam_cf_start_actor save_scope_as = founder
  title:h_china.holder = { save_scope_as = owner }
  primary_title.var:mam_cf_project_target = { save_scope_as = mam_cf_start_target }
  clear_saved_scope = mam_cf_start_site clear_saved_scope = mam_cf_auto_project clear_saved_scope = province
  primary_title = { set_variable = { name = mam_cf_start_retry value = { value = current_date add = 7 } } }
'''+ '\n'.join(branches)+r'''
  if = { limit = { NOT = { exists = scope:mam_cf_start_site } }
   primary_title = {
    if = { limit = { NOT = { has_variable = mam_cf_start_blocked } }
     debug_log = "MAM_PROJECT_START: paid grant waiting for native eligibility, affordability or a valid authorized site"
    }
    set_variable = { name = mam_cf_start_blocked value = 1 }
   }
  }
 }
}
mam_revenue_fund_check_auto_start_effect = {
 if = { limit = { exists = scope:mam_cf_auto_project }
  primary_title = {
   set_variable = { name = mam_cf_start_before value = scope:mam_cf_start_before }
   set_variable = { name = mam_cf_start_price value = scope:mam_cf_start_price }
  }
  save_scope_value_as = { name = mam_cf_start_after value = treasury }
  primary_title = { set_variable = { name = mam_cf_start_after value = scope:mam_cf_start_after } }
  if = { limit = { primary_title.var:mam_cf_project_instance = scope:mam_cf_auto_project
   treasury <= { value = scope:mam_cf_start_before subtract = scope:mam_cf_start_price add = 0.01 }
  }
   primary_title = { remove_variable = mam_cf_start_blocked set_variable = { name = mam_cf_start_on value = current_date } }
   debug_log = "MAM_PROJECT_START: funded AI ministry planned its authorized native project"
   trigger_event = { id = mam_fund.31 days = 1 }
  }
  else = {
   primary_title = { set_variable = { name = mam_cf_payment_hold value = 1 } set_variable = { name = mam_cf_start_blocked value = 2 } }
   debug_log = "MAM_PROJECT_START: project created but native charge or grant receipt uncertain; held without replay"
  }
 }
 else = {
  primary_title = { set_variable = { name = mam_cf_start_blocked value = 1 } }
  debug_log = "MAM_PROJECT_START: native planning returned no project; grant retained, retry in seven days"
 }
}
''')

events='events/mam_revenue_common_project_orders.txt'
edit(events,'mam_fund.31',lambda s:s.replace(' immediate = {',' immediate = {\n  mam_revenue_fund_auto_start_effect = yes',1))
write(events,read(events)+r'''
mam_fund.36 = {
 type = character_event hidden = yes
 trigger = { is_ai = yes mam_revenue_ministry_trigger = yes }
 immediate = { mam_revenue_fund_auto_start_effect = yes }
}
''')
choices='common/scripted_effects/mam_revenue_common_choice_effects.txt'
edit(choices,'mam_revenue_fund_legacy_commit_effect',lambda s:s.replace(
    'var:mam_cf_target.holder = { mam_revenue_fund_prepare_project_budget_effect = yes }',
    'var:mam_cf_target.holder = { mam_revenue_fund_prepare_project_budget_effect = yes trigger_event = { id = mam_fund.36 days = 1 } }',1))

menu='events/mam_revenue_common_events.txt'
def preflight_menu(s):
    s=s.replace('immediate = { save_scope_as = founder  }',
                'immediate = { save_scope_as = founder mam_revenue_fund_preflight_project_choices_effect = yes }',1)
    edits=[]
    for option in (n for n in parse(s)[0].children if n.key=='option'):
        name=next((n.value for n in option.children if n.key=='name'),None)
        match=re.fullmatch(r'mam_cf.project_(\d+)',name or '')
        if match:
            gate=next(n for n in option.children if n.key=='trigger')
            edits.append((gate.end-1,'\n trigger_if = { limit = { is_ai = yes } scope:mam_cf_start_choice_'+match[1]+' = 1 }\n'))
    for at,addition in sorted(edits,reverse=True):s=s[:at]+addition+s[at:]
    return s
edit(menu,'mam_fund.5',preflight_menu)
edit(menu,'mam_fund.96',lambda s:s.replace('limit = { mam_revenue_province_trigger = yes }',
    '''limit = { mam_revenue_province_trigger = yes
 trigger_if = { limit = { root = { has_title = title:e_minister_grand_marshal } }
  any_sub_realm_county = { any_neighboring_county = { exists = holder holder.top_liege != title:h_china.holder } }
 }
}''',1))

p=ROOT/'descriptor.mod'
p.write_text(re.sub(r'version="[^"]+"','version="0.4.0-alpha.20-dev.57"',read('descriptor.mod'),count=1),encoding='utf-8')
print('Applied dev.57 native callback/scope repairs and funded AI project planning continuation.')
