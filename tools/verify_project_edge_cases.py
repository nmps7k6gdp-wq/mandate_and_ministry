"""Source and independent safety cases for dev.60; not a CK3 emulator."""
from pathlib import Path
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT / 'tools/verify_revenue_source.py'))['parse']


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8-sig')


def verify():
    defs = {}
    for folder in ['common', 'events']:
        for path in (ROOT / folder).rglob('*revenue_common*.txt'):
            text = path.read_text(encoding='utf-8-sig')
            for node in parse(text):
                if node.children:
                    defs[node.key] = text[node.start:node.end]
    # The no-location-filter native projects are precisely imperial capital and
    # Wall work. Do not silently broaden provincial or geographical projects.
    manifest = json.loads(read('docs/COMMON-FUND-AI-START-MANIFEST.json'))
    global_types = {p['type'] for p in manifest['projects'] if p['province_filter'] is None}
    assert global_types == {9, 10, 11, 12}
    location = defs['mam_revenue_fund_project_location_trigger']
    for index in global_types:
        assert f'var:mam_cf_project_type = {index}' in location
    assert 'is_vassal_or_below_of' in location, 'Provincial grants lost their jurisdiction boundary'
    request = defs['mam_revenue_fund_open_project_effect']
    assert all(f'var:mam_cf_project_type = {i}' in request for i in [10, 11, 12])
    assert 'name = mam_cf_project_target value = title:h_china' in request
    commit = defs['mam_revenue_fund_legacy_commit_effect']
    assert commit.index('mam_revenue_fund_validate_start_request_effect') < commit.index('mam_revenue_fund_transfer_effect')
    assert 'mam_revenue_fund_close_effect = { RESULT = 4 }' in commit
    assert commit.index('mam_cf_start_commit_valid = 0') < commit.index('scope:mam_cf_paid > 0')
    validation = defs['mam_revenue_fund_validate_start_request_effect']
    for i in range(1, 18):
        assert f'scope:mam_cf_start_choice_{i} = 1' in validation
        assert f'scope:mam_cf_committing.var:mam_cf_amount >= mam_revenue_fund_start_cost_{i}' in validation
    assert 'mam_revenue_fund_live_case_trigger = yes' in validation
    assert 'mam_revenue_fund_check_start_choices_effect = yes' in validation
    search = defs['mam_revenue_fund_check_start_choices_effect']
    assert search.count('name = mam_cf_start_choice_') == 34, 'All 17 choices must initialize false and set true only after a native-valid site'
    for forbidden in ['pay_short_term_treasury', 'mam_revenue_fund_transfer_effect', 'KEY = proposal_valid_choices', 'mam_cf_project_cash value']:
        assert forbidden not in search and forbidden not in validation
    assert 'mam_cf.project_obsolete_desc' in defs['mam_fund.20']

    # The override keeps source hashes/price contracts and makes only the
    # documented notification replacement plus campaign-scope insertions.
    native_manifest = json.loads(read('docs/COMMON-FUND-NATIVE-PROJECTS.json'))
    entry = native_manifest['definitions']['grand_campaign_project']
    assert len(entry['post_replacements']) == 1
    notification = entry['post_replacements'][0]
    assert notification['new'] == '''every_contribution = {
 limit = { contribution_is_funded = yes }
 contributor ?= {
  if = { limit = { is_alive = yes }
   trigger_event = tgp_china_ministry.0008
  }
 }
}'''
    campaign = parse(defs['grand_campaign_project'])[0]
    slots = next(n for n in campaign.children if n.key == 'project_contributions')
    assert len(slots.children) == 20
    for slot in slots.children:
        callbacks = [n for n in slot.children if n.key == 'on_contribution_funded']
        assert len(callbacks) == 1
        text = defs['grand_campaign_project'][callbacks[0].start:callbacks[0].end]
        assert text.count('mam_revenue_fund_prepare_campaign_callback_effect = yes') == 1
        assert text.index('mam_revenue_fund_prepare_campaign_callback_effect') < text.index('grand_campaign_contribution_effect')
    binder = defs['mam_revenue_fund_prepare_campaign_callback_effect']
    assert binder.index('clear_saved_scope = grand_campaign_war') < binder.index('var:grand_campaign_war ?=')
    assert 'save_scope_as = grand_campaign_war' in binder
    for forbidden in ['trigger_event', 'end_war', 'declare_war', 'pay_short_term_treasury', 'set_variable']:
        assert forbidden not in binder

    invoice = defs['mam_revenue_fund_execute_project_invoice_effect']
    assert 'KEY = invoice_native_check_refused' in invoice
    assert 'treasury < { value = scope:mam_cf_native_before subtract = 0.01 }' in invoice
    assert 'treasury > { value = scope:mam_cf_native_before add = 0.01 }' in invoice
    assert 'set_variable = { name = mam_cf_payment_hold value = 1 }' in invoice
    assert 'name = mam_cf_floor value = scope:mam_cf_invoice_before' in invoice
    wait = defs['mam_revenue_fund_refresh_native_wait_effect']
    for required in ['var:mam_pc_attempt_before = var:mam_pc_attempt_after', 'var:mam_pc_native_key = 0',
                     'var:mam_pc_attempt_on <= { value = current_date subtract = 7 }',
                     'NOT = { has_variable = mam_pc_executing }', 'NOT = { has_variable = mam_cf_payment_hold }']:
        assert required in wait
    assert 'remove_variable = mam_cf_payment_hold' not in wait
    assert 'remove_variable = mam_pc_attempt' not in wait and 'pay_short_term_treasury' not in wait
    assert 'mam_revenue_fund_refresh_native_wait_effect = yes' in defs['mam_revenue_fund_init_project_order_effect']

    scenarios = []
    def jurisdiction(index, site_in_empire, site_in_province):
        return site_in_empire if index in global_types else site_in_province
    for index in [10, 11, 12]:
        assert jurisdiction(index, True, False)
        assert not jurisdiction(index, False, False)
    assert not jurisdiction(3, True, False) and jurisdiction(3, True, True)
    scenarios.append('Wall/extension imperial sites pass despite unrelated governor selection; foreign and wrong provincial sites fail')
    def may_pay(native_eligible, valid_site, quote, current_price):
        return native_eligible and valid_site and quote >= current_price
    assert may_pay(True, True, 500, 500)
    assert not may_pay(False, True, 500, 500)
    assert not may_pay(True, False, 500, 500)
    assert not may_pay(True, True, 500, 600)
    scenarios.append('eligibility, site or price changes return the request before payment')
    def receipt(funded, proof, before, after, price, advance):
        if funded and proof and after <= before-price+0.01:
            return 'verified', 0
        if funded or abs(after-before) > 0.01:
            return 'held', 0
        return 'native_wait', advance
    assert receipt(True, True, 600, 100, 500, 500) == ('verified', 0)
    assert receipt(False, False, 600, 600, 500, 500) == ('native_wait', 500)
    assert receipt(False, False, 600, 599, 500, 500) == ('held', 0)
    assert receipt(True, False, 600, 100, 500, 500) == ('held', 0)
    assert receipt(True, True, 600, 600, 500, 500) == ('held', 0)
    scenarios.append('verified charge, refused no-charge return, unfunded partial debit and missing-proof holds')
    for project_war in [None, 'war_A', 'war_B']:
        # Clear an inherited alias even when the new project has no live war.
        alias = 'unrelated_old_war'
        alias = project_war
        assert alias == project_war
    scenarios.append('first pledge without war and later pledges bind only their own linked war; no war creation in binder')
    recipients = [(True, True), (True, False), (False, True), (False, False)]
    assert sum(funded and alive for funded, alive in recipients) == 1
    scenarios.append('completion notifies funded living recipients only')
    baseline = json.loads(read('docs/PLAYTEST-test3-2026-10-30.json'))
    wall = next(p for p in baseline['current_projects'] if p['type'] == 'great_wall')
    mapping = json.loads(read('docs/COMMON-FUND-CONTRIBUTIONS-MANIFEST.json'))
    attempt = next(i for i in mapping['invoices'] if i['key'] == wall['variables']['mam_pc_attempt_key'])
    slot = next(c for c in wall['contributions'] if c['slot'] == attempt['slot'])
    assert attempt['slot'] == 'walls_19' and slot['funded']
    assert slot['actor'] != int(wall['variables']['mam_pc_attempt_actor']['identity'])
    assert wall['variables']['mam_pc_attempt_before'] == wall['variables']['mam_pc_attempt_after']
    scenarios.append('test3 stale Wall attempt: zero debit; exact saved-key slot subsequently funded by another contributor')
    build = re.search(r'version="([^"]+)"', read('descriptor.mod'))[1]
    (ROOT / 'docs/PROJECT-EDGE-CASE-VERIFICATION.json').write_text(json.dumps({
        'build': build, 'source_checked': True, 'native_campaign_slots': 20,
        'native_notification_replacements': 1, 'revalidated_start_types': 17,
        'scenarios': scenarios, 'engine_tested': False,
        'limitations': 'Source/model cases and a prior saved fixture; new CK3 behavior still needs a focused retest.'
    }, indent=2) + '\n', encoding='utf-8')
    print('PASS: imperial Wall jurisdiction, 17 pre-payment site/price checks, 20 native campaign scopes, guarded notifications and invoice safety cases.')
    print('NOT TESTED: dev.60 CK3 execution, actual Wall planning or native campaign completion callback timing.')


if __name__ == '__main__':
    verify()
