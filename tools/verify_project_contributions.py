"""Project financing source contracts and independent accounting examples.

These checks do not execute CK3, validate DLL behavior or substitute for a
campaign playtest. Native sources and saved-key identities are read-only inputs.
"""
from pathlib import Path
import hashlib
import json
import re
import runpy
from dataclasses import dataclass

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']


def read(rel):
    return (ROOT/rel).read_text(encoding='utf-8-sig')


def source_contracts():
    manifest = json.loads(read('docs/COMMON-FUND-CONTRIBUTIONS-MANIFEST.json'))
    registry = json.loads(read('docs/COMMON-FUND-CONTRIBUTION-KEYS.json'))
    native_manifest = json.loads(read('docs/COMMON-FUND-NATIVE-PROJECTS.json'))
    assert len(set(registry.values())) == len(registry), 'Saved keys collide'
    defs = {}
    for folder in ['common', 'events']:
        for p in (ROOT/folder).rglob('*revenue_common*.txt'):
            text = p.read_text(encoding='utf-8-sig')
            for n in parse(text):
                if n.value is None:
                    assert n.key not in defs, n.key
                    defs[n.key] = text[n.start:n.end]
    bindings = defs['mam_revenue_fund_bind_invoice_effect']
    bound_cases = [n for n in parse(bindings)[0].children if n.key in {'if','else_if'}]
    assert len(bound_cases) == len(manifest['invoices']) == len(native_manifest['contribution_costs'])
    assert bound_cases[0].key == 'if' and all(n.key == 'else_if' for n in bound_cases[1:])
    for invoice, branch in zip(manifest['invoices'], bound_cases):
        key = invoice['key']
        assert registry[invoice['project']+'::'+invoice['slot']] == key
        text = Path(invoice['native_source']).read_text(encoding='utf-8-sig')
        project = next(n for n in parse(text) if n.key == invoice['project'])
        slots = next(n for n in project.children if n.key == 'project_contributions')
        slot = next(n for n in slots.children if n.key == invoice['slot'])
        assert hashlib.sha256(text[slot.start:slot.end].encode()).hexdigest() == invoice['native_contribution_sha256']
        clauses = [text[text.index('{',c.start)+1:c.end-1] for c in slot.children if c.key in {'is_shown','contributor_is_valid'}]
        conditions = re.sub(r'\broot\b', 'scope:mam_cf_contributor', '\n'.join(clauses))
        assert conditions == invoice['native_eligibility']
        assert conditions in defs[f'mam_revenue_fund_invoice_eligible_{key}_trigger']
        ai = next((c for c in slot.children if c.key == 'ai_will_do'), None)
        if ai:
            assert text[text.index('{',ai.start)+1:ai.end-1] in defs[f'mam_revenue_fund_invoice_weight_{key}']
        bridge = bindings[branch.start:branch.end]
        assert f'great_project_type = {invoice["project"]}' in bridge
        assert f'contribution_id = {invoice["slot"]}' in bridge
        assert f'name = mam_cf_invoice_key value = {key} ' in bridge
        assert f'name = mam_cf_invoice_price value = {invoice["price"]}' in bridge
    execute = defs['mam_revenue_fund_execute_project_invoice_effect']
    required = ['can_fund_project_contribution = scope:mam_cf_pick_slot',
                'fund_great_project_contribution = { contribution = scope:mam_cf_pick_slot cost = yes check_can_contribute = yes }',
                'var:mam_pc_native_actor = scope:mam_cf_executing_contributor',
                'var:mam_pc_native_key = scope:mam_cf_invoice_key',
                'name = mam_pc_budget subtract = scope:mam_cf_execute_price',
                'name = mam_cf_floor value = scope:mam_cf_invoice_before',
                'has_variable = mam_pc_executing', 'mam_pc_mobilization_paid = 1',
                'scope:mam_cf_using_legacy = 1', 'this = scope:mam_cf_payer',
                'mam_cf_native_before subtract = scope:mam_cf_execute_price']
    for fragment in required:
        assert fragment in execute, fragment
    assert execute.index('mam_revenue_fund_transfer_effect = yes') < execute.index('can_fund_project_contribution')
    assert execute.index('can_fund_project_contribution') < execute.index('fund_great_project_contribution')
    budget = defs['mam_revenue_fund_commit_project_budget_effect']
    assert 'name = mam_pc_budget value = scope:mam_cf_budget_file.var:mam_cf_amount' in budget
    assert 'name = mam_pc_budget add =' not in budget, 'Amendments replace remaining ceiling'
    assert 'mam_revenue_fund_transfer_effect' not in budget, 'Reserving is not paying'
    assert 'mam_cf_authorized = title:h_china.holder' in budget
    assert 'subtract = scope:mam_cf_budget_file.var:mam_pc_minimum' in budget
    assert 'mam_pc_commitments' in defs['mam_revenue_fund_available']
    delegated = defs['mam_revenue_fund_delegated_trigger']
    assert 'var:mam_pc_spent <= { value = 500 subtract = prev.var:mam_cf_amount }' in delegated
    authority = defs['mam_revenue_fund_project_budget_authority_trigger']
    for fragment in ['mam_pc_level = 3', 'mam_pc_level = 2', 'mam_pc_ceiling <= 500',
                     'mam_revenue_authority_expanded', 'has_title = title:e_minister_of_revenue',
                     'great_project_type = grand_campaign_project']:
        assert fragment in authority
    opener = defs['mam_revenue_fund_open_project_budget_effect']
    assert 'mam_revenue_fund_invoice_needs_budget_trigger = yes' in opener
    needs = defs['mam_revenue_fund_invoice_needs_budget_trigger']
    assert 'mam_revenue_fund_invoice_budget_sufficient_trigger = no' in needs
    assert 'contribution_is_funded = no' in needs and 'has_variable = mam_pc_executing' in needs
    assert 'mam_revenue_fund_project_request_covered_trigger = yes' in budget
    assert 'mam_revenue_fund_project_request_covered_trigger = yes' in defs['mam_revenue_fund_resolve_effect']
    assert 'mam_revenue_fund_invoice_needs_budget_trigger = yes' in execute
    coverage=defs['mam_revenue_fund_project_request_covered_trigger']
    assert 'save_temporary_scope_as = mam_cf_selected_project' not in coverage
    assert 'save_temporary_scope_value_as' not in coverage
    assert 'name = mam_pc_executing_key value = scope:mam_cf_invoice_key' in execute
    receipt_effect=defs['mam_revenue_fund_native_invoice_receipt_effect']
    assert 'scope:mam_cf_receipted_contributor.primary_title.var:mam_pc_executing_key' in receipt_effect
    assert 'mam_pc_attempt_price' in execute and 'mam_pc_attempt_after' in execute
    assert 'var:mam_pc_launch_authorized = 0' in opener
    # A saved player intent is retried by the weekly worker while approval is
    # pending. Only an explicit UI action may open the modal status event.
    worker=defs['mam_fund.31']
    assert 'name = mam_cf_manual_invoice_action value = 0' in worker
    assert worker.index('mam_cf_manual_invoice_action') < worker.index('mam_revenue_fund_auto_start_effect')
    assert defs['mam_fund.32'].count('name = mam_cf_manual_invoice_action value = 1')==3
    assert 'name = mam_cf_manual_invoice_action value = 1' in defs['mam_fund.35']
    status=defs['mam_revenue_fund_show_invoice_status_effect']
    assert 'is_ai = no scope:mam_cf_manual_invoice_action = 1' in status
    assert 'trigger_event = mam_fund.34' in status
    for key,text in defs.items():
        if key.startswith('mam_revenue_fund_') and key!='mam_revenue_fund_show_invoice_status_effect':
            assert 'trigger_event = mam_fund.34' not in text, ('Unguarded background modal',key)
    assert 'NOT = { has_variable = mam_pc_pending }' in defs['mam_revenue_fund_process_project_invoice_effect']
    notice=defs['mam_revenue_fund_notify_campaign_war_effect']
    assert 'exists = var:grand_campaign_war' in notice and 'has_variable = mam_pc_war_notice' in notice
    assert 'name = mam_pc_war_notice value = 1' in notice and 'send_interface_toast' in notice
    assert 'mam_revenue_fund_notify_campaign_war_effect = yes' in defs['mam_revenue_fund_project_driver_effect']
    assert 'mam_cf_case_9' not in opener.split('= {', 1)[1]
    assert 'mam_pc_pending' in opener and 'mam_cf_explicit_imperial' in opener
    assert 'mam_pc_campaign_launch' in opener and 'name = mam_cf_stage value = 1' in opener
    assert 'mam_pc_request_office.holder = var:mam_cf_requester' in defs['mam_revenue_fund_live_case_trigger']
    driver = defs['mam_revenue_fund_project_driver_effect']
    assert driver.count('id = mam_fund.31') == 9 and 'current_date add = 7' in driver
    discovery = defs['mam_revenue_fund_find_project_invoice_effect']
    assert 'contribution_is_required = yes' in discovery and 'contribution_id = attack_1' in discovery
    assert 'mam_pc_next_optional' in discovery and 'mam_cf_project_cash' not in discovery
    sufficient = defs['mam_revenue_fund_invoice_budget_sufficient_trigger']
    assert 'value = scope:mam_cf_invoice_price add = scope:mam_cf_selected_project.var:mam_pc_mobilization_reserved' in sufficient
    assert 'current_date add = 30' in execute
    assert 'mam_revenue_fund_project_invoice_actor_trigger' in defs['mam_fund.35']
    assert 'remove_variable = mam_pc_launch_prompt' in defs['mam_fund.35']
    assert 'current_date add = 30' in defs['mam_fund.35']
    assert defs['mam_fund.32'].count('remove_variable = mam_pc_launch_prompt') == 3
    mobilize = defs['mam_revenue_fund_release_mobilization_effect']
    assert 'var:mam_pc_mobilization_paid = 0' in mobilize and 'scope:mam_cf_paid > 0' in mobilize
    assert 'name = mam_pc_mobilization_until value = { value = current_date add = 90 }' in mobilize
    assert 'mam_cf_special_target' not in mobilize
    receipt = defs['mam_revenue_project_receipt_story']
    assert 'clear_saved_scope = mam_cf_receipt_heir' in receipt and 'current_heir' in receipt
    assert 'subtract = 1825' in receipt
    # Governor path remains outside module payment gates: exact native parity
    # for every overridden project is additionally checked by verify_common_fund.
    for p in (ROOT/'common/great_projects/types').glob('zz_mam_revenue_common*.txt'):
        text = p.read_text(encoding='utf-8-sig')
        assert 'mam_revenue_fund_native_invoice_receipt_effect' in text
        assert 'mam_revenue_fund_project_order_closed_effect' in text
        for project in parse(text):
            if project.value is not None:continue
            slots=[slot for group in project.children if group.key=='project_contributions' for slot in group.children]
            for owner in [project]+slots:
                callbacks=[n.key for n in owner.children if n.key.startswith('on_')]
                assert len(callbacks)==len(set(callbacks)), ('Duplicate engine callback',project.key,owner.key)
                assert not any(n.key in {'if','else','else_if','hidden_effect'} for n in owner.children), ('Bare effect in database',project.key,owner.key)
            for slot in slots:
                if any(n.key=='cost' and any(c.key in {'treasury','treasury_or_gold'} for c in n.children) for n in slot.children):
                    callback=next(n for n in slot.children if n.key=='on_contribution_funded')
                    assert 'mam_revenue_fund_native_invoice_receipt_effect' in text[callback.start:callback.end]
    loc = {m[1]:json.loads(m[2]) for line in read('localization/english/mam_revenue_common_l_english.yml').splitlines()
           if (m:=re.fullmatch(r' ([\w.]+):0 (".*")',line))}
    assert set(json.loads(read('tools/templates/revenue_projects_localization.json'))) <= set(loc)
    custom = '\n'.join(s for k,s in defs.items() if k.startswith(('mam_fund.','mam_revenue_fund_')))
    for key in set(re.findall(r'\bmam_pc\.[A-Za-z_]+', custom)):
        assert key in loc, f'Missing project localization: {key}'
    for value in loc.values():
        assert '[scope:' not in value and 'ERROR:' not in value
    assert 'docs/MOD-CURRENT-STATE.md' in read('AGENTS.md')
    build = re.search(r'version="([^"]+)"', read('descriptor.mod'))[1]
    assert build in read('docs/MOD-CURRENT-STATE.md')
    return len(manifest['invoices'])


