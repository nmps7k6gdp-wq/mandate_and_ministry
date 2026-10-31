"""Keep native project prices in contributor scope and expose grant failures."""
from pathlib import Path
import json,re,runpy
ROOT=Path(__file__).resolve().parents[1]
parse=runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']
def read(rel):return (ROOT/rel).read_text(encoding='utf-8-sig')
def write(rel,s):(ROOT/rel).write_text(s.rstrip()+'\n',encoding='utf-8-sig' if Path(rel).suffix in {'.txt','.yml'} else 'utf-8')
def edit(rel,key,fn):
 s=read(rel);n=next(n for n in parse(s) if n.key==key)
 write(rel,s[:n.start]+fn(s[n.start:n.end])+s[n.end:])

triggers='common/scripted_triggers/mam_revenue_common_triggers.txt'
edit(triggers,'mam_revenue_fund_project_start_trigger',lambda s:r'''mam_revenue_fund_project_start_trigger = {
 # Native prices use the founder's council seat, income and other character
 # properties. Evaluate BEFORE entering primary_title, which stores the grant.
 save_temporary_scope_value_as = { name = mam_cf_required_start_cost value = $COST$ }
 primary_title = {
  custom_tooltip = { text = mam_cf.grant_exists_tt has_variable = mam_cf_project_type }
  trigger_if = { limit = { has_variable = mam_cf_project_type }
  custom_tooltip = { text = mam_cf.grant_type_tt var:mam_cf_project_type = $TYPE$ }
  custom_tooltip = { text = mam_cf.grant_current_tt
   has_variable = mam_cf_project_until
   trigger_if = { limit = { has_variable = mam_cf_project_until } var:mam_cf_project_until > current_date } }
  custom_tooltip = { text = mam_cf.grant_unused_tt NOT = { has_variable = mam_cf_project_instance } }
  custom_tooltip = { text = mam_cf.grant_cash_tt has_variable = mam_cf_project_cash
   trigger_if = { limit = { has_variable = mam_cf_project_cash } var:mam_cf_project_cash >= scope:mam_cf_required_start_cost } }
  custom_tooltip = { text = mam_cf.grant_hold_tt NOT = { has_variable = mam_cf_payment_hold } }
  }
 }
}''')
edit(triggers,'mam_revenue_fund_contribution_trigger',lambda s:r'''mam_revenue_fund_contribution_trigger = {
 save_temporary_scope_value_as = { name = mam_cf_required_contribution_cost value = $COST$ }
 exists = scope:great_project
 primary_title = {
  NOT = { has_variable = mam_cf_payment_hold }
  var:mam_cf_project_instance = scope:great_project
  var:mam_cf_project_until > current_date
  var:mam_cf_project_cash >= scope:mam_cf_required_contribution_cost
 }
}''')

# Remove the single opaque authorization tooltip around the start guard, so
# native UI can show each actual failing condition. Reconstruct every override
# from the native original plus its explicit audited insertions.
manifest_path='docs/COMMON-FUND-NATIVE-PROJECTS.json';manifest=json.loads(read(manifest_path));types={}
for name,entry in manifest['definitions'].items():
 for insertion in entry['insertions']:
  match=re.search(r'mam_revenue_fund_project_start_trigger = \{ TYPE = (\d+) COST = ([\w]+) \}',insertion['text'])
  if not match or not any(t in insertion['text'] for t in ['text = mam_cf.project_authorization_tt','show exact grant checks']):continue
  index=int(match[1]);types[index]=name
  insertion['text']='''
# MAM COMMON FUND bridge: preserve native eligibility and show exact grant checks.
trigger_if = { limit = { mam_revenue_fund_member_trigger = yes }
 mam_revenue_fund_project_start_trigger = { TYPE = '''+str(index)+' COST = '+match[2]+''' }
}
'''
 originals={}
 source=Path(entry['native_source']).read_text(encoding='utf-8-sig')
 node=next(n for n in parse(source) if n.key==name);changed=source[node.start:node.end]
 for item in sorted(entry['insertions'],key=lambda e:(e['at'],e['text']),reverse=True):
  at=item['at'];changed=changed[:at]+item['text']+changed[at:]
 originals[name]=changed
 # Each definition is unique across the mod's audited native project copies.
 for path in (ROOT/'common/great_projects/types').glob('zz_mam_revenue_common_*.txt'):
  text=path.read_text(encoding='utf-8-sig');n=next((n for n in parse(text) if n.key==name),None)
  if n:
   write(str(path.relative_to(ROOT)),text[:n.start]+changed+text[n.end:]);break
write(manifest_path,json.dumps(manifest,indent=2))

