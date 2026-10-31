"""Imperial Wall grants, pre-payment site revalidation and native campaign scopes.

Run only through the staged full builder. Native inputs, saved keys, prices,
Personnel, approval authority, paid grants and financial holds are preserved.
"""
from pathlib import Path
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT / 'tools/verify_revenue_source.py'))['parse']


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8-sig')


def write(rel, text):
    (ROOT / rel).write_text(text.rstrip() + '\n', encoding='utf-8-sig' if Path(rel).suffix in {'.txt', '.yml'} else 'utf-8')


def once(text, old, new):
    assert text.count(old) == 1, ('Unexpected source anchor', old)
    return text.replace(old, new, 1)


def edit(rel, key, fn):
    text = read(rel)
    node = next(n for n in parse(text) if n.key == key)
    write(rel, text[:node.start] + fn(text[node.start:node.end]) + text[node.end:])


effects = 'common/scripted_effects/mam_revenue_common_project_orders.txt'
triggers = 'common/scripted_triggers/mam_revenue_common_triggers.txt'
edit(triggers, 'mam_revenue_fund_project_location_trigger', lambda s: once(s,
    '  trigger_else = {', '''  # Native Wall projects have no provincial location filter. Their work is
  # imperial; a previously selected governor is not their territorial owner.
  trigger_else_if = { limit = { OR = {
   var:mam_cf_project_type = 10 var:mam_cf_project_type = 11 var:mam_cf_project_type = 12
  } }
   holder = { top_liege = title:h_china.holder }
   trigger_if = { limit = { exists = scope:province }
    scope:province.county.holder = { top_liege = title:h_china.holder }
   }
  }
  trigger_else = {'''))
initiative = 'common/scripted_effects/mam_revenue_common_initiative_effects.txt'
edit(initiative, 'mam_revenue_fund_open_project_effect', lambda s: once(s,
    '   if = { limit = { var:mam_cf_project_type = 9 }', '''   if = { limit = { OR = {
    var:mam_cf_project_type = 10 var:mam_cf_project_type = 11 var:mam_cf_project_type = 12
   } } set_variable = { name = mam_cf_project_target value = title:h_china } }
   if = { limit = { var:mam_cf_project_type = 9 }'''))

# Share the actual native site search between menu preflight and final commit.
# The commit invocation is quiet and works for human/AI requesters alike; it
# neither writes a pretend grant nor pays an advance to test affordability.
auto = 'common/scripted_effects/mam_revenue_common_auto_start.txt'
text = read(auto)
top = next(n for n in parse(text) if n.key == 'mam_revenue_fund_preflight_project_choices_effect')
branch = next(n for n in top.children if n.key == 'if')
diagnostic = next(n for n in branch.children if n.key == 'if' and
                  'KEY = proposal_valid_choices' in text[n.start:n.end])
limit = next(n for n in branch.children if n.key == 'limit')
pure = text[limit.end:diagnostic.start]
diag = text[diagnostic.start:branch.end-1]
replacement = '''mam_revenue_fund_preflight_project_choices_effect = {
 if = { limit = { is_ai = yes exists = scope:mam_cf_site_title.holder }
  mam_revenue_fund_check_start_choices_effect = yes
''' + diag + '\n }\n}'
text = text[:top.start] + replacement + text[top.end:]
text += '\n# Character scope; caller binds mam_cf_site_title. No currency or diagnostic effects.\n'
text += 'mam_revenue_fund_check_start_choices_effect = {\n' + pure + '\n}\n'
write(auto, text)

clauses = '\n'.join(f'''   if = {{ limit = {{ scope:mam_cf_committing.var:mam_cf_project_type = {i}
    scope:mam_cf_start_choice_{i} = 1
    scope:mam_cf_committing.var:mam_cf_amount >= mam_revenue_fund_start_cost_{i}
   }} save_scope_value_as = {{ name = mam_cf_start_commit_valid value = 1 }} }}''' for i in range(1, 18))
