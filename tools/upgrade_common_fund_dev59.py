"""Reliable due reconciliation, current relief priority and bounded diagnostics.

Applied only by the complete staged builder. Existing cash, due dates, leases,
project identity, approvals and uncertain-payment holds are retained.
"""
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT / 'tools/verify_revenue_source.py'))['parse']


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8-sig')


def write(rel, text):
    encoding = 'utf-8-sig' if Path(rel).suffix in {'.txt', '.yml'} else 'utf-8'
    (ROOT / rel).write_text(text.rstrip() + '\n', encoding=encoding)


def replace_once(text, old, new):
    assert text.count(old) == 1, ('Expected one insertion anchor', old)
    return text.replace(old, new, 1)


def edit(rel, key, fn):
    text = read(rel)
    node = next(n for n in parse(text) if n.key == key)
    write(rel, text[:node.start] + fn(text[node.start:node.end]) + text[node.end:])


def diagnostic(key):
    return 'mam_revenue_fund_record_diagnostic_effect = { KEY = ' + key + ' }'


# Reuse the realm's seven-day lease and the reconciliation's existing 25-day
# guard. Normal settlement cadence is therefore four weeks, with no catch-up
# replay for years of missed monthly work in an old save.
cash = 'common/scripted_effects/mam_revenue_common_cash_effects.txt'
edit(cash, 'mam_revenue_fund_payroll_effect', lambda s: replace_once(
    s, '  save_scope_as = mam_cf_payroll_sovereign',
    '''  # Dev.59: due monthly work uses the live weekly lease, never an
  # undocumented monthly engine callback. Its own due gate prevents replay.
  mam_revenue_fund_month_effect = yes
  save_scope_as = mam_cf_payroll_sovereign'''))
edit(cash, 'mam_revenue_fund_month_effect', lambda s: replace_once(
    s, '  set_variable = { name = mam_cf_statement_date value = current_date }',
    '''  set_variable = { name = mam_cf_statement_date value = current_date }
  ''' + diagnostic('reconciled')))
edit(cash, 'mam_revenue_fund_init_office_effect', lambda s: replace_once(
    s, '  set_variable = { name = mam_cf_project_cash value = 0 }\n  remove_variable = mam_cf_project_type',
    '''  if = { limit = { var:mam_cf_project_cash > 0 }
   ''' + diagnostic('project_advance_expired') + '''
  }
  set_variable = { name = mam_cf_project_cash value = 0 }
  remove_variable = mam_cf_project_type'''))

# CK3 documents quarterly_playable_pulse. This is only a recovery entry into
# the existing startup/lease logic, not a second recurring payment timer.
actions = 'common/on_action/mam_revenue_on_actions.txt'
write(actions, replace_once(read(actions),
    'monthly_playable_pulse = { on_actions = { mam_revenue_fund_monthly } }',
    '''# Keep the old custom action name for saved/reference compatibility.
# The weekly realm lease performs due reconciliation; this native pulse repairs
# a missing lease/custodian transition without bypassing its due-date guard.
quarterly_playable_pulse = { on_actions = { mam_revenue_fund_monthly } }'''))

# The live Recovery programme replaces the retired mam_rv_priority setting.
# An explicit guarded comparison keeps legacy/non-adopted contexts safe.
def current_relief_priority(s):
    old = 'title:h_china = { var:mam_rv_priority = 2 }'
    new = '''title:h_china = {
  has_variable = mam_cf_programme
  trigger_if = { limit = { has_variable = mam_cf_programme } var:mam_cf_programme = 2 }
 }'''
    # This shared legacy value is authored input, unlike the regenerated common
    # module. A subsequent full build must accept its already-migrated form.
    if old in s:
        return replace_once(s, old, new)
    assert s.count(new) == 1 and 'mam_rv_priority' not in s, 'Unexpected relief ranking source'
    return s


edit('common/script_values/mam_revenue_values.txt', 'mam_revenue_need_score', current_relief_priority)

# Scalar counters and last occurrence dates are institutional, compact and
# safe in already-adopted saves. They have no financial or gameplay authority.
write('common/scripted_effects/mam_revenue_common_diagnostics.txt', r'''
# Callable from character/title/story context. Only counts actual effect paths;
# this must never be used in a trigger, tooltip or affordability simulation.
mam_revenue_fund_record_diagnostic_effect = {
 title:h_china = {
  if = { limit = { NOT = { has_variable = mam_cf_diag_$KEY$ } }
   set_variable = { name = mam_cf_diag_$KEY$ value = 0 }
  }
  change_variable = { name = mam_cf_diag_$KEY$ add = 1 }
  set_variable = { name = mam_cf_diag_last_$KEY$ value = current_date }
 }
 debug_log = "MAM_FUND_DIAG: $KEY$"
}
''')