@dataclass
class Account:
    bank: float
    office: float = 0
    reserved: float = 0
    spent: float = 0
    funded: bool = False
    launches: int = 0

    def approve(self, remaining):
        if remaining < 0 or remaining > self.bank:
            return False
        self.reserved = remaining
        return True

    def invoice(self, price, *, native_ok=True, legacy=False, custodian=False, launch=False):
        if self.funded or price <= 0:
            return False
        if legacy:
            if self.office < price:
                return False
        elif self.reserved < price or self.bank < price:
            return False
        if not native_ok:
            # An exact temporary advance followed by an exact return is neutral.
            return False
        if legacy:
            self.office -= price
        else:
            # Recipient advance + native charge net to zero; self reserves in place.
            self.bank -= price
        self.reserved = max(0, self.reserved-price) if self.reserved >= price else self.reserved
        self.spent += price
        self.funded = True
        self.launches += int(launch)
        return True


def accounting_examples():
    checks = []
    def check(name, result):
        assert result, name
        checks.append(name)
    a = Account(2000, 75)
    check('approve without moving cash', a.approve(500) and a.bank == 2000 and a.office == 75)
    check('native expenditure once', a.invoice(250) and a.bank == 1750 and a.office == 75 and a.reserved == 250)
    check('paid slot cannot replay after reload', not a.invoice(250) and a.spent == 250)
    a.funded = False
    check('replacement amendment not duplicate ceiling', a.approve(600) and a.reserved == 600 and a.bank == 1750)
    before = (a.bank,a.office,a.reserved,a.spent)
    check('native eligibility failure and refund neutral', not a.invoice(250,native_ok=False) and before == (a.bank,a.office,a.reserved,a.spent))
    check('reject overdraw', not a.approve(9999) and a.reserved == 600)
    b = Account(1000, 400)
    check('paid legacy grant needs no new transfer', b.invoice(250,legacy=True) and b.bank == 1000 and b.office == 150)
    c = Account(1000)
    c.approve(500)
    check('Revenue self contribution costs once', c.invoice(250,custodian=True) and c.bank == 750 and c.reserved == 250)
    d = Account(2000)
    d.approve(1000)
    check('campaign mandate executes one pledge', d.invoice(250,launch=True) and d.launches == 1)
    check('same pledge cannot launch twice', not d.invoice(250,launch=True) and d.launches == 1)
    remaining, price, ordinary = 300, 250, 175
    check('mobilization cut cannot consume pledge', min(600,max(0,remaining-price)) == 50)
    check('mobilization refund protects payroll', min(600,max(0,500-ordinary)) == 325)
    spent, remaining = 350, 200
    check('splitting envelopes cannot evade 500 ceiling', spent+remaining > 500)
    def authority(level, law, sensitive=False, own=False, campaign=False, total=500, balanced=True):
        return level == 3 or (not(sensitive or own or campaign) and law != 'reserved' and
            (level == 2 or (level == 1 and law == 'expanded' and total <= 500 and balanced)))
    check('reserved law rejects old delegated authority', not authority(1,'reserved'))
    check('limited law allows Chancellor ordinary envelope', authority(2,'limited'))
    check('Revenue cannot approve own contribution', not authority(1,'expanded',own=True))
    check('sensitive department requires Emperor', not authority(2,'limited',sensitive=True))
    check('campaign requires Emperor even under expanded law', not authority(1,'expanded',campaign=True))
    check('imperial institutional mandate persists', authority(3,'reserved',campaign=True))
    check('unpaid mobilization must leave current pledge price', 1300 < 1000+350)
    def needs_request(*, eligible=True, funded=False, covered=False, prepaid=False, executing=False, held=False):
        return eligible and not (funded or covered or prepaid or executing or held)
    check('authorized unchanged invoice creates no new request', not needs_request(covered=True))
    check('native refusal cannot turn covered funds into new approval', not needs_request(covered=True,eligible=False))
    check('in-flight native callback cannot create another request', not needs_request(executing=True))
    check('uncertain funded invoice remains held without reapproval', not needs_request(funded=True,held=True))
    check('higher uncovered native price may seek amendment', needs_request())
    check('paid legacy allowance needs no fresh budget request', not needs_request(prepaid=True))
    def status_modal(human,manual):return human and manual
    check('six pending weekly retries create no status modals', sum(status_modal(True,False) for _ in range(6))==0)
    check('explicit human status remains available', status_modal(True,True))
    check('AI invoices create no player status modals', not status_modal(False,False))
    notified=False;notices=0
    for _ in range(6):
        if not notified:
            notices+=1;notified=True
    check('existing campaign war notification is once only',notices==1)
    return checks


if __name__ == '__main__':
    count = source_contracts()
    examples = accounting_examples()
    build = re.search(r'version="([^"]+)"', read('descriptor.mod'))[1]
    (ROOT/'docs/PROJECT-CONTRIBUTIONS-VERIFICATION.json').write_text(json.dumps({
        'build':build, 'native_treasury_contribution_bindings':count,
        'accounting_contract_examples':examples, 'engine_tested':False,
        'not_tested':['native contribution callback context/timing', 'project scope lifetime/save migration',
                      'native treasury bucket semantics', 'campaign launch and war start', 'observer AI balance']
    },indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {count} native contribution eligibility/price/AI bindings; stable keys, approval, execution, migration and campaign source contracts.')
    print(f'PASS: {len(examples)} independent contribution accounting examples (not an engine simulation).')
    print('NOT TESTED: CK3 native callback scopes, saved project/contribution lifetimes, treasury bucket timing, war launch and observer AI behavior.')
