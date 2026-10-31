"""Source and accounting-contract checks; not a CK3 engine emulator."""
from __future__ import annotations

import hashlib
import json
import re
import runpy
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT / 'tools/verify_revenue_source.py'))['parse']
safety = runpy.run_path(str(ROOT / 'tools/revenue_safety_contracts.py'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_checks():
    baseline = json.loads((ROOT/'docs/COMMON-FUND-BASELINE.json').read_text())
    protected = {p:h for p,h in baseline['files'].items() if 'revenue' not in Path(p).name.lower()}
    for relative, old_hash in protected.items():
        assert digest(ROOT/relative) == old_hash, f'Unrelated gameplay changed: {relative}'
    legacy = json.loads((ROOT/'docs/REVENUE-IMPLEMENTATION-AUDIT.json').read_text())
    for relative, old_hash in legacy['protected_existing_hashes'].items():
        assert digest(ROOT/relative) == old_hash, f'Personnel/pre-Revenue asset changed: {relative}'

    files = [p for folder in ('common','events','localization') for p in (ROOT/folder).rglob('*')
             if p.is_file() and 'revenue' in p.name and p.suffix in {'.txt','.yml'}]
    definitions = {}
    texts = {}
    loc = {}
    for path in files:
        assert path.read_bytes().startswith(b'\xef\xbb\xbf'), path
        text = path.read_text(encoding='utf-8-sig')
        texts[path] = text
        if path.suffix == '.yml':
            for line in text.splitlines()[1:]:
                if not line.strip() or line.lstrip().startswith('#'): continue
                match = re.fullmatch(r' ([\w.]+):0 (".*")',line)
                assert match, (path,line)
                assert match[1] not in loc, match[1]
                loc[match[1]] = json.loads(match[2])
        else:
            for node in parse(text):
                if node.children:
                    assert node.key not in definitions, f'Duplicate definition {node.key}'
                    definitions[node.key] = (path,node,text[node.start:node.end])

    new_text = '\n'.join(t for p,t in texts.items() if 'common' in p.name and p.suffix=='.txt')
    event_ids = {k for k in definitions if re.fullmatch(r'mam_fund\.\d+',k)}
    for event in set(re.findall(r'\bmam_fund\.\d+\b',new_text)):
        assert event in event_ids, event
    for key in set(re.findall(r'\bmam_cf\.[\w]+',new_text)):
        assert key in loc, f'Missing localization {key}'
    bound = set(re.findall(r'save_(?:temporary_)?scope_as\s*=\s*(mam_cf_\w+)',new_text))
    bound |= set(re.findall(r'save_(?:temporary_)?scope_value_as\s*=\s*\{\s*name\s*=\s*(mam_cf_\w+)',new_text))
    assert not set(re.findall(r'scope:(mam_cf_\w+)',new_text))-bound, 'Never-bound scope'
    for k,(p,n,text) in definitions.items():
        if not k.startswith('mam_revenue_fund_'): continue
        params = set(re.findall(r'\$([A-Z_]+)\$',text))
        for op,(_,top,_) in definitions.items():
            for child in top.walk():
                if child is top or child.key != k: continue
                if params:
                    assert {c.key for c in child.children} == params, (k,op)
                    assert all(not c.children for c in child.children), ('Inline macro argument',k,op)
    # The model has no custom currency, title transfers, personal-gold payment,
    # candidate-score mutation or judicial runtime in its authored boundaries.
    safety_outputs = {r['output'] for r in json.loads((ROOT/'tools/templates/revenue_native_campaign_safety.json').read_text(encoding='utf-8'))['records']}
    # These exact native outputs have separately pinned original source hashes
    # and reviewed patches; all authored fiscal code keeps the stricter boundary.
    authored = '\n'.join(t for p,t in texts.items() if 'revenue_common' in p.name
                         and 'native_spending' not in p.name and 'native_obligations' not in p.name and 'great_projects' not in p.parts
                         and p.relative_to(ROOT).as_posix() not in safety_outputs
                         and p.suffix=='.txt')
    for forbidden in ('add_gold','remove_gold','add_treasury','remove_treasury','change_title_holder',
                      'change_liege','mam_personnel_','mam_senior_','mam_cj_record_'):
        assert not re.search(r'\b'+forbidden,authored), forbidden
    cash = definitions['mam_revenue_fund_transfer_effect'][2]
    assert cash.count('pay_short_term_treasury') == 1
    assert 'scope:mam_cf_payer != scope:mam_cf_payee' in cash
    assert 'mam_cf_payment_hold' in cash and 'mam_cf_debit > 0' in cash and 'mam_cf_credit > 0' in cash
    for k,(p,top,text) in definitions.items():
        if not k.startswith(('mam_revenue_fund_','mam_fund.')): continue
        for node in top.walk():
            if node.key == 'pay_short_term_treasury':
                assert k == 'mam_revenue_fund_transfer_effect' or any(a.key == 'show_as_tooltip' for a in ancestors(node)), k
    actor = definitions['mam_revenue_fund_actor_trigger'][2]
    for check in ('mam_cf_generation','mam_cf_stage','mam_revenue_officer_trigger','mam_revenue_fund_imperial_trigger'):
        assert check in actor, check
    commit = definitions['mam_revenue_fund_legacy_commit_effect'][2]
    dispatcher = definitions['mam_revenue_fund_commit_effect'][2]
    assert 'var:mam_cf_kind = 13' in dispatcher and 'mam_revenue_fund_commit_project_budget_effect' in dispatcher
    for check in ('mam_revenue_fund_live_case_trigger','mam_revenue_fund_imperial_trigger',
                  'mam_revenue_fund_delegated_trigger','mam_cf_consent','mam_cf_project_cash = 0',
                  'subtract = var:mam_cf_issued'):
        assert check in commit, check
    assert 'scope:mam_cf_' not in '\n'.join(t for p,t in texts.items() if p.parent.name=='customizable_localization')
    assert all('ERROR:' not in value for k,value in loc.items() if k.startswith('mam_cf.'))
    # Regressions identified in the user's dev.49 engine log. Script scope
    # notation is not localization data syntax; ai_chance.base is numeric.
    cf_loc={k:v for k,v in loc.items() if k.startswith('mam_cf.')}
    assert not any('[scope:' in v for v in cf_loc.values()), 'Script syntax in localization'
    assert not re.search(r'\bhidden_trigger\s*=',new_text), 'Unsupported CK3 trigger wrapper'
    used_loc=set(re.findall(r'\[(mam_cf_\w+)', '\n'.join(cf_loc.values())))
    assert not used_loc-bound, ('Unbound localization data',used_loc-bound)
    for event in event_ids:
        for chance in (n for n in definitions[event][1].walk() if n.key=='ai_chance'):
            for base in (n for n in chance.children if n.key=='base'):
                assert re.fullmatch(r'-?\d+(?:\.\d+)?',base.value), (event,base.value)
    assert 'current_heir' not in definitions['mam_fund.5'][2]
    for name,(path,node,body) in definitions.items():
        if path.name=='mam_revenue_common_opinions.txt' and 'decaying = yes' in body:
            assert any(n.key in {'years','months','days','monthly_change'} for n in node.children), name
    for name in ('relief','supplement','project','contribution','topup','remit','debt',
                 'programme_result','operations_result','refused_result','paid_result',
                 'reserved_result','supplement_self_result','unpaid_result'):
        # Generous space allowance for expanded localized character/title names.
        body=re.sub(r'\[[^\]]+\]','NAME',loc['mam_cf.'+name+'_desc'])
        assert len(body.split())<=55, ('Letter too long',name)
    sweep=definitions['mam_revenue_fund_sweep_effect'][2]
    refill=definitions['mam_revenue_fund_refill_effect'][2]
    assert sweep.index('mam_revenue_fund_transfer_effect = yes') < sweep.index('add = scope:mam_cf_paid')
    assert refill.index('mam_revenue_fund_transfer_effect = yes') < refill.index('name = mam_cf_statement_received')
    month=definitions['mam_revenue_fund_month_effect'][2]
    assert month.index('name = mam_cf_recording_statement') < month.index('mam_revenue_fund_sweep_effect = yes')
    assert month.index('remove_variable = mam_cf_recording_statement') > month.rindex('mam_revenue_fund_refill_effect')
    for eid in ('mam_fund.11','mam_fund.12','mam_fund.13'):
        assert 'desc = mam_cf.departments_all' in definitions[eid][2]
        assert 'mam_cf.next_accounts' not in definitions[eid][2]
        assert 'mam_cf.previous_accounts' not in definitions[eid][2]
    assert loc['mam_cf.departments_all'].count("GetPlayer.Custom('MamRevenueFundDepartment")==9
    assert 'mam_cf_fund_balance' not in loc['mam_cf.accounts_desc'], 'Account cash must not depend on saved event values'
    assert "GetPlayer.Custom('MamRevenueFundAuthority')" in loc['mam_cf.accounts_desc']
    assert 'mam_cf.statement_none' in new_text
    essential_count=definitions['mam_revenue_fund_count_essential_effect'][2]
    assert 'mam_cf_remaining' not in essential_count, 'Essential need must survive an exhausted discretionary cap'
    assert 'mam_cf_remaining > 0' not in refill, 'Essential payment blocked by discretionary cap'
    refill_node=definitions['mam_revenue_fund_refill_effect'][1]
    for node in refill_node.walk():
        if node.key in {'change_variable','max'} and (node.value=='var:mam_cf_remaining' or
                any(c.key=='name' and c.value in {'mam_cf_remaining','mam_cf_issued'} for c in node.children)):
            assert any(a.key=='if' and any(c.key=='always' and c.value=='$EXTRA$' for c in a.walk()) for a in ancestors(node)), 'Discretionary ledger charged for essential payroll'
    service_cost=definitions['mam_revenue_fund_service_cost'][2]
    assert 'min = holder.mam_revenue_fund_observed_cost' in service_cost
    assert 'value = var:mam_cf_cost' in service_cost
    assert 'mam_revenue_fund_service_cost multiply = 2' in definitions['mam_revenue_fund_target'][2]
    assert 'mam_cf_payroll_due <= current_date' in definitions['mam_revenue_fund_payroll_effect'][2]
    assert 'days = 7' in definitions['mam_revenue_fund_payroll_effect'][2]
    assert 'mam_revenue_fund_sweep_effect' not in definitions['mam_revenue_fund_payroll_effect'][2]
    assert 'mam_revenue_fund_ensure_payroll_effect' in definitions['mam_revenue_fund_start_effect'][2]
    initiative=definitions['mam_revenue_fund_initiative_effect'][2]
    project_call=next(n for n in definitions['mam_revenue_fund_initiative_effect'][1].walk()
                      if n.key=='random_vassal_or_below' and 'id = mam_fund.96' in texts[definitions['mam_revenue_fund_initiative_effect'][0]][n.start:n.end])
    assert project_call.parent is definitions['mam_revenue_fund_initiative_effect'][1], 'Project requests still restricted to quarterly initiatives'
    location=definitions['mam_revenue_fund_project_location_trigger'][1]
    primary=next(n for n in location.children if n.key=='primary_title')
    capital=next(n for n in primary.walk() if n.key in {'trigger_if','trigger_else_if'} and any(c.key=='limit' and any(v.key=='var:mam_cf_project_type' and v.value=='9' for v in c.children) for c in n.children))
    provincial=next(n for n in primary.walk() if n.key=='trigger_else')
    assert any(n.key=='has_variable' and n.value=='mam_cf_project_type' for n in primary.children), 'Empty native project previews must not fetch missing grant type'
    cap_limit=next(n for n in capital.children if n.key=='limit')
    assert any(n.key=='var:mam_cf_project_type' and n.value=='9' for n in cap_limit.children)
    assert any(n.key=='top_liege' and n.value=='title:h_china.holder' for n in capital.walk())
    assert not any(n.key.startswith('var:mam_cf_project_target') for n in capital.walk()), 'Capital still tied to a provincial grant target'
    border=next(n for n in primary.walk() if n.key=='trigger_if' and any(c.key=='limit' and any(v.key=='var:mam_cf_project_type' and v.value=='1' for v in c.children) for c in n.children))
    assert any(n.key=='var:mam_cf_project_type' and n.value=='1' for n in border.walk())
    assert any(n.key=='any_neighboring_county' for n in border.walk()), 'Campaign grant still excludes authorized exterior border sites'
    assert any(n.key=='is_vassal_or_below_of' for n in provincial.walk()), 'Provincial grants lost their jurisdiction constraint'
    request=definitions['mam_revenue_fund_open_project_effect'][2]
    assert 'name = mam_cf_project_target value = title:h_china' in request
    start=definitions['mam_revenue_fund_project_start_trigger'][2]
    for guard in ('var:mam_cf_project_type = $TYPE$','var:mam_cf_project_until > current_date','var:mam_cf_project_cash >= scope:mam_cf_required_start_cost','mam_cf_payment_hold'):
        assert guard in start, ('Project authorization weakened',guard)
    # Project price expressions use character/council/income properties. They
    # must be evaluated before changing to the grant-storing title's scope.
    for key,temp in [('mam_revenue_fund_project_start_trigger','mam_cf_required_start_cost'),
                     ('mam_revenue_fund_contribution_trigger','mam_cf_required_contribution_cost')]:
        node=definitions[key][1]
        price=next(n for n in node.children if n.key=='save_temporary_scope_value_as')
        title=next(n for n in node.children if n.key=='primary_title')
        assert price.start<title.start and any(n.key=='value' and n.value=='$COST$' for n in price.children)
        assert any(n.key=='var:mam_cf_project_cash' and n.value=='scope:'+temp for n in title.walk())
        assert not any(n.value=='$COST$' for n in title.walk()), 'Character price evaluated inside title scope'
    prepare=definitions['mam_revenue_fund_prepare_project_budget_effect'][2]
    assert 'from = budget_short_term to = budget_long_term' in prepare
    assert 'mam_revenue_fund_transfer_effect' not in prepare
    assert 'mam_revenue_fund_prepare_project_budget_effect = yes' in commit
    # Evaluate the actual installed price-expression AST with fixed base-cost
    # fixtures. This is a price-scope regression, not a CK3 engine emulator.
    def fixture_price(children,councillor,value=0.):
        base={'great_project_base_contribution_cost':250.,'great_project_base_starting_cost':500.}
        def number(n):return base[n] if n in base else float(n)
        for n in children:
            if n.key=='value':value=number(n.value)
            elif n.key=='multiply':value*=number(n.value)
            elif n.key=='divide':value/=number(n.value)
            elif n.key=='if':
                gate=next(c for c in n.children if c.key=='limit')
                assert all(c.key=='is_councillor' and c.value=='yes' for c in gate.children)
                if councillor:value=fixture_price([c for c in n.children if c is not gate],councillor,value)
            else:raise AssertionError(('Unhandled cost fixture operation',n.key))
        return value
    for index in (3,4):
        expression=definitions[f'mam_revenue_fund_start_cost_{index}'][1]
        actual=fixture_price(expression.children,True)
        wrong_scope=fixture_price(expression.children,False)
        assert actual==500 and wrong_scope==1000
        assert 500>=actual and not 500>=wrong_scope
    for eid in ('mam_fund.1','mam_fund.8'):
        assert 'mam_cf.project_request_3' in definitions[eid][2]
    assert 'mam_cf.project_paid_3' in definitions['mam_fund.20'][2]

    manifest = json.loads((ROOT/'docs/COMMON-FUND-NATIVE-PROJECTS.json').read_text())
    for path, sha in manifest['native_files'].items():
        assert digest(Path(path)) == sha, f'Installed native source changed: {path}'
    for key, entry in manifest['definitions'].items():
        source = Path(entry['native_source']).read_text(encoding='utf-8-sig')
        native = next(n for n in parse(source) if n.key==key)
        original = source[native.start:native.end]
        assert hashlib.sha256(original.encode()).hexdigest()==entry['original_sha256']
        expected = original
        for edit in sorted(entry['insertions'],key=lambda e:(e['at'],e['text']),reverse=True):
            at=edit['at']; expected=expected[:at]+edit['text']+expected[at:]
        expected = safety['apply_project_replacements'](key, expected, entry.get('post_replacements', []))
        assert definitions[key][2] == expected, f'Native project parity: {key}'
        if any('mam_revenue_fund_project_start_trigger' in e['text'] for e in entry['insertions']):
            assert not any('text = mam_cf.project_authorization_tt' in e['text'] for e in entry['insertions']), 'Opaque grant condition restored'
    for key, entry in manifest['contribution_costs'].items():
        expr = definitions[key][2].split('=',1)[1].strip()
        assert expr == entry['native_expression'], f'Contribution cost drift: {key}'
    development=definitions['minister_project_development'][2]
    assert 'treasury < 20000' in development and 'TYPE = 3 COST = mam_revenue_fund_start_cost_3' in development
    assert development.index('a paid matching project grant') < development.index('culture = {'), 'Readiness bonus must preserve subsequent native zero multipliers'
    native = json.loads((ROOT/'docs/COMMON-FUND-NATIVE-INTERACTIONS.json').read_text())
    source=Path(native['source']).read_text(encoding='utf-8-sig')
    for key,entry in native['definitions'].items():
        node=next(n for n in parse(source) if n.key==key)
        assert hashlib.sha256(source[node.start:node.end].encode()).hexdigest()==entry['sha256']
        assert entry['original_accept_body'] in definitions[key][2]
        assert 'mam_cf.native_payment_guard_tt' in definitions[key][2]
    obligation=json.loads((ROOT/'docs/COMMON-FUND-NATIVE-OBLIGATIONS.json').read_text())
    source=Path(obligation['native_source']).read_text(encoding='utf-8-sig')
    original=next(n for n in parse(source) if n.key==obligation['definition'])
    expected=source[original.start:original.end]
    assert hashlib.sha256(expected.encode()).hexdigest()==obligation['native_sha256']
    for edit in sorted(obligation['insertions'],key=lambda e:(e['at'],e['text']),reverse=True):
        at=edit['at']; expected=expected[:at]+edit['text']+expected[at:]
    assert definitions[obligation['definition']][2]==expected, 'Native insurance bridge drift'
    claims=definitions['mam_revenue_fund_claim_commit_effect'][2]
    assert 'mam_revenue_fund_transfer_effect = yes' in claims
    assert 'scope:mam_cf_paid > 0' in claims and 'scope:mam_cf_uncertain = 1' in claims
    assert 'any_in_list' not in definitions['mam_revenue_fund_create_claim_effect'][2], 'Distinct vested payments must not collapse into one claim'
    assert 'has_variable = mam_cf_insurance_claim' in definitions['mam_revenue_fund_insurance_claim_effect'][2]
    assert 'mam_revenue_fund_custodian_trigger' in definitions['mam_revenue_fund_ready_trigger'][2]
    assert 'mam_cf_bootstrap_until' in definitions['mam_revenue_fund_start_effect'][2]
    assert 'OR = { var:mam_cf_kind = 3 var:mam_cf_kind = 9 var:mam_cf_kind = 13 }' in definitions['mam_revenue_fund_delegated_trigger'][2], 'Programme limits must cover legacy and project-scoped contributions'
    assert 'min = var:mam_cf_cost' in definitions['mam_revenue_fund_start_effect'][2], 'Opening baseline must not clamp settled expenses to zero'
    assert 'has_variable = mam_cf_clear_debt' in definitions['mam_revenue_fund_live_case_trigger'][2]
    assert 'var:mam_cf_target.holder.treasury multiply = -1' in commit
    for event in ['mam_fund.1','mam_fund.2','mam_fund.3','mam_fund.4','mam_fund.8']:
        assert 'name = mam_cf.changed' in definitions[event][2], f'Stale window has no exit: {event}'
    for k in ['mam_revenue_interactions.txt','mam_revenue_decisions.txt']:
        source=next(t for p,t in texts.items() if p.name==k)
        for n in parse(source):
            shown=next(c for c in n.children if c.key=='is_shown')
            assert 'always = no # retired common-fund entry' in source[shown.start:shown.end]
    return {'protected_files':len(protected),'module_files':len(files),'events':len(event_ids),
            'native_project_definitions':len(manifest['definitions']),
            'native_contribution_costs':len(manifest['contribution_costs']),
            'engine_log_regressions':'localization, numeric AI base, atomic macro arguments, scope type, opinion duration, letter length, statement guards',
            'funding_regressions':'essential/discretionary separation, current bills, weekly lease, monthly AI proposals, funded Works readiness',
            'capital_regressions':'TYPE 9 imperial realm, provincial jurisdiction retained, imperial request target, authorization guards intact',
            'project_scope_regressions':'Character-priced start/contribution checks before title scope; actual native Develop/Control cost fixtures; explicit grant reasons and project names; conserved AI budget preparation'}


def ancestors(node):
    while node.parent:
        node=node.parent
        yield node


@dataclass
class Office:
    cash: float
    cost: float=0
    headroom: float=75
    project: float=0
    remaining: float=1000
    issued: float=0

    @property
    def target(self): return 2*self.cost+self.headroom+self.project


def accounting_contracts():
    """Independent small examples of the financial rules, not CK3 execution."""
    tests=[]
    def check(name, condition):
        assert condition, name
        tests.append(name)
    def transfer(accounts, payer, payee, amount, floor=0):
        if payer==payee or amount<=0 or accounts[payer]-amount<floor: return False
        before=sum(accounts.values())
        accounts[payer]-=amount; accounts[payee]+=amount
        assert abs(sum(accounts.values())-before)<1e-8
        return True
    accounts={'imperial':2000.,'revenue':500.,'works':0.}
    accounts['works']+=90 # a single native receipt
    check('Native receipts counted once',sum(accounts.values())==2590)
    transfer(accounts,'works','revenue',15,floor=75)
    check('Pooling does not charge emperor',accounts['imperial']==2000 and sum(accounts.values())==2590)
    transfer(accounts,'imperial','revenue',200,floor=500)
    check('Additional appropriation is conserved',accounts['imperial']==1800 and sum(accounts.values())==2590)
    office=Office(200,cost=10,headroom=40,project=80)
    check('Project cash excluded from sweep',office.cash-office.target==60)
    office=Office(45,cost=10,headroom=40,remaining=20)
    refill=min(max(0,office.target-office.cash),office.remaining)
    office.cash+=refill; office.remaining-=refill; office.issued+=refill
    check('Only missing working balance refilled',refill==15 and office.remaining==5)
    check('Unspent advance cannot be granted twice',max(0,office.target-office.cash)==0)
    office.cash-=20
    refill=min(max(0,office.target-office.cash),office.remaining)
    check('Quarterly limit survives repeated spending',refill==5)
    office.issued=90
    new_authorization=max(0,office.headroom-office.issued)
    check('Review cannot reset previously issued advances',new_authorization==0)
    # A native project charge reduces cash and earmark together, leaving the
    # operating shortfall unchanged. It is not a second charge to the fund.
    office=Office(560,cost=10,headroom=40,project=500)
    before_gap=office.target-office.cash
    office.cash-=500; office.project-=500
    check('Project charge does not generate operating refill',office.target-office.cash==before_gap)
    common=1000; earmark=500
    check('Revenue self-project reserves without self-transfer',common==1000 and common-earmark==500)
    a={'fund':500.,'ministry':0.}
    check('Protected balances cannot be breached',not transfer(a,'fund','ministry',501))
    check('Self-transfer refused',not transfer(a,'fund','fund',1))
    check('No payment on refusal',a=={'fund':500.,'ministry':0.})
    # Scarcity is apportioned on the full need, not on the cash left after the
    # first office is processed: two equal needs receive equal advances.
    needs=[20,20]; available=20; shares=[int(available*n/sum(needs)) for n in needs]
    check('Equal essential needs share shortage equally',shares==[10,10] and sum(shares)<=available)
    # Receipt tolerance must require a real debit and credit, including for tiny
    # transfers where a fixed tolerance alone could falsely accept zero.
    def verified(amount,debit,credit):
        return amount>0 and debit>0 and credit>0 and abs(debit-amount)<=.01 and abs(credit-amount)<=.01
    check('Zero native debit is never success',not verified(.005,0,0))
    check('Asymmetric native transfer is not success',not verified(100,0,100))
    check('Exact native debit and credit are success',verified(100,100,100))
    debt=250.25; authorized=1000
    check('Debt payment capped at remaining debt',min(authorized,debt)==250.25)
    check('Previously settled debt needs no second payment',max(-0.,0)==0)
    obligations=[1000,1000]
    check('Separate earned native benefits remain payable',sum(obligations)==2000)
    # Rites' reported failure: no discretionary allowance left, genuine monthly
    # bills still due, and a solvent common bank. Essential cash is uncapped by
    # that discretionary ledger and is a real conserved bank-to-office payment.
    def essential_need(cash,approved,observed,project=0):
        return max(0,2*max(approved,observed)+project-cash)
    accounts={'fund':20000.,'rites':-30.}; remaining=0
    due=essential_need(accounts['rites'],10,40)
    check('Rites payroll survives exhausted discretionary cap',remaining==0 and due==110)
    transfer(accounts,'fund','rites',due,floor=200)
    check('Debt and two months of actual bills funded conservatively',accounts=={'fund':19890.,'rites':80.} and sum(accounts.values())==19970)
    check('Repeated weekly check cannot pay a second full advance',essential_need(accounts['rites'],10,40)==0)
    check('Current raised-army bills enlarge the safety buffer',essential_need(100,30,300)==500)
    check('Project reserves remain outside disposable operating cash',essential_need(80,10,40,500)==500)
    # Rejected or still-pending projects cannot supply the funded AI bonus.
    def readiness(grant,required,kind,match,treasury):
        return 70 if grant>=required and kind==match and treasury<20000 else 0
    check('Paid matching Works grant replaces hoard-only bonus',readiness(200,200,3,3,275)==70)
    check('Unfunded or mismatched grant adds no readiness bonus',readiness(0,200,3,3,75)==0 and readiness(500,200,2,3,575)==0)
    check('Native wealth bonus is not added twice',readiness(500,200,3,3,20000)==0)
    check('Later native war/culture zeroes still win',(30+readiness(200,200,3,3,275))*0==0)
    return tests


if __name__=='__main__':
    source=source_checks()
    contracts=accounting_contracts()
    build=re.search(r'version="([^"]+)"',(ROOT/'descriptor.mod').read_text()).group(1)
    report={'build':build,'source_checks':source,
            'accounting_contract_checks':contracts,
            'engine_tested':False,
            'not_tested':['engine commands and treasury buckets','rendering and letter layout',
                          'native salary timing','great-project callback timing and scope',
                          'observer AI balance','save migration and title-linked treasury succession']}
    (ROOT/'docs/COMMON-FUND-VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:',json.dumps(source))
    print(f'PASS: {len(contracts)} accounting-contract examples (not an engine simulation).')
    print('NOT TESTED: CK3 engine execution, UI, native expense timing, save migration and AI balance.')
