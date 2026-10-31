"""Read-only dev.66 Justice contracts; no claim of CK3 execution/AI acceptance.

Native facts in the predicate tests are supplied inputs. The evaluator fails on
unsupported syntax instead of assuming an accusation or missing fact is true.
"""
from pathlib import Path
import copy
import hashlib
import json
import re
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']
MISSING = object()
DEFS = {}; TEXTS = {}; LOC = {}


def load():
    DEFS.clear(); TEXTS.clear(); LOC.clear()
    paths = [p for base in ('common','events','localization') for p in (ROOT/base).rglob('*')
             if p.is_file() and 'mam_justice' in p.name and p.suffix in ('.txt','.yml')]
    for p in paths:
        assert p.read_bytes().startswith(b'\xef\xbb\xbf'), p
        text = p.read_text(encoding='utf-8-sig'); TEXTS[p] = text
        if p.suffix == '.yml':
            assert text.startswith('l_english:\n')
            for line in text.splitlines()[1:]:
                if not line.strip(): continue
                m=re.fullmatch(r' ([\w.]+):0 (".*")',line); assert m,(p,line)
                assert m[1] not in LOC,m[1]; LOC[m[1]]=json.loads(m[2])
        else:
            for n in parse(text):
                if n.value is not None: continue
                assert n.key not in DEFS,(p,n.key)
                DEFS[n.key]=(p,n)
    return paths


def body(name):
    p,n=DEFS[name]; return TEXTS[p][n.start:n.end]