initiative = 'common/scripted_effects/mam_revenue_common_initiative_effects.txt'
edit(initiative, 'mam_revenue_fund_initiative_effect', lambda s: replace_once(
    replace_once(s, ' # Fund one eligible project proposal each monthly review.',
        ''' # Fund one eligible project proposal each monthly review.
 save_scope_value_as = { name = mam_cf_proposal_dispatched value = 0 }
 ''' + diagnostic('proposal_cycle')),
    '} trigger_event = { id = mam_fund.96 days = 1 } }',
    '''}
 save_scope_value_as = { name = mam_cf_proposal_dispatched value = 1 }
 ''' + diagnostic('proposal_dispatched') + '''
 trigger_event = { id = mam_fund.96 days = 1 } }
 if = { limit = { scope:mam_cf_proposal_dispatched = 0 }
  ''' + diagnostic('proposal_no_dispatch') + '''
 }'''))
edit(initiative, 'mam_revenue_fund_open_project_effect', lambda s: replace_once(
    s, '  scope:mam_cf_created = {',
    '  ' + diagnostic('project_requested') + '''
  debug_log = "MAM_FUND_PROJECT_REQUEST: type $TYPE$"
  scope:mam_cf_created = {'''))

events = 'events/mam_revenue_common_events.txt'
edit(events, 'mam_fund.96', lambda s: replace_once(s,
    '  if = { limit = { exists = scope:mam_cf_site_title } trigger_event = mam_fund.5 }',
    '''  if = { limit = { exists = scope:mam_cf_site_title }
   ''' + diagnostic('proposal_jurisdiction_found') + '''
   trigger_event = mam_fund.5
  }
  else = { ''' + diagnostic('proposal_no_jurisdiction') + ' }'))

auto = 'common/scripted_effects/mam_revenue_common_auto_start.txt'
def preflight(s):
    # Attach inside the AI-only branch, after all 17 native location checks.
    top = parse(s)[0]
    branch = next(n for n in top.children if n.key == 'if')
    valid = ' '.join(f'scope:mam_cf_start_choice_{index} = 1' for index in range(1, 18))
    addition = '''
 if = { limit = { OR = { ''' + valid + ''' } }
  ''' + diagnostic('proposal_valid_choices') + '''
 }
 else = { ''' + diagnostic('proposal_no_valid_choice') + ''' }
'''
    return s[:branch.end-1] + addition + s[branch.end-1:]
edit(auto, 'mam_revenue_fund_preflight_project_choices_effect', preflight)
for key, marker in [
    ('mam_revenue_fund_auto_start_effect', 'paid grant waiting for native eligibility, affordability or a valid authorized site'),
    ('mam_revenue_fund_check_auto_start_effect', 'funded AI ministry planned its authorized native project'),
    ('mam_revenue_fund_check_auto_start_effect', 'project created but native charge or grant receipt uncertain; held without replay'),
    ('mam_revenue_fund_check_auto_start_effect', 'native planning returned no project; grant retained, retry in seven days')]:
    outcome = {'paid grant waiting for native eligibility, affordability or a valid authorized site': 'start_waiting_native',
               'funded AI ministry planned its authorized native project': 'start_planned',
               'project created but native charge or grant receipt uncertain; held without replay': 'start_payment_uncertain',
               'native planning returned no project; grant retained, retry in seven days': 'start_no_project'}[marker]
    old = 'debug_log = "MAM_PROJECT_START: ' + marker + '"'
    edit(auto, key, lambda s, old=old, outcome=outcome: replace_once(s, old, old + '\n ' + diagnostic(outcome)))

choices = 'common/scripted_effects/mam_revenue_common_choice_effects.txt'
edit(choices, 'mam_revenue_fund_legacy_commit_effect', lambda s: replace_once(s,
    '    if = { limit = { var:mam_cf_kind = 3 }\n     var:mam_cf_target.holder = { mam_revenue_fund_prepare_project_budget_effect',
    '    if = { limit = { var:mam_cf_kind = 3 }\n     ' + diagnostic('start_advance_authorized') + '\n     var:mam_cf_target.holder = { mam_revenue_fund_prepare_project_budget_effect'))

queue = 'common/scripted_effects/mam_revenue_common_queue_effects.txt'
edit(queue, 'mam_revenue_fund_close_effect', lambda s: replace_once(s,
    ' set_variable = { name = mam_cf_closed value = current_date }',
    ''' set_variable = { name = mam_cf_closed value = current_date }
 if = { limit = { var:mam_cf_kind = 3 }
  ''' + diagnostic('start_result_$RESULT$') + '''
 }
 if = { limit = { var:mam_cf_kind = 13 }
  ''' + diagnostic('budget_result_$RESULT$') + '''
 }'''))

write('descriptor.mod', re.sub(r'version="[^"]+"',
    'version="0.4.0-alpha.20-dev.59"', read('descriptor.mod'), count=1))
# Keep the old explanatory screen's breadcrumb consistent with Realm > Laws.
law_loc = 'localization/english/mam_revenue_l_english.yml'
write(law_loc, read(law_loc).replace('Realm > Laws > Fiscal Authority',
                                   'Realm > Laws > Revenue Fiscal Authority'))
print('Applied dev.59 weekly due reconciliation, native quarterly recovery, current relief priority and diagnostic counters.')
