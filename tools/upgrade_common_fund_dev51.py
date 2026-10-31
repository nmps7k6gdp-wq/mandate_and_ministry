"""Single-screen, live departmental accounts. Run after the dev.50 generator."""
from pathlib import Path
import json
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]
parse=runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']
def read(rel): return (ROOT/rel).read_text(encoding='utf-8-sig')
def write(rel,s): (ROOT/rel).write_text(s.rstrip()+'\n',encoding='utf-8-sig')
def edit(rel,key,fn):
    s=read(rel); n=next(n for n in parse(s) if n.key==key)
    write(rel,s[:n.start]+fn(s[n.start:n.end])+s[n.end:])

events='events/mam_revenue_common_events.txt'
# Saved pages remain valid entry points, but every one now opens all nine rows.
for eid in (11,12,13):
    edit(events,f'mam_fund.{eid}',lambda s,eid=eid:f'''mam_fund.{eid} = {{
 type = character_event theme = stewardship title = mam_cf.departments_title
 desc = mam_cf.departments_all
 immediate = {{ mam_revenue_fund_bind_accounts_effect = yes }}
 left_portrait = {{ character = root animation = reading }}
 option = {{ name = mam_cf.accounts_close }}
 option = {{ name = mam_cf.refresh_accounts custom_tooltip = mam_cf.refresh_accounts_tt
  hidden_effect = {{ trigger_event = mam_fund.11 }} }}
}}''')

# Keep the account overview short. Administrative actions move to their own
# screen; multiple old/stale actor gates cannot crowd out the account text.
s=read(events); top=next(n for n in parse(s) if n.key=='mam_fund.6')
actions=[]; cuts=[]
for n in top.children:
    if n.key!='option': continue
    name=next(c.value for c in n.children if c.key=='name')
    if name in {'mam_cf.release_programme','mam_cf.suspend','mam_cf.restore'}:
        actions.append(s[n.start:n.end]); cuts.append((n.start,n.end))
for a,b in sorted(cuts,reverse=True): s=s[:a]+s[b:]
write(events,s)
edit(events,'mam_fund.6',lambda s:s[:-1]+'''
 option = { name = mam_cf.view_controls
  trigger = { custom_tooltip = { text = mam_cf.context_tt
   OR = { mam_revenue_emperor_trigger = yes mam_revenue_chancellor_trigger = yes } } }
  hidden_effect = { trigger_event = mam_fund.14 }
 }
 option = { name = mam_cf.refresh_accounts custom_tooltip = mam_cf.refresh_accounts_tt
  hidden_effect = { trigger_event = mam_fund.6 } }
}''')
write(events,read(events)+'''
mam_fund.14 = {
 type = character_event theme = stewardship title = mam_cf.controls_title desc = mam_cf.controls_desc
 immediate = { mam_revenue_fund_bind_accounts_effect = yes }
 left_portrait = { character = root animation = reading }
 option = { name = mam_cf.accounts_close }
'''+ '\n'.join(actions)+'\n}\n')

# These are read-only presentation values. They do not approve costs, replenish
# money, advance queues or overwrite the last completed settlement.
values='common/script_values/mam_revenue_common_values.txt'
extra=''
for key,var in [('cash','holder.treasury'),('target','mam_revenue_fund_target')]:
    gate='exists = holder' if key=='cash' else 'has_variable = mam_cf_cost'
    extra+=f'''mam_revenue_fund_display_{key} = {{
 value = 0 if = {{ limit = {{ {gate} }} value = {var} }}
}}
'''
write(values,read(values)+'\n'+extra)

local='localization/english/mam_revenue_common_l_english.yml'
loc={}
for line in read(local).splitlines()[1:]:
    match=re.fullmatch(r' ([\w.]+):0 (".*")',line)
    if match: loc[match[1]]=json.loads(match[2])