write(auto, read(auto) + '''
# Story scope. Revalidate the actual requesting holder and current native site
# before any Treasury payment. An obsolete request is returned without cash.
mam_revenue_fund_validate_start_request_effect = {
 save_scope_value_as = { name = mam_cf_start_commit_valid value = 1 }
 if = { limit = { var:mam_cf_kind = 3 mam_revenue_fund_live_case_trigger = yes }
  save_scope_value_as = { name = mam_cf_start_commit_valid value = 0 }
  var:mam_cf_target.holder = {
   if = { limit = { mam_revenue_ministry_trigger = yes
    exists = scope:mam_cf_committing.var:mam_cf_project_target.holder
   }
    scope:mam_cf_committing.var:mam_cf_project_target = { save_scope_as = mam_cf_site_title }
    mam_revenue_fund_check_start_choices_effect = yes
''' + clauses + '''
   }
  }
 }
}
''')
choices = 'common/scripted_effects/mam_revenue_common_choice_effects.txt'
edit(choices, 'mam_revenue_fund_legacy_commit_effect', lambda s: once(s,
    ' save_scope_as = mam_cf_committing\n if = { limit = {', ''' save_scope_as = mam_cf_committing
 mam_revenue_fund_validate_start_request_effect = yes
 if = { limit = { scope:mam_cf_start_commit_valid = 0 }
  set_variable = { name = mam_cf_start_request_obsolete value = 1 }
  mam_revenue_fund_record_diagnostic_effect = { KEY = start_request_obsolete }
  mam_revenue_fund_close_effect = { RESULT = 4 }
  mam_revenue_fund_notify_effect = yes
 }
 else_if = { limit = {'''))

# Every native campaign contributor, including governors outside the common
# fund, needs the current project's war alias for native participant updates.
write(effects, read(effects) + '''
# Character scope in native on_contribution_funded. Never declare another war.
mam_revenue_fund_prepare_campaign_callback_effect = {
 clear_saved_scope = grand_campaign_war
 scope:great_project ?= {
  if = { limit = { has_variable = grand_campaign_war }
   var:grand_campaign_war ?= { save_scope_as = grand_campaign_war }
  }
 }
}
# Project presentation state only. A rejected, unfunded invoice with no native
# debit is a temporary native eligibility/affordability/cooldown wait. Old
# diagnostic snapshots are retained; uncertain Treasury holds are never reset.
mam_revenue_fund_refresh_native_wait_effect = {
 if = { limit = { has_variable = mam_pc_blocked has_variable = mam_pc_attempt_on
  has_variable = mam_pc_attempt_before has_variable = mam_pc_attempt_after
  has_variable = mam_pc_native_key var:mam_pc_native_key = 0
  NOT = { has_variable = mam_pc_executing }
  var:mam_pc_attempt_before = var:mam_pc_attempt_after
  var:mam_pc_attempt_on <= { value = current_date subtract = 7 }
  has_variable = mam_pc_attempt_actor exists = var:mam_pc_attempt_actor
  var:mam_pc_attempt_actor = {
   is_alive = yes exists = primary_title
   trigger_if = { limit = { exists = primary_title }
    primary_title = { NOT = { has_variable = mam_cf_payment_hold } }
   }
  }
 }
  remove_variable = mam_pc_blocked
  mam_revenue_fund_record_diagnostic_effect = { KEY = invoice_native_wait_elapsed }
 }
}
''')
edit(effects, 'mam_revenue_fund_init_project_order_effect', lambda s:
     s[:-1] + '\n mam_revenue_fund_refresh_native_wait_effect = yes\n}')