def source_checks():
    paths=load()
    script='\n'.join(s for p,s in TEXTS.items() if p.suffix=='.txt')
    clean=re.sub(r'#[^\n]*','',script)
    for ref in re.findall(r'\bmam_justice[\w.]*',clean):
        assert ref=='mam_justice' or ref in DEFS or ref in LOC,('Undefined Justice reference',ref)
    for ref in re.findall(r'\bmam_jus\.[\w.]+',clean): assert ref in LOC,ref
    bound=set(re.findall(r'save_(?:temporary_)?scope_as\s*=\s*(mam_jus_\w+)',script))
    bound |= set(re.findall(r'save_scope_value_as\s*=\s*{\s*name\s*=\s*(mam_jus_\w+)',script))
    used=set(re.findall(r'\bscope:(mam_jus_\w+)',script))
    assert used<=bound,('Never bound',used-bound)
    macros={name:set(re.findall(r'\$([A-Z_]+)\$',body(name))) for name in DEFS if name.startswith('mam_justice')}
    for name,(p,top) in DEFS.items():
        for n in top.walk():
            if n is not top and n.key in macros and macros[n.key]:
                assert {c.key for c in n.children}==macros[n.key],(name,n.key,macros[n.key])
            if n.key=='option' and name.startswith('mam_justice.') and name!='mam_justice.90':
                txt=TEXTS[p][n.start:n.end]
                guard=next(c for c in n.children if c.key=='trigger')
                assert any(c.key=='mam_justice_actor_trigger' for c in guard.children),name
                if 'mam_jus.stale' not in txt:
                    commit=next(c for c in n.children if c.key=='if' and any(x.key=='hidden_effect' for x in c.children))
                    limit=next(c for c in commit.children if c.key=='limit')
                    assert TEXTS[p][guard.start:guard.end].split('{',1)[1].rsplit('}',1)[0].strip()==TEXTS[p][limit.start:limit.end].split('{',1)[1].rsplit('}',1)[0].strip(),name
    for key,text in LOC.items():
        assert '[scope:' not in text,('Script scope in localization',key)
        assert 'ERROR:' not in text and '\ufffd' not in text,key
        assert text.count('#bold ')+text.count('#high ')+text.count('#weak ')<=text.count('#!'),key
    for template in (ROOT/'tools/templates/justice').glob('*.txt'):
        for block in template.read_text(encoding='utf-8').split('@@ ')[1:]:
            rel,s=block.split('\n',1)
            assert (ROOT/rel.strip()).read_text(encoding='utf-8-sig')==s.strip()+'\n',('Generated/template mismatch',rel)
    # Native executable bridges are compared to installed definitions, not a
    # mutable expected output copied from this implementation.
    native=runpy.run_path(str(ROOT/'tools/build_justice.py'))
    sources=native['native_sources'](ROOT)
    for i,key in {1:'imprison_interaction',2:'pardon_interaction',3:'release_from_prison_interaction',4:'execute_prisoner_interaction'}.items():
        s,n=sources[key]; accept=next(x for x in n.children if x.key=='on_accept')
        original=native['inner'](s,accept)
        expected=re.sub(r'\broot\b','scope:mam_jus_performer',original).strip()
        p,exe=DEFS[f'mam_justice_native_execute_{i}_effect']
        assert native['inner'](TEXTS[p],exe).strip()==expected,('Native acceptance drift',key)
        override=DEFS[key][1]
        accepted=next(c for c in override.children if c.key=='on_accept')
        wrapper=next(c for c in accepted.children if c.key=='if')
        keys=[c.key for c in wrapper.children]
        assert keys[0:2]==['limit','mam_justice_native_begin_effect'] and keys[-2:]==['mam_justice_native_observed_effect','mam_justice_native_end_effect'],key
        # Remove only the explicitly authorized wrapper/hooks; every original
        # native acceptance token remains in order.
        inner_nodes=wrapper.children[2:-2]
        original_nodes=accept.children
        assert len(inner_nodes)==len(original_nodes),key
        for a,b in zip(inner_nodes,original_nodes):
            assert TEXTS[DEFS[key][0]][a.start:a.end]==s[b.start:b.end],(key,a.key)
        cost=next((c for c in n.children if c.key=='cost'),None)
        if cost:
            for c in cost.children:
                expected=native['inner'](s,c) if c.children else 'value = '+c.value
                expected=re.sub(r'\broot\b','scope:mam_jus_performer',expected).strip()
                p,v=DEFS[f'mam_justice_cost_{i}_{c.key}']
                assert native['inner'](TEXTS[p],v).strip()==expected,(key,c.key)
    # The actual transaction pays once, then executes once. Native validity
    # includes affordability, so checking it AFTER the debit would strand fees.
    commit=body('mam_justice_commit_effect'); paid=body('mam_justice_execute_paid_effect')
    assert commit.index('mam_justice_native_valid_trigger = no')<commit.index('remove_treasury =')<commit.index('mam_justice_execute_paid_effect = yes')
    assert 'mam_justice_native_valid_trigger' not in paid
    assert 'mam_jus_cost_paid' in paid and 'mam_jus_executed' in paid
    assert 'var:mam_jus_confirmed = 0' in paid and 'RESULT = 10' in paid
    assert 'remove_treasury = scope:mam_jus_cost_treasury' in commit
    assert 'mam_jus_before_treasury subtract = scope:mam_jus_cost_treasury' in commit
    assert 'KIND = 12 AMOUNT = scope:mam_jus_cost_treasury' in commit
    # Only the deliberately compiled native bodies can perform punishment.
    for name,(p,n) in DEFS.items():
        if not name.startswith('mam_justice') or '_native_execute_' in name: continue
        for x in n.walk():
            assert x.key not in ('imprison','release_from_prison','death','change_title_holder','create_character','add_secret','add_treasury','add_imprisonment_reason'),(name,x.key)
    assert 'mam_jus_transaction' in body('mam_justice_tick_effect')
    assert 'mam_justice_dispatch_commit_effect = yes' in body('mam_justice_tick_effect')
    assert 'mam_justice_commit_effect = yes' not in body('mam_justice_tick_effect')
    assert 'trigger_event = mam_justice.11' in body('mam_justice_dispatch_commit_effect')
    assert 'scope:mam_jus_performer = root' in body('mam_justice.11')
    assert 'mam_justice_current_judge_trigger = yes' in commit
    assert 'mam_jus_pending_death' in body('mam_justice_tick_effect')
    assert 'mam_jus_pending_death' in paid
    recovery=body('mam_justice_recover_transaction_effect')
    assert 'STAGE = 4' in recovery and 'native_execute_' not in recovery
    assert 'mam_justice_offer_valid_trigger = no' in commit
    assert 'var:mam_jus_offer_author = var:mam_jus_judge' in paid
    assert 'mam_jus_approved_authority' in body('mam_justice_authorized_trigger')
    assert 'mam_jus_warrant_sources' in commit and 'mam_jus_statute_started' in body('mam_justice_evidence_base_trigger')
    assert 'mam_jus_approved_offense' in body('mam_justice_authorized_trigger')
    assert 'mam_jus_proposed_offense' not in body('mam_justice_bind_effect')
    assert 'mam_jus_proposed_offense' not in body('mam_justice_native_bind_effect')
    assert 'imprisonment_reason = yes' in body('mam_jus_imperial_warrant')
    assert all(x not in body('mam_jus_imperial_warrant') for x in ('execution_reason','banishment_reason','revoke_title_reason'))
    assert 'modifier = mam_jus_imperial_warrant' in body('mam_justice_pardon_warrant_effect')
    assert 'consume_all_criminal_reasons_effect' not in body('mam_justice_pardon_warrant_effect')
    assert 'mam_jus_receipt_review' in body('mam_justice_actor_trigger')
    assert 'mam_jus_appeal_used' in body('mam_justice_petition_effect')
    assert 'mam_justice_petition_effect = yes' in body('mam_justice_petition_decision')
    assert 'mam_jus_offer_void' in body('mam_justice_tick_effect')
    assert 'monthly_playable_pulse' not in script
    assert 'mam_cj_' not in clean
    assert 'version="0.4.0-alpha.20-dev.66"' in (ROOT/'descriptor.mod').read_text()
    return {'build':'0.4.0-alpha.20-dev.66','runtime_text_files':len(paths),'definitions':len(DEFS),
            'english_keys':len(LOC),'pinned_native_definitions':len(sources),'native_acceptance_and_cost_parity':True,
            'engine_execution':'NOT TESTED','visual_and_long_run_AI':'NOT TESTED'}