for page in range(3): loc.pop(f'mam_cf.departments_{page}',None)
loc.update({
 'mam_cf.refresh_accounts':'Bring the current accounts.',
 'mam_cf.refresh_accounts_tt':'Re-read current cash and recalculate the account summary. This does not collect money, pay an advance or approve new spending. Reconciliation figures describe the last completed monthly settlement.',
 'mam_cf.view_controls':'Review the safeguards on public spending.',
 'mam_cf.controls_title':'Safeguards on Public Spending',
 'mam_cf.controls_desc':"The fiscal law is #high [GetPlayer.Custom('MamRevenueFundAuthority')]#!. The programme is #high [GetPlayer.Custom('MamRevenueFundProgramme')]#!.\n\nExisting salaries and approved commitments continue. I may change who directs future programmes or temporarily require superior review of discretionary releases.",
 'mam_cf.accounts_desc':"Revenue holds #high [GetTitleByKey('e_minister_of_revenue').MakeScope.ScriptValue('mam_revenue_fund_display_cash')|0]#! [treasury_i] in the common fund. After commitments and reserves, #high [GetTitleByKey('h_china').MakeScope.ScriptValue('mam_revenue_fund_available')|0]#! [treasury_i] is available.\n\n[GetPlayer.Custom('MamRevenueFundStatement')]\n\nProgramme: #high [GetPlayer.Custom('MamRevenueFundProgramme')]#!.\nAuthority: #high [GetPlayer.Custom('MamRevenueFundAuthority')]#!.",
 'mam_cf.statement_none':'No monthly reconciliation has been completed yet. Operating income continues during adoption.',
 'mam_cf.statement_done':"Last completed reconciliation: #high [GetTitleByKey('h_china').MakeScope.Var('mam_cf_statement_collected').GetValue|0]#! [treasury_i] collected; #high [GetTitleByKey('h_china').MakeScope.Var('mam_cf_statement_advanced').GetValue|0]#! [treasury_i] advanced. These are settled transfers, not current cash.",
 'mam_cf.flow_desc':"Ministry income reaches each office. At reconciliation, offices keep approved operating balances and project advances; surplus passes to Revenue. The fund then pays funded operating shortfalls.\n\n[GetPlayer.Custom('MamRevenueFundStatement')]\n\nNative income, expenses and separate grants change cash between settlements. Revenue's public treasury is the common bank. Its operating target is an authorization within that bank. Personal Gold remains separate.",
})
roster=[('e_minister_chancellor','Chancellery'),('e_minister_censor','Censorate'),
 ('e_minister_grand_marshal','Grand Marshal'),('e_minister_of_personnel','Personnel'),
 ('e_minister_of_war','War'),('e_minister_of_rites','Rites'),('e_minister_of_works','Works'),
 ('e_minister_of_revenue','Revenue'),('e_minister_of_justice','Justice')]
custom='''
MamRevenueFundStatement = {
 type = character
 text = { trigger = { title:h_china = { has_variable = mam_cf_statement_date } }
  localization_key = mam_cf.statement_done }
 text = { localization_key = mam_cf.statement_none }
}
'''
rows=[]
for i,(title,label) in enumerate(roster,1):
    getter=f"GetTitleByKey('{title}').MakeScope"
    cash=f"[{getter}.ScriptValue('mam_revenue_fund_display_cash')|0]"
    goal=f"[{getter}.ScriptValue('mam_revenue_fund_display_target')|0]"
    loc[f'mam_cf.department_{i}']=f'#high {label}#!: {cash} / {goal}'
    loc[f'mam_cf.department_{i}_unreviewed']=f'#high {label}#!: {cash} / unreviewed'
    loc[f'mam_cf.department_{i}_shared']=f'#high {label}#!: {cash} / shared holder account'
    loc[f'mam_cf.department_{i}_vacant']=f'#high {label}#!: vacant'
    custom+=f'''MamRevenueFundDepartment{i} = {{
 type = character
 text = {{ trigger = {{ title:{title} = {{ NOT = {{ exists = holder }} }} }} localization_key = mam_cf.department_{i}_vacant }}
 text = {{ trigger = {{ title:{title} = {{ exists = holder holder.primary_title != title:{title} }} }} localization_key = mam_cf.department_{i}_shared }}
 text = {{ trigger = {{ title:{title} = {{ NOT = {{ has_variable = mam_cf_cost }} }} }} localization_key = mam_cf.department_{i}_unreviewed }}
 text = {{ localization_key = mam_cf.department_{i} }}
}}
'''
    rows.append(f"[GetPlayer.Custom('MamRevenueFundDepartment{i}')]")
loc['mam_cf.departments_all']='#bold Current public cash / approved operating target#! [treasury_i]\n\n'+'\n'.join(rows)+"\n\nRevenue's cash includes the common fund; its target covers only its own operations. Targets exclude project earmarks. Shared holders have one native cash account."
write('common/customizable_localization/mam_revenue_common_loc.txt',read('common/customizable_localization/mam_revenue_common_loc.txt')+custom)
write(local,'l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items()))
path=ROOT/'descriptor.mod'
path.write_text(re.sub(r'version="[^"]+"','version="0.4.0-alpha.20-dev.51"',path.read_text(),count=1),encoding='utf-8')
print('Applied dev.51 single-screen live accounts.')