def safer_invoice(s):
    # Record native refusal explicitly, after the actual funded token/advance
    # exists. Do not force eligibility or silently drop engine checks.
    anchor = '    primary_title = { remove_variable = mam_pc_executing_project'
    s = once(s, anchor, '''    else = { mam_revenue_fund_record_diagnostic_effect = { KEY = invoice_native_check_refused } }
''' + anchor)
    s = once(s, '     if = { limit = { scope:mam_cf_pick_slot = { contribution_is_funded = yes } }',
        '''     if = { limit = { OR = {
      scope:mam_cf_pick_slot = { contribution_is_funded = yes }
      treasury < { value = scope:mam_cf_native_before subtract = 0.01 }
      treasury > { value = scope:mam_cf_native_before add = 0.01 }
     } }''')
    s = once(s, 'debug_log = "MAM_PROJECT_INVOICE: native slot funded but cash/receipt uncertain; account held; no retry"',
        'debug_log = "MAM_PROJECT_INVOICE: native funding state or cash delta uncertain; account held; no retry"')
    return s
edit(effects, 'mam_revenue_fund_execute_project_invoice_effect', safer_invoice)

edit('events/mam_revenue_common_events.txt', 'mam_fund.20', lambda s: once(s,
     ' desc = { first_valid = {', ''' desc = { first_valid = {
 triggered_desc = { trigger = { scope:mam_cf_file = { has_variable = mam_cf_start_request_obsolete } } desc = mam_cf.project_obsolete_desc }'''))
loc_path = 'localization/english/mam_revenue_common_l_english.yml'
write(loc_path, read(loc_path) + '\n mam_cf.project_obsolete_desc:0 ' + json.dumps(
    'The project proposed by #high [mam_cf_subject.GetShortUIName]#! can no longer proceed under the conditions used to prepare this request. The ministry must choose an eligible project and site, or revise the amount, before submitting it again. No Treasury was transferred.', ensure_ascii=False))

# Explicit, narrow native-source changes remain auditable against original
# source hashes. Insertions bind the alias; one documented replacement guards
# completion notifications without suppressing native rewards or changing wars.
manifest_path = 'docs/COMMON-FUND-NATIVE-PROJECTS.json'
manifest = json.loads(read(manifest_path))
entry = manifest['definitions']['grand_campaign_project']
native = Path(entry['native_source']).read_text(encoding='utf-8-sig')
project = next(n for n in parse(native) if n.key == 'grand_campaign_project')
slots = next(n for n in project.children if n.key == 'project_contributions')
for slot in slots.children:
    callback = next(n for n in slot.children if n.key == 'on_contribution_funded')
    entry['insertions'].append({'at': native.index('{', callback.start)+1-project.start,
        'text': '\n# MAM: native participant helper needs the linked war event target.\nhidden_effect = { mam_revenue_fund_prepare_campaign_callback_effect = yes }\n'})
completion = next(n for n in project.children if n.key == 'on_complete')
notification = next(n for n in completion.walk() if n.key == 'every_contribution' and
                    'trigger_event = tgp_china_ministry.0008' in native[n.start:n.end])
old = native[notification.start:notification.end]
new = '''every_contribution = {
 limit = { contribution_is_funded = yes }
 contributor ?= {
  if = { limit = { is_alive = yes }
   trigger_event = tgp_china_ministry.0008
  }
 }
}'''
entry['post_replacements'] = [{'old': old, 'new': new,
    'reason': 'Notify only funded contributions with a living recipient; native rewards and owner notification are preserved.'}]
write(manifest_path, json.dumps(manifest, indent=2))
# Rebuild only the changed project in its established generated output file.
assembled = native[project.start:project.end]
for insertion in sorted(entry['insertions'], key=lambda e: (e['at'], e['text']), reverse=True):
    at = insertion['at']; assembled = assembled[:at] + insertion['text'] + assembled[at:]
for replacement in entry.get('post_replacements', []):
    assembled = once(assembled, replacement['old'], replacement['new'])
path = 'common/great_projects/types/zz_mam_revenue_common_00_ministry_projects.txt'
edit(path, 'grand_campaign_project', lambda s: assembled)
write('descriptor.mod', re.sub(r'version="[^"]+"', 'version="0.4.0-alpha.20-dev.60"', read('descriptor.mod'), count=1))
print('Applied dev.60 imperial Wall jurisdiction, final grant revalidation, native campaign scope/recipient guards and safe invoice waits.')