# Native project AI spends from long-term budgets. Incoming grants arrive via
# the short-term payment boundary. Move only a funded project's missing reserve
# internally: this does not pay another grant or change total public treasury.
cash='common/scripted_effects/mam_revenue_common_cash_effects.txt'
helper=r'''
mam_revenue_fund_prepare_project_budget_effect = {
 if = { limit = { is_ai = yes has_treasury = yes
  primary_title = { has_variable = mam_cf_project_type var:mam_cf_project_cash > 0
   NOT = { has_variable = mam_cf_payment_hold } }
  treasury >= primary_title.var:mam_cf_project_cash
 }
  save_scope_value_as = { name = mam_cf_project_budget_before value = treasury }
  save_scope_value_as = { name = mam_cf_project_budget_move value = {
   value = primary_title.var:mam_cf_project_cash subtract = long_term_treasury min = 0 max = short_term_treasury
  } }
  if = { limit = { scope:mam_cf_project_budget_move > 0 }
   move_budget_treasury = { treasury = scope:mam_cf_project_budget_move from = budget_short_term to = budget_long_term }
   if = { limit = { OR = {
    treasury < { value = scope:mam_cf_project_budget_before subtract = 0.01 }
    treasury > { value = scope:mam_cf_project_budget_before add = 0.01 }
   } }
    debug_log = "MAM_COMMON_FUND: project budget preparation changed total treasury unexpectedly"
   }
  }
 }
}
'''
if 'mam_revenue_fund_prepare_project_budget_effect = {' not in read(cash):write(cash,read(cash)+helper)
edit(cash,'mam_revenue_fund_init_office_effect',lambda s:s if 'holder = { mam_revenue_fund_prepare_project_budget_effect = yes }' in s else s[:-1]+'\n holder = { mam_revenue_fund_prepare_project_budget_effect = yes }\n}')
choices='common/scripted_effects/mam_revenue_common_choice_effects.txt'
edit(choices,'mam_revenue_fund_commit_effect',lambda s:s.replace('    mam_revenue_fund_native_rewards_effect = yes',r'''
    if = { limit = { var:mam_cf_kind = 3 }
     var:mam_cf_target.holder = { mam_revenue_fund_prepare_project_budget_effect = yes }
    }
    mam_revenue_fund_native_rewards_effect = yes''') if 'var:mam_cf_target.holder = { mam_revenue_fund_prepare_project_budget_effect = yes }' not in s else s)

# Name the specific project in requests and paid results. A general grant for
# another project or ordinary operations must never masquerade as TYPE 3.
local='localization/english/mam_revenue_common_l_english.yml';loc={}
for line in read(local).splitlines()[1:]:
 m=re.fullmatch(r' ([\w.]+):0 (".*")',line)
 if m:loc[m[1]]=json.loads(m[2])
loc.update({
 'mam_cf.grant_exists_tt':'This office has an approved project grant.',
 'mam_cf.grant_type_tt':'The approved grant is for this project type. Funding for another project or ordinary operations does not authorize this work.',
 'mam_cf.grant_current_tt':'The project authorization has not expired.',
 'mam_cf.grant_unused_tt':'This starting grant has not already been used to plan a project.',
 'mam_cf.grant_cash_tt':"Enough unspent project funding remains to cover this minister's current native starting cost, including applicable discounts.",
 'mam_cf.grant_hold_tt':'The public account has no unresolved payment hold.',
 'mam_cf.grant_none':'No starting-project authorization is recorded.',
})
for i,name in sorted(types.items()):
 project='#high $great_project_type_'+name+'$#!'
 loc[f'mam_cf.project_request_{i}']=f'[mam_cf_subject.GetShortUIName] requests #high [mam_cf_quote|0]#! [treasury_i] for {project} in #high [mam_cf_project_target.GetName]#!.\n\nThe advance authorizes this project\'s planning cost. Required construction contributions are funded separately.'
 loc[f'mam_cf.project_paid_{i}']=f'[mam_cf_subject.GetShortUIName] has received #high [mam_cf_result_amount|0]#! [treasury_i] for {project} in #high [mam_cf_project_target.GetName]#!.\n\nThe ministry may now choose an eligible location and plan this work. Required construction contributions remain separate.'
 loc[f'mam_cf.grant_name_{i}']='$great_project_type_'+name+'$'
custom='common/customizable_localization/mam_revenue_common_loc.txt'
block='MamRevenueFundGrantProject = {\n type = character\n'
for i in sorted(types):block+=f' text = {{ trigger = {{ primary_title = {{ has_variable = mam_cf_project_type var:mam_cf_project_type = {i} }} }} localization_key = mam_cf.grant_name_{i} }}\n'
block+=' text = { localization_key = mam_cf.grant_none }\n}'
if 'MamRevenueFundGrantProject = {' in read(custom):edit(custom,'MamRevenueFundGrantProject',lambda s:block)
else:write(custom,read(custom)+'\n'+block)
for key in ['mam_cf.own_desc','mam_cf.own_revenue_desc']:
 if 'MamRevenueFundGrantProject' not in loc[key]:loc[key]+="\n\nRecorded project: #high [GetPlayer.Custom('MamRevenueFundGrantProject')]#!."
events='events/mam_revenue_common_events.txt'
requests='\n'.join(f'  triggered_desc = {{ trigger = {{ scope:mam_cf_file.var:mam_cf_kind = 3 scope:mam_cf_file.var:mam_cf_project_type = {i} }} desc = mam_cf.project_request_{i} }}' for i in sorted(types))
for eid in ['mam_fund.1','mam_fund.8']:
 edit(events,eid,lambda s:s.replace('  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_kind = 3 } desc = mam_cf.project_desc }',requests+'\n  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_kind = 3 } desc = mam_cf.project_desc }') if 'desc = mam_cf.project_request_3' not in s else s)
paid='\n'.join(f' triggered_desc = {{ trigger = {{ scope:mam_cf_file.var:mam_cf_kind = 3 scope:mam_cf_file.var:mam_cf_project_type = {i} scope:mam_cf_file.var:mam_cf_result = 1 scope:mam_cf_file.var:mam_cf_paid_from != scope:mam_cf_file.var:mam_cf_paid_to }} desc = mam_cf.project_paid_{i} }}' for i in sorted(types))
edit(events,'mam_fund.20',lambda s:s.replace('desc = { first_valid = {','desc = { first_valid = {\n'+paid,1) if 'desc = mam_cf.project_paid_3' not in s else s)
write(local,'l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items()))
p=ROOT/'descriptor.mod';p.write_text(re.sub(r'version="[^"]+"','version="0.4.0-alpha.20-dev.54"',p.read_text(),count=1),encoding='utf-8')
print('Applied dev.54 character-scoped project prices, grant diagnostics and AI budget preparation.')