class Predicate:
    """Small evaluator of the ACTUAL source predicates and numeric values."""
    def __init__(self,scopes): self.scopes=scopes; self.previous=[]
    def resolve(self,key,env):
        if key in ('yes','no'): return key=='yes'
        try:return float(key)
        except (ValueError,TypeError):pass
        if key=='current_date':return self.scopes['date']
        if key=='prev':return self.previous[-1] if self.previous else MISSING
        if key in ('this','root'):return env if key=='this' else self.scopes['root']
        if key.startswith('scope:'):
            first,*rest=key[6:].split('.'); obj=self.scopes.get(first,MISSING)
        elif key.startswith('title:'):
            first,*rest=key.split('.');obj=self.scopes.get(first,MISSING)
        else:
            first,*rest=key.split('.');obj=env.get(first,MISSING) if isinstance(env,dict) else MISSING
        for field in rest:
            if not isinstance(obj,dict):return MISSING
            obj=obj.get(field,MISSING)
        if obj is MISSING and key in DEFS and 'values' in str(DEFS[key][0]):return self.number(DEFS[key][1].children,env)
        return obj
    def op(self,n):
        p,_=next((p,t) for p,t in DEFS.values() if n in t.walk())
        m=re.match(r'\S+\s*(\?=|>=|<=|!=|=|>|<)',TEXTS[p][n.start:n.end]);assert m,n.key
        return m[1]
    def equal(self,a,b):
        if a is MISSING or b is MISSING:return False
        return a is b if isinstance(a,dict) or isinstance(b,dict) else a==b
    def compare(self,a,b,op):
        if a is MISSING or b is MISSING:return False
        if op in ('=','?='):return self.equal(a,b)
        if op=='!=':return not self.equal(a,b)
        return {'>':lambda:a>b,'<':lambda:a<b,'>=':lambda:a>=b,'<=':lambda:a<=b}[op]()
    def holds(self,nodes,env):
        out=[];chain=None
        for n in nodes:
            k=n.key
            if k in ('trigger_if','trigger_else_if','trigger_else'):
                if k=='trigger_if':chain=False
                assert chain is not None
                take=not chain and (k=='trigger_else' or self.holds(next(x.children for x in n.children if x.key=='limit'),env))
                if take:out.append(self.holds([x for x in n.children if x.key!='limit'],env));chain=True
                continue
            chain=None
            if k=='OR':out.append(any(self.holds([c],env) for c in n.children))
            elif k=='AND':out.append(self.holds(n.children,env))
            elif k=='NOT':out.append(not self.holds(n.children,env))
            elif k=='exists':out.append(self.resolve(n.value,env) is not MISSING)
            elif k=='has_variable':out.append('var:'+n.value in env)
            elif k=='has_character_modifier':out.append(n.value in env.get('modifiers',set()))
            elif k=='has_realm_law':out.append(n.value in env.get('laws',set()))
            elif k=='has_character_flag':out.append(n.value in env.get('flags',set()))
            elif k=='has_trait':out.append(n.value in env.get('traits',set()))
            elif k=='story_type':out.append(env.get('story_type')==n.value)
            elif k=='save_temporary_scope_as':self.scopes[n.value]=env
            elif k=='any_owned_story':
                out.append(any(self.holds(n.children,story) for story in env.get('stories',[])))
            elif k in ('has_imprisonment_reason','has_execute_reason','has_banish_reason','has_revoke_title_reason'):
                target=self.resolve(n.value,env);out.append(target is not MISSING and target.get('id') in env.get(k,set()))
            elif k=='can_add_hook':out.append(env.get('can_add_hook',False))
            elif k=='has_hook':out.append(env.get('has_hook',False))
            elif k=='has_extra_criminal_reason_against_trigger':out.append(env.get(k,False))
            elif k=='is_close_or_extended_family_of':out.append(env.get(k,False))
            elif k in env and k.endswith('_trigger'):
                out.append(bool(env[k])==(n.value=='yes'))
            elif k.startswith('mam_justice') and k in DEFS:
                assert not n.children,('Unimplemented macro evaluator',k)
                out.append(self.holds(DEFS[k][1].children,env)==(n.value=='yes'))
            elif n.children:
                value=self.resolve(k,env)
                if isinstance(value,dict):
                    self.previous.append(env)
                    try:out.append(self.holds(n.children,value))
                    finally:self.previous.pop()
                else:out.append(False)
            else:
                out.append(self.compare(self.resolve(k,env),self.resolve(n.value,env),self.op(n)))
        return all(out)
    def number(self,nodes,env):
        value=0
        for n in nodes:
            if n.key=='if':
                if self.holds(next(x.children for x in n.children if x.key=='limit'),env):
                    # Numeric branch operates on the accumulated value.
                    value=self.number([type(n)('value',str(value),0,0)]+[x for x in n.children if x.key!='limit'],env)
                continue
            amount=self.number(n.children,env) if n.children else self.resolve(n.value,env)
            assert amount is not MISSING,(n.key,n.value)
            if n.key=='value':value=amount
            elif n.key=='add':value+=amount
            elif n.key=='subtract':value-=amount
            elif n.key=='multiply':value*=amount
            elif n.key=='min':value=max(value,amount)
            elif n.key=='max':value=min(value,amount)
            else:raise AssertionError(('Unsupported numeric clause',n.key))
        return value
    def test(self,name,env):return self.holds(DEFS[name][1].children,env)


