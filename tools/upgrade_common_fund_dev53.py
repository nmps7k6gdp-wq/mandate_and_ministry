"""Correct Strengthen Capital's common-fund jurisdiction without native edits."""
from pathlib import Path
import json,re,runpy

ROOT=Path(__file__).resolve().parents[1]
parse=runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']
def read(rel):return (ROOT/rel).read_text(encoding='utf-8-sig')
def write(rel,s):(ROOT/rel).write_text(s.rstrip()+'\n',encoding='utf-8-sig' if Path(rel).suffix in {'.txt','.yml'} else 'utf-8')
def edit(rel,key,fn):
 s=read(rel);n=next(n for n in parse(s) if n.key==key)
 write(rel,s[:n.start]+fn(s[n.start:n.end])+s[n.end:])

# A governor-scoped provincial grant cannot represent the Emperor's directly
# held capital. Existing TYPE 9 grants receive the correct realm-wide rule too;
# their type/cash/expiry checks remain in project_start_trigger unchanged.
edit('common/scripted_triggers/mam_revenue_common_triggers.txt',
 'mam_revenue_fund_project_location_trigger',lambda s:'''mam_revenue_fund_project_location_trigger = {
 primary_title = {
  trigger_if = { limit = { var:mam_cf_project_type = 9 }
   scope:province.county.holder = { top_liege = title:h_china.holder }
  }
  trigger_else = {
   exists = var:mam_cf_project_target.holder
   save_temporary_scope_as = mam_cf_project_office
   scope:province.county.holder = {
    OR = { this = scope:mam_cf_project_office.var:mam_cf_project_target.holder
     is_vassal_or_below_of = scope:mam_cf_project_office.var:mam_cf_project_target.holder }
   }
  }
 }
}''')

rel='common/scripted_effects/mam_revenue_common_initiative_effects.txt'
def correct_request(s):
 marker='''
   # Strengthen Capital is imperial work, regardless of the governor used to
   # open the project chooser. Keep the beneficiary ministry as the payer.
   if = { limit = { var:mam_cf_project_type = 9 }
    set_variable = { name = mam_cf_project_target value = title:h_china }
   }
'''
 if '# Strengthen Capital is imperial work' not in s:
  s=s.replace('set_variable = { name = mam_cf_project_target value = scope:mam_cf_site_title }',
              'set_variable = { name = mam_cf_project_target value = scope:mam_cf_site_title }'+marker)
 return s
edit(rel,'mam_revenue_fund_open_project_effect',correct_request)

locpath='localization/english/mam_revenue_common_l_english.yml';loc={}
for line in read(locpath).splitlines()[1:]:
 m=re.fullmatch(r' ([\w.]+):0 (".*")',line)
 if m:loc[m[1]]=json.loads(m[2])
loc['mam_cf.project_location_tt']='Use the area authorized for this project. Strengthen Capital uses the imperial realm, including counties held directly by the Emperor; provincial work uses the jurisdiction named in its approved request. Native site requirements still apply.'
write(locpath,'l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items()))
p=ROOT/'descriptor.mod';p.write_text(re.sub(r'version="[^"]+"','version="0.4.0-alpha.20-dev.53"',p.read_text(),count=1),encoding='utf-8')
print('Applied dev.53 Strengthen Capital jurisdiction correction.')