class JusticeContracts(unittest.TestCase):
    def world(self):
        emperor={'id':'emperor','mam_justice_emperor_trigger':True,'laws':set()}
        judge={'id':'judge','mam_justice_officer_trigger':True,'modifiers':set(),'learning':12,'intrigue':10}
        subject={'id':'subject','is_alive':True,'is_adult':True,'is_diarch':False,'tgp_is_any_minister':False,
                 'is_close_or_extended_family_of':False,'diplomacy':10,'learning':10,'intrigue':10,'traits':set(),'gold':100}
        realm={'holder':emperor,'var:mam_jus_statute_started':100}
        case={'var:mam_jus_realm':realm,'var:mam_jus_judge':judge,'var:mam_jus_subject':subject,'var:mam_jus_action':4}
        scopes={'title:h_china':realm,'mam_jus_case':case,'mam_jus_subject':subject,'mam_jus_judge':judge,
                'mam_jus_performer':judge,'date':200,'root':judge}
        return Predicate(scopes),case,emperor,judge,subject
    def test_reserved_capital_requires_current_seal(self):
        p,c,e,j,s=self.world();self.assertFalse(p.test('mam_justice_authorized_trigger',c))
        c.update({'var:mam_jus_approved':1,'var:mam_jus_approver':e});self.assertTrue(p.test('mam_justice_authorized_trigger',c))
        c['var:mam_jus_realm']['holder']={'id':'new_emperor'};self.assertFalse(p.test('mam_justice_authorized_trigger',c))
    def test_ordinary_authority_changes_immediately_with_law(self):
        p,c,e,j,s=self.world();c['var:mam_jus_action']=1
        self.assertTrue(p.test('mam_justice_authorized_trigger',c))
        e['laws'].add('mam_justice_authority_reserved');self.assertFalse(p.test('mam_justice_authorized_trigger',c))
    def test_shadow_cannot_borrow_emperors_personal_powers(self):
        p,c,e,j,s=self.world();c.update({'var:mam_jus_action':1,'var:mam_jus_shadow':1});e['laws'].add('mam_justice_authority_reserved')
        self.assertTrue(p.test('mam_justice_authorized_trigger',c))
        p.scopes['mam_jus_performer']=e;self.assertFalse(p.test('mam_justice_authorized_trigger',c))
        p.scopes['mam_jus_performer']=j;j['modifiers'].add('mam_jus_restrained');self.assertFalse(p.test('mam_justice_authorized_trigger',c))
    def test_pardon_changed_authority_or_reason_category_requires_new_seal(self):
        p,c,e,j,s=self.world();e['laws'].add('mam_justice_authority_reserved')
        e['has_imprisonment_reason']={'subject'}
        p.scopes.update(mam_jus_pardon_authority=e,mam_jus_pardon_performer=e)
        c.update({'var:mam_jus_action':2,'var:mam_jus_approved':1,'var:mam_jus_approver':e,'var:mam_jus_approved_authority':e,'var:mam_jus_approved_reasons':1})
        self.assertTrue(p.test('mam_justice_authorized_trigger',c))
        e['has_execute_reason']={'subject'};self.assertFalse(p.test('mam_justice_authorized_trigger',c))
        e['has_execute_reason']=set();p.scopes['mam_jus_pardon_authority']=j;self.assertFalse(p.test('mam_justice_authorized_trigger',c))
    def test_free_native_action_does_not_require_positive_balances(self):
        p,c,e,j,s=self.world()
        for r in ('treasury','gold','prestige','piety','influence'):j[r]=-100;p.scopes['mam_jus_cost_'+r]=0
        self.assertTrue(p.test('mam_justice_native_affordable_trigger',c))
        p.scopes['mam_jus_cost_treasury']=1;self.assertFalse(p.test('mam_justice_native_affordable_trigger',c))
    def test_allegation_has_no_custom_criminal_force(self):
        p,c,e,j,s=self.world();c['var:mam_jus_source']={'var:mam_cen_subject':s,'var:mam_cen_obstruction':1}
        self.assertFalse(p.test('mam_justice_custom_evidence_trigger',c))
    def test_paid_appointment_must_be_actual_and_prospective(self):
        p,c,e,j,s=self.world()
        payment={'var:mam_patron_minister':s,'var:mam_patron_appointment':True,'var:mam_patron_appointed':120,'var:mam_patron_amount':100,'var:mam_patron_date':110}
        c['var:mam_jus_source']={'var:mam_cen_subject':s,'var:mam_cen_proof':1,'var:mam_cen_source':payment}
        self.assertTrue(p.test('mam_justice_custom_evidence_trigger',c))
        payment['var:mam_patron_date']=90;self.assertFalse(p.test('mam_justice_custom_evidence_trigger',c))
        payment['var:mam_patron_date']=110;payment.pop('var:mam_patron_appointment');self.assertFalse(p.test('mam_justice_custom_evidence_trigger',c))
    def test_judicial_corruption_requires_actual_personal_author(self):
        p,c,e,j,s=self.world();receipt={'var:mam_jus_offer_author':s,'var:mam_jus_offer_sent':1,'var:mam_jus_offer_date':150}
        c['var:mam_jus_source']={'var:mam_cen_subject':s,'var:mam_cen_judicial_proof':1,'var:mam_cen_judicial_record':receipt}
        self.assertTrue(p.test('mam_justice_custom_evidence_trigger',c))
        receipt['var:mam_jus_offer_author']=j;self.assertFalse(p.test('mam_justice_custom_evidence_trigger',c))
    def test_undated_or_old_false_certification_remains_administrative(self):
        p,c,e,j,s=self.world();source={'var:mam_cen_subject':s,'var:mam_cen_false_return':1,'var:mam_cen_return_exposed':1}
        c['var:mam_jus_source']=source
        self.assertFalse(p.test('mam_justice_custom_evidence_trigger',c))
        source['var:mam_cen_false_return_date']=90;self.assertFalse(p.test('mam_justice_custom_evidence_trigger',c))
        source['var:mam_cen_false_return_date']=110;self.assertTrue(p.test('mam_justice_custom_evidence_trigger',c))
    def test_private_agreement_does_not_pass_to_new_minister(self):
        p,c,e,j,s=self.world();c.update({'var:mam_jus_offer_author':j,'var:mam_jus_offer_kind':1})
        self.assertTrue(p.test('mam_justice_offer_valid_trigger',c))
        c['var:mam_jus_judge']={'id':'successor','mam_justice_officer_trigger':True};self.assertFalse(p.test('mam_justice_offer_valid_trigger',c))
    def test_skills_change_mitigation_not_proof(self):
        p,c,e,j,s=self.world();n=DEFS['mam_justice_mitigation_chance'][1]
        base=p.number(n.children,c);s['diplomacy']=20;self.assertGreater(p.number(n.children,c),base)
        s['diplomacy']=10;j['learning']=25;self.assertLess(p.number(n.children,c),base)
        self.assertFalse(p.test('mam_justice_custom_evidence_trigger',c))
    def test_deceit_meets_the_reviewers_intrigue(self):
        p,c,e,j,s=self.world();s['traits'].add('deceitful');s['intrigue']=25
        n=DEFS['mam_justice_mitigation_chance'][1];base=p.number(n.children,c)
        j['intrigue']=25;self.assertLess(p.number(n.children,c),base)
    def test_closed_receipts_cannot_enter_a_new_disposition_event(self):
        text=body('mam_justice_actor_trigger')
        assert 'mam_jus_receipt_review' in text and 'scope:mam_jus_expected = 4' in text
        petition=body('mam_justice_petition_effect')
        assert 'STAGE = 8' in petition and 'mam_jus_action value = 0' in petition
        assert 'mam_justice_native_execute_' not in petition
    def test_native_player_execution_waits_without_replaying_the_notice(self):
        text=body('mam_justice_pending_execution_effect')
        self.assertIn('death_reason = death_execution',text)
        self.assertIn('killer = scope:mam_jus_case.var:mam_jus_performer',text)
        self.assertNotIn('native_execute_',text)
        self.assertNotIn('remove_treasury',text)
        self.assertIn('RESULT = 4',text)
        self.assertIn('RESULT = 10',text)
    def test_native_helpers_execute_with_actual_performer_as_root(self):
        worker=body('mam_justice.11');commit=body('mam_justice_commit_effect')
        self.assertIn('scope:mam_jus_performer = root',worker)
        self.assertIn('var:mam_jus_serial = scope:mam_jus_token',worker)
        self.assertIn('mam_justice_current_judge_trigger = yes',commit)
    def test_departed_minister_cannot_commit_during_the_worker_handoff(self):
        p,c,e,j,s=self.world()
        self.assertTrue(p.test('mam_justice_current_judge_trigger',c))
        j['mam_justice_officer_trigger']=False
        self.assertFalse(p.test('mam_justice_current_judge_trigger',c))
    def test_own_petition_is_available_in_custody_but_only_once(self):
        p,c,e,j,s=self.world();s['top_liege']=e;s['is_imprisoned']=True
        c.update({'var:mam_jus_pending':1});s['var:mam_jus_case']=c
        # The actual live trigger checks the subject's unique institutional link.
        self.assertTrue(p.test('mam_justice_self_petition_trigger',s))
        c['var:mam_jus_appeal_used']=1
        self.assertFalse(p.test('mam_justice_self_petition_trigger',s))
    def test_petition_cannot_interrupt_an_accepted_native_execution(self):
        p,c,e,j,s=self.world();c['var:mam_jus_pending_death']=1
        self.assertFalse(p.test('mam_justice_petition_case_trigger',c))
        c.pop('var:mam_jus_pending_death');self.assertTrue(p.test('mam_justice_petition_case_trigger',c))
    def test_unpaid_gold_is_not_silently_converted_into_a_hook(self):
        p,n=DEFS['mam_justice_execute_paid_effect']
        branches=[x for x in n.walk() if x.key=='else_if' and any(c.key=='limit' and any(z.key=='var:mam_jus_offer_kind' and z.value=='2' for z in c.children) for c in x.children)]
        self.assertEqual(len(branches),1)
        self.assertIn('mam_jus_offer_unpaid',body('mam_justice_execute_paid_effect'))
    def test_unreported_private_demand_is_not_imperial_knowledge(self):
        p,c,e,j,s=self.world();c['var:mam_jus_offer_author']=j
        self.assertFalse(p.test('mam_justice_known_misconduct_trigger',c))
        c['var:mam_jus_offer_reported']=1
        self.assertTrue(p.test('mam_justice_known_misconduct_trigger',c))
    def test_censor_detection_must_reach_the_throne_before_knowledge(self):
        p,c,e,j,s=self.world()
        f={'story_type':'mam_censor_inspection_story','var:mam_cen_judicial_record':c,'var:mam_cen_judicial_proof':1,'var:mam_cen_imperial_seen':0}
        e['stories']=[f]
        self.assertFalse(p.test('mam_justice_known_misconduct_trigger',c))
        f['var:mam_cen_imperial_seen']=1
        self.assertTrue(p.test('mam_justice_known_misconduct_trigger',c))
    def test_warrant_cannot_consume_an_unproved_secondary_source(self):
        p,c,e,j,s=self.world()
        payment={'var:mam_patron_minister':s,'var:mam_patron_appointment':True,'var:mam_patron_appointed':120,'var:mam_patron_amount':100,'var:mam_patron_date':110}
        unproved={'var:mam_jus_offer_author':s,'var:mam_jus_offer_sent':1,'var:mam_jus_offer_date':150}
        source={'var:mam_cen_subject':s,'var:mam_cen_proof':1,'var:mam_cen_source':payment,'var:mam_cen_judicial_record':unproved,'var:mam_cen_judicial_proof':0}
        c['var:mam_jus_source']=source;c['var:mam_jus_proposed_offense']=unproved
        self.assertFalse(p.test('mam_justice_selected_offense_trigger',c))
        c['var:mam_jus_proposed_offense']=payment
        self.assertTrue(p.test('mam_justice_selected_offense_trigger',c))
    def test_a_changed_warrant_basis_requires_a_new_proposal_and_seal(self):
        p,c,e,j,s=self.world()
        source={'var:mam_cen_subject':s,'var:mam_cen_false_return':1,'var:mam_cen_return_exposed':1,'var:mam_cen_false_return_date':150}
        old={'id':'old_source'}
        c.update({'var:mam_jus_action':7,'var:mam_jus_source':source,'var:mam_jus_proposed_offense':old,'var:mam_jus_approved_offense':old,'var:mam_jus_approved':1,'var:mam_jus_approver':e})
        self.assertFalse(p.test('mam_justice_authorized_trigger',c))
        c['var:mam_jus_proposed_offense']=source
        self.assertFalse(p.test('mam_justice_authorized_trigger',c))
        c['var:mam_jus_approved_offense']=source
        self.assertTrue(p.test('mam_justice_authorized_trigger',c))


if __name__=='__main__':
    report=source_checks()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(JusticeContracts)
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
    report['actual_source_predicate_contract_tests']=result.testsRun
    (ROOT/'docs/JUSTICE-VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
