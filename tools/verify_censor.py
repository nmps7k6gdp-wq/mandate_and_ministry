"""Read-only Censorate source/lifecycle checks; NOT CK3 execution or AI testing."""
from pathlib import Path
import json
import re
import runpy
import unittest
import hashlib

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']


def source_checks():
    paths = [p for d in ('common', 'events', 'localization') for p in (ROOT/d).rglob('*')
             if p.is_file() and p.suffix in ('.txt', '.yml') and 'mam_censor' in p.name]
    assert len(paths) == 11, (len(paths), paths)
    texts = {}; trees = {}; loc = {}
    for p in paths:
        assert p.read_bytes().startswith(b'\xef\xbb\xbf'), p
        s = p.read_text(encoding='utf-8-sig'); texts[p] = s
        if p.suffix == '.yml':
            assert s.startswith('l_english:\n')
            for line in s.splitlines()[1:]:
                if not line.strip(): continue
                m = re.fullmatch(r' ([\w.]+):0 (".*")', line)
                assert m, (p, line)
                assert m[1] not in loc, m[1]
                loc[m[1]] = json.loads(m[2])
        else:
            trees[p] = parse(s)
    defs = {}; macros = {}
    for p, nodes in trees.items():
        for n in nodes:
            if n.value is not None: continue
            if n.key.startswith(('mam_censor', 'mam_cen_')):
                assert n.key not in defs, n.key
                defs[n.key] = (p, n)
                macros[n.key] = set(re.findall(r'\$([A-Z_]+)\$', texts[p][n.start:n.end]))
    script = '\n'.join(s for p, s in texts.items() if p.suffix == '.txt')
    clean = re.sub(r'#[^\n]*', '', script)
    for ref in re.findall(r'\bmam_censor[\w.]*\b', clean):
        if ref == 'mam_censor': continue
        assert ref in defs or ref in loc, f'Undefined module reference: {ref}'
    for ref in re.findall(r'\bmam_cen\.[\w.]+', clean):
        assert ref in loc, f'Missing localization: {ref}'
    bound = set(re.findall(r'save_(?:temporary_)?scope_as\s*=\s*(mam_cen_\w+)', script))
    bound |= set(re.findall(r'save_scope_value_as\s*=\s*{\s*name\s*=\s*(mam_cen_\w+)', script))
    used = set(re.findall(r'\bscope:(mam_cen_\w+)', script))
    assert used <= bound, f'Never-bound scopes: {used-bound}'
    for s in loc.values():
        assert '[scope:' not in s, 'CK3 localization needs DATA names, not script scope: syntax'
        assert not re.search(r'\[scope:[^\]]*\.var:', s), 'Nested script scope in localization; bind a named event scope instead'
        assert s.count('#bold ') + s.count('#high ') + s.count('#weak ') <= s.count('#!'), s
    for p, nodes in trees.items():
        for top in nodes:
            for n in top.walk():
                if n.key in macros and macros[n.key] and n is not top:
                    assert {c.key for c in n.children} == macros[n.key], (p, n.key, macros[n.key])
                if n.key == 'option' and top.key.startswith('mam_censor.') and top.key not in ('mam_censor.90', 'mam_censor.100'):
                    guard = next(c for c in n.children if c.key == 'trigger')
                    actor_guard = 'mam_censor_intel_actor_trigger' if top.key == 'mam_censor.101' else 'mam_censor_actor_trigger'
                    assert any(c.key == actor_guard for c in guard.children)
                    body = texts[p][n.start:n.end]
                    if 'mam_cen.stale' not in body:
                        conditional = next(c for c in n.children if c.key == 'if' and
                                           any(child.key == 'hidden_effect' for child in c.children))
                        limit = next(c for c in conditional.children if c.key == 'limit')
                        assert any(c.key == actor_guard for c in limit.children), top.key
                        # Other direct conditions are tooltip-only, never unguarded commits.
                        for other in n.children:
                            if other.key == 'if' and other is not conditional:
                                assert all(c.key in ('limit', 'custom_tooltip') for c in other.children), top.key
    # Never introduce alternate payment/candidate mutation or a criminal reason.
    forbidden = ('add_gold', 'add_treasury', 'remove_treasury', 'change_title_holder',
                 'imprison', 'add_secret', 'create_character', 'add_appointment_score',
                 'pay_treasury_to_gold', 'set_realm_law', 'mam_cj_open',
                 'add_imprisonment_reason','remove_imprisonment_reason','release_from_prison')
    for p, nodes in trees.items():
        for top in nodes:
            for n in top.walk():
                assert n.key not in forbidden, (p, n.key)
                if n.key in ('set_variable', 'change_variable', 'remove_variable'):
                    if n.value is not None: name = n.value
                    else: name = next((c.value for c in n.children if c.key == 'name'), '')
                    assert not name or name.startswith('mam_cen_'), (p, name)
    # All scheduling uses inspected native actions and an institutional story.
    support = (ROOT/'common/on_action/mam_censor_on_actions.txt').read_text(encoding='utf-8-sig')
    assert 'monthly_playable_pulse' not in support
    assert 'quarterly_playable_pulse' in support and 'on_game_start_after_lobby' in support
    effects = (ROOT/'common/scripted_effects/mam_censor_effects.txt').read_text(encoding='utf-8-sig')
    assert 'mam_senior_capture_effect = yes' in effects, 'Senior removal must preserve Personnel custody'
    assert 'mam_cen_retirement_office' in effects and 'mam_senior_pending = 1' in effects
    assert 'mam_cen_return_exposed' in effects
    assert 'scope:mam_cen_source_candidate' in effects
    triggers = (ROOT/'common/scripted_triggers/mam_censor_triggers.txt').read_text(encoding='utf-8-sig')
    assert 'var:mam_cen_serial = scope:mam_cen_token' in triggers
    assert 'var:mam_cen_stage = scope:mam_cen_expected' in triggers
    assert 'var:mam_cen_reviewer = root' in triggers
    assert 'primary_title = $OFFICE$' in triggers
    # Every dispatched stage exists, and every numbered stage has routing and a
    # guarded event; no sender/context depends on character-only Custom() text.
    routed = set(map(int, re.findall(r'trigger_event = mam_censor\.(\d+)', effects)))
    assert set(range(1, 13)) <= routed, routed
    for n in range(1, 13): assert f'mam_censor.{n}' in defs
    graph = {}; terminal = set()
    for number in range(1, 13):
        _, node = defs[f'mam_censor.{number}']; graph[number] = set()
        for child in node.walk():
            if child.key == 'mam_censor_move_effect':
                graph[number].add(int(next(c.value for c in child.children if c.key == 'STAGE')))
            elif child.key == 'mam_censor_examine_effect': graph[number].update((3, 12))
            elif child.key == 'mam_censor_close_effect': terminal.add(number)
    assert all(dst in graph for edges in graph.values() for dst in edges)
    for stage in graph:
        pending = [stage]; seen = set()
        while pending:
            here = pending.pop()
            if here in seen: continue
            seen.add(here); pending.extend(graph[here]-seen)
        assert seen & terminal, ('Stage has no closure path', stage)
    assert 'NOT = { has_variable = mam_cen_sanctioned }' in effects
    assert 'mam_cen_recused' in effects
    assert 'this != scope:mam_cen_subject' in triggers
    # Engine log 2026-10-31: creating a story and setting a variable do not run
    # during effect preview. Later preview branches must guard that state.
    assert 'if = { limit = { exists = scope:mam_cen_file }' in effects
    assert 'if = { limit = { has_variable = mam_cen_result }' in effects
    assert 'mam_censor_independent_check_effect' in effects
    assert 'mam_censor_test_denial_effect' in effects
    assert LOC_EXPECTED_ACCEPT in loc.values()
    assert 'ai_frequency = 0' not in (ROOT/'common/character_interactions/mam_censor_interactions.txt').read_text(encoding='utf-8-sig')
    # Check authors/templates plus the additive discovery template. Neither
    # generated runtime nor pinned native hashes are a substitute for sources.
    additions = {}
    for template in ('intelligence.txt','public_crime.txt'):
        for block in (ROOT/'tools/templates/censor'/template).read_text(encoding='utf-8').split('@@ ')[1:]:
            rel, body = block.split('\n', 1)
            rel=rel.strip()
            additions[rel] = additions.get(rel,'')+('\n\n' if rel in additions else '')+body.strip()
    for name, rel in [('triggers','common/scripted_triggers/mam_censor_triggers.txt'),
                      ('effects','common/scripted_effects/mam_censor_effects.txt')]:
        expected = (ROOT/f'tools/templates/censor/{name}.txt').read_text(encoding='utf-8').strip()
        expected += '\n\n'+additions[rel]
        assert (ROOT/rel).read_text(encoding='utf-8-sig').strip() == expected.strip(), rel
    for block in (ROOT/'tools/templates/censor/support.txt').read_text(encoding='utf-8').split('@@ ')[1:]:
        rel, body = block.split('\n', 1)
        rel = rel.strip(); expected = body.strip()
        if rel in additions: expected += '\n\n'+additions[rel]
        assert (ROOT/rel).read_text(encoding='utf-8-sig').strip() == expected.strip(), rel
    # Native boundaries are direct evidence, not invented engine API names.
    game = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game')
    native = (game/'events/dlc/ep3/ep3_decisions_events.txt').read_text(encoding='utf-8-sig')
    assert 'force_step_down_landed_titles = yes' in native
    assert 'fired_minister_position_effect = yes' in native
    registry = json.loads((ROOT/'docs/CENSOR-NATIVE-BOUNDARIES.json').read_text(encoding='utf-8'))
    for record in registry['definitions']:
        s = (game/record['source']).read_text(encoding='utf-8-sig')
        n = next(n for n in parse(s) if n.key == record['definition'])
        assert hashlib.sha256(s[n.start:n.end].encode('utf-8')).hexdigest() == record['sha256'], (
            'Native Censor boundary drift; compare the source before deliberately migrating the baseline', record['definition'])
    descriptor=(ROOT/'descriptor.mod').read_text(encoding='utf-8')
    integrated_build=re.search(r'version="([^"]+)"',descriptor)[1]
    assert integrated_build in ('0.4.0-alpha.20-dev.65','0.4.0-alpha.20-dev.66')
    intelligence_checks(defs, texts, loc)
    public_crime_checks(defs, texts, loc)
    print(f'Censor source checks passed: {len(paths)} files, {len(defs)} definitions, {len(loc)} localization keys. No engine claim.')
    return {'build':integrated_build, 'source_checked': True, 'engine_tested': False,
            'native_definitions_pinned':len(registry['definitions']),
            'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'definitions':len(defs), 'localization_keys':len(loc),
            'stage_edges':{str(k):sorted(v) for k,v in graph.items()},
            'not_tested':['CK3 script execution','event rendering','native handoffs','AI balance','save migration']}


LOC_EXPECTED_ACCEPT = 'The Dragon Throne has spoken. I will let the matter rest.'


def intelligence_checks(defs, texts, localization):
    def source(name):
        path, node = defs[name]
        return texts[path][node.start:node.end]
    actions = source('on_scheme_discovered') if 'on_scheme_discovered' in defs else next(
        s for p,s in texts.items() if p.name == 'mam_censor_on_actions.txt')
    assert 'on_scheme_discovered = { on_actions = { mam_censor_intel_plot_discovered } }' in actions
    assert 'on_secret_discovered' not in actions, 'Do not invent an undocumented native callback'
    poll = source('mam_censor_intel_poll_effect')
    assert 'random_known_secret' in poll and 'is_known_by = scope:mam_cen_intel_reader' in poll
    assert 'every_living_character' not in poll
    assert 'count >= 8' in poll
    secret_filter = source('mam_censor_intel_secret_trigger')
    assert set(__import__('re').findall(r'secret_type = (secret_\w+)', secret_filter)) == {
        'secret_siphoned_treasury','secret_embezzler','secret_exam_cheater','secret_request_incursion',
        'secret_coup_plotter','secret_murder','secret_murder_attempt'}
    assert 'mam_cen_intel_imperial_recorded' in secret_filter
    secret_capture = source('mam_censor_intel_capture_secret_effect')
    assert 'exists = var:mam_cen_intel_recorded' in secret_capture
    assert 'has_variable = mam_cen_sanctioned' in secret_capture
    assert 'mam_censor_live_trigger = yes' in secret_capture
    assert 'name = mam_cen_intel_recorded value = scope:mam_cen_new_intel' in secret_capture
    capture = source('mam_censor_intel_capture_plot_effect')
    assert 'name = mam_cen_identified value = 0' in capture
    assert 'host = title:h_china.holder' in capture
    assert 'exists = scheme_target_character' in capture
    assert 'scheme_target_character ?=' not in capture[:capture.index('clear_saved_scope')]
    trace = source('mam_censor_intel_resolve_trace_effect')
    assert 'every_scheme' in trace and 'is_scheme_exposed = yes' in trace
    assert 'var:mam_cen_intel_recorded = scope:mam_cen_intel_lead' in trace
    assert 'exists = scope:mam_cen_live_plot' in trace
    assert 'var:mam_cen_tracer = title:e_minister_censor.holder' in trace
    assert 'name = mam_cen_trace_finished value = 1' in trace
    assert 'name = mam_cen_suspect' not in trace, 'Tracing must not invent a different culprit'
    bind = source('mam_censor_intel_bind_effect')
    assert 'var:mam_cen_identified = 1' in bind
    assert 'clear_saved_scope = mam_cen_intel_subject' in bind
    for text in localization.values():
        assert '[mam_cen_hidden_suspect' not in text, 'Unidentified plot author leaked in localization'
    event = source('mam_censor.101')
    assert 'character = scope:mam_cen_hidden_suspect' not in event
    tick = source('mam_censor_intel_tick_effect')
    assert 'var:mam_cen_subject = scope:mam_cen_intel_lead.var:mam_cen_suspect' in tick
    assert 'mam_censor_move_effect = { STAGE = 2 DAYS = 7 }' in tick
    assert 'var:mam_cen_imperial_seen = 0' in tick
    assert 'NOT = { exists = var:mam_cen_active }' in tick
    assert 'mam_cen_intel_brief' in tick and 'add = 90' in tick
    attach = source('mam_censor_intel_attach_effect')
    assert 'mam_cen_native_fact' in attach and 'mam_censor_intel_finish_effect = yes' in attach
    assert 'name = mam_cen_inspection value = scope:mam_cen_file' in attach
    actor = source('mam_censor_intel_actor_trigger')
    for required in ('var:mam_cen_serial = scope:mam_cen_intel_token',
                     'var:mam_cen_reviewer = root', 'root = { mam_censor_emperor_trigger = yes }'):
        assert required in actor
    assert 'end_story' not in attach, 'Keep the dated source snapshot until its archive lifetime'


def evaluate_chance(name, env):
    """Evaluate the arithmetic/trait subset in actual chance ScriptValues.

    This is a narrow source evaluator, not an imitation of CK3 event execution.
    Unsupported syntax fails rather than silently passing an imagined result.
    """
    path = ROOT/'common/script_values/mam_censor_values.txt'
    node = next(n for n in parse(path.read_text(encoding='utf-8-sig')) if n.key == name)
    def scalar(value):
        try: return float(value)
        except ValueError:
            actor, stat = value.rsplit('.', 1)
            return env[actor][stat]
    def holds(nodes, actor=None):
        outcomes = []
        for n in nodes:
            if n.key == 'exists': outcomes.append(env.get(n.value) is not None)
            elif n.key == 'OR': outcomes.append(any(holds([c], actor) for c in n.children))
            elif n.key == 'has_trait': outcomes.append(n.value in actor['traits'])
            elif n.key == 'has_title': outcomes.append(n.value in actor['titles'])
            elif n.key.startswith(('var:', 'scope:')) and n.children: outcomes.append(holds(n.children, env[n.key]))
            else: raise AssertionError(('Unsupported chance predicate', n.key))
        return all(outcomes)
    def body(nodes, initial=0):
        value = initial
        for n in nodes:
            if n.key == 'if':
                limit = next(c for c in n.children if c.key == 'limit')
                if holds(limit.children): value = body([c for c in n.children if c is not limit], value)
                continue
            operand = body(n.children) if n.children else scalar(n.value)
            if n.key == 'value': value = operand
            elif n.key == 'add': value += operand
            elif n.key == 'subtract': value -= operand
            elif n.key == 'multiply': value *= operand
            elif n.key == 'min': value = max(value, operand)
            elif n.key == 'max': value = min(value, operand)
            else: raise AssertionError(('Unsupported chance operator', n.key))
        return value
    return body(node.children)


def public_crime_checks(defs, texts, loc):
    def source(name):
        path,node=defs[name];return texts[path][node.start:node.end]
    public=source('mam_censor_public_subject_trigger')
    assert 'tier >= tier_kingdom tier <= tier_empire' in public
    assert 'this != title:h_china.holder' in public
    poll=source('mam_censor_public_poll_effect')
    assert 'mam_censor_public_trait_trigger = yes mam_censor_public_ground_trigger = yes' in poll
    assert 'max = 1' in poll and 'count >= 8' in poll and 'mam_censor_public_detention_trigger' in poll
    capture=source('mam_censor_public_capture_effect')
    for forbidden in ('name = mam_cen_native_fact','name = mam_cen_proof','name = mam_cen_admission', 'add_imprisonment_reason', 'release_from_prison'):
        assert forbidden not in capture, ('Allegation changed into guilt/custody',forbidden)
    assert 'exists = scope:mam_cen_new_intel' in capture
    assert 'var:mam_cen_native_fact = 6' in capture and 'has_variable = mam_cen_sanctioned' in capture
    assert 'mam_cen_public_seen' in source('mam_censor_public_new_trigger')
    assert 'scope:mam_cen_intel_lead.var:mam_cen_intel_kind >= 30' in source('mam_censor_intel_attach_effect')
    assert 'mam_censor_public_attach_effect = yes' in source('mam_censor_intel_attach_effect')
    for key in ('mam_cen_native_fact','mam_cen_proof','mam_cen_admission'):
        assert 'name = '+key not in source('mam_censor_public_attach_effect')
    assert 'has_variable = mam_cen_public_case' not in source('mam_censor_supported_trigger')
    assert 'has_variable = mam_cen_public_checked' not in source('mam_censor_supported_trigger')
    fitness=source('mam_censor_public_fitness_trigger')
    assert 'var:mam_cen_public_checked = 1' in fitness and 'var:mam_cen_public_ground_found = 1' in fitness
    assert 'mam_censor_public_ground_trigger = yes' in fitness
    actor=source('mam_censor_actor_trigger')
    assert 'scope:mam_cen_expected = 2 this = scope:mam_cen_subject' in actor
    assert 'is_imprisoned = no' in source('mam_censor_officer_trigger')
    assert 'is_imprisoned = no' in source('mam_censor_emperor_trigger')
    assert 'scope:mam_cen_subject = { is_imprisoned = no }' in source('mam_censor.4')
    referral=source('mam_censor_refer_crime_interaction')
    assert referral.count('has_imprisonment_reason = scope:recipient') >= 2
    assert 'scope:actor = { save_scope_as = mam_cen_public_accuser }' in referral
    removal=source('mam_censor.7')
    assert removal.index('name = mam_cen_removal_grounded value = 1') < removal.index('mam_censor_retire_effect')
    assert 'scope:mam_cen_removal_grounded = 0' in removal
    assert 'mam_cen.public_imperial_check' in removal
    assert 'mam_cen.result_public_censure' in source('mam_censor.90')
    assert 'mam_censor_supported_trigger = yes' in source('mam_censor_close_effect')
    actions=next(s for p,s in texts.items() if p.name=='mam_censor_on_actions.txt')
    assert 'on_trait_gained = { on_actions = { mam_censor_public_trait_gained } }' in actions
    assert 'on_imprison = { on_actions = { mam_censor_public_arrest } }' in actions
    assert 'on_secret_exposed' not in actions and 'on_crime_committed' not in actions


def evaluate_public_predicate(name, state):
    """Evaluate actual Censor trigger guards with supplied native fact booleans.

    This does not simulate native crime, custody or authority. Unsupported
    syntax fails rather than treating a new allegation as an established fact.
    """
    p=ROOT/'common/scripted_triggers/mam_censor_triggers.txt'
    node=next(n for n in parse(p.read_text(encoding='utf-8-sig')) if n.key==name)
    aliases={}
    def scalar(raw):
        try:return int(raw)
        except ValueError:
            if raw.startswith('scope:') and '.var:' in raw:
                alias,field=raw[6:].split('.var:',1)
                return aliases.get(alias,{}).get(field)
            return None
    def holds(nodes,env):
        values=[]
        for n in nodes:
            if n.key=='save_temporary_scope_as': aliases[n.value]=env
            elif n.key=='OR': values.append(any(holds([c],env) for c in n.children))
            elif n.key=='AND': values.append(holds(n.children,env))
            elif n.key=='NOT': values.append(not holds(n.children,env))
            elif n.key=='has_variable': values.append(n.value in env)
            elif n.key=='exists': values.append(n.value.removeprefix('var:') in env)
            elif n.key.startswith('var:') and n.children:
                values.append(holds(n.children,env.get(n.key[4:],{})))
            elif n.key.startswith('var:'):
                rhs=scalar(n.value)
                values.append(n.key[4:] in env and rhs is not None and env.get(n.key[4:])==rhs)
            elif n.key in ('mam_censor_public_subject_trigger','mam_censor_public_ground_trigger'):
                values.append(bool(env.get(n.key))==(n.value=='yes'))
            else: raise AssertionError(('Unsupported public predicate',n.key))
        return all(values)
    return holds(node.children,state)


class PublicCrimeContracts(unittest.TestCase):
    def state(self):
        return dict(mam_cen_public_case=True,mam_cen_public_checked=1,mam_cen_public_ground_found=1,
                    mam_cen_subject=dict(mam_censor_public_subject_trigger=True,mam_censor_public_ground_trigger=True))
    def test_allegation_and_review_do_not_prove_misconduct(self):
        state=self.state()
        self.assertFalse(evaluate_public_predicate('mam_censor_supported_trigger',state))
        state['mam_cen_obstruction']=1
        self.assertTrue(evaluate_public_predicate('mam_censor_supported_trigger',state))
    def test_withdrawn_native_grounds_invalidate_fitness(self):
        state=self.state();self.assertTrue(evaluate_public_predicate('mam_censor_public_fitness_trigger',state))
        state['mam_cen_subject']['mam_censor_public_ground_trigger']=False
        self.assertFalse(evaluate_public_predicate('mam_censor_public_fitness_trigger',state))
    def test_review_is_required_and_cannot_inherit_unverified_grounds(self):
        for field in ('mam_cen_public_checked','mam_cen_public_ground_found'):
            state=self.state();state[field]=0
            self.assertFalse(evaluate_public_predicate('mam_censor_public_fitness_trigger',state))
        state=self.state();state['mam_cen_subject']['mam_censor_public_subject_trigger']=False
        self.assertFalse(evaluate_public_predicate('mam_censor_public_fitness_trigger',state))


class SkillContracts(unittest.TestCase):
    def env(self, skill=10):
        def actor(): return dict(intrigue=skill, learning=skill, stewardship=skill,
                                 martial=skill, diplomacy=skill, traits=set(), titles=set())
        return {'var:mam_cen_'+key:actor() for key in ('censor','subject','reviewer','connected')}
    def test_inspector_and_subject_skills_oppose_each_other(self):
        for kind in ('payment', 'return'):
            name = 'mam_censor_'+kind+'_detection_chance'; env = self.env()
            baseline = evaluate_chance(name, env)
            for skill in ('intrigue','learning','stewardship'):
                env = self.env(); env['var:mam_cen_censor'][skill] += 5
                self.assertGreater(evaluate_chance(name, env), baseline)
                env = self.env(); env['var:mam_cen_subject'][skill] += 5
                self.assertLess(evaluate_chance(name, env), baseline)
    def test_judges_own_skill_is_used(self):
        name='mam_censor_justice_detection_chance'; env=self.env(); baseline=evaluate_chance(name,env)
        env['var:mam_cen_censor']['learning']=50
        self.assertEqual(evaluate_chance(name,env),baseline)
        env['var:mam_cen_reviewer']['learning']=20
        self.assertGreater(evaluate_chance(name,env),baseline)
    def test_witness_courtcraft_and_military_expertise_are_relevant(self):
        env=self.env(); name='mam_censor_witness_detection_chance'; baseline=evaluate_chance(name,env)
        env['var:mam_cen_connected']['diplomacy']+=8
        self.assertLess(evaluate_chance(name,env),baseline)
        env=self.env(); name='mam_censor_return_detection_chance'; baseline=evaluate_chance(name,env)
        env['var:mam_cen_censor']['martial']=30
        self.assertEqual(evaluate_chance(name,env),baseline)
        env['var:mam_cen_subject']['titles'].add('title:e_minister_of_war')
        self.assertGreater(evaluate_chance(name,env),baseline)
    def test_trait_modifiers_and_bounded_extremes(self):
        name='mam_censor_payment_detection_chance'; env=self.env(); baseline=evaluate_chance(name,env)
        env['var:mam_cen_censor']['traits'].add('diligent')
        self.assertGreater(evaluate_chance(name,env),baseline)
        env=self.env(); env['var:mam_cen_subject']['traits'].add('deceitful')
        self.assertLess(evaluate_chance(name,env),baseline)
        for kind in ('payment','return','justice','witness'):
            name='mam_censor_'+kind+'_detection_chance'
            for high,low in ((100,0),(0,100)):
                env=self.env(low)
                env['var:mam_cen_censor'].update(intrigue=high,learning=high,stewardship=high)
                env['var:mam_cen_reviewer'].update(intrigue=high,learning=high,stewardship=high)
                chance=evaluate_chance(name,env)
                self.assertGreaterEqual(chance,10);self.assertLessEqual(chance,90)

    def test_plot_tracing_uses_actual_investigator_and_suspect(self):
        actor = lambda skill: dict(intrigue=skill, learning=skill, diplomacy=skill, traits=set())
        env = {'scope:mam_cen_intel_reader':actor(10), 'scope:mam_cen_hidden_suspect':actor(10)}
        name='mam_censor_plot_trace_chance'; baseline=evaluate_chance(name,env)
        env['scope:mam_cen_intel_reader']['intrigue'] = 20
        self.assertGreater(evaluate_chance(name,env),baseline)
        env['scope:mam_cen_hidden_suspect']['intrigue'] = 30
        self.assertLess(evaluate_chance(name,env),baseline)
        for high, low in ((100,0),(0,100)):
            env = {'scope:mam_cen_intel_reader':actor(high), 'scope:mam_cen_hidden_suspect':actor(low)}
            self.assertGreaterEqual(evaluate_chance(name,env),10)
            self.assertLessEqual(evaluate_chance(name,env),90)


class Lease:
    """Executable specification for stale review and duplicate outcome invariants.

    These tests exercise the contract, not the game parser/interpreter. Source
    checks above independently require the corresponding guards in runtime.
    """
    def __init__(self):
        self.stage = 1; self.serial = 1; self.actor = 'censor-a'
        self.pending = True; self.sanctions = 0; self.returned = False
        self.abuser = None; self.paid = 0
    def choose(self, token, actor, stage, next_stage=None, close=False, sanction=False):
        if not (self.pending and self.serial == token and self.actor == actor and self.stage == stage): return False
        if sanction: self.sanctions += 1
        self.serial += 1
        if close: self.pending = False
        if next_stage: self.stage = next_stage
        return True
    def replace_reviewer(self, actor):
        if actor != self.actor: self.actor = actor; self.serial += 1


class LifecycleContracts(unittest.TestCase):
    def test_double_click_never_repeats_censure(self):
        x = Lease(); old = x.serial
        self.assertTrue(x.choose(old, x.actor, 1, close=True, sanction=True))
        self.assertFalse(x.choose(old, x.actor, 1, close=True, sanction=True))
        self.assertEqual(x.sanctions, 1); self.assertEqual(x.paid, 0)
    def test_late_previous_minister_cannot_commit(self):
        x = Lease(); token = x.serial; x.abuser = x.actor
        x.replace_reviewer('censor-b')
        self.assertFalse(x.choose(token, 'censor-a', 1, sanction=True))
        self.assertEqual(x.abuser, 'censor-a')
        self.assertTrue(x.choose(x.serial, 'censor-b', 1, next_stage=2))
    def test_petition_invalidates_open_findings_event(self):
        x = Lease(); x.stage = 6; old = x.serial
        self.assertTrue(x.choose(old, x.actor, 6, next_stage=3))
        self.assertFalse(x.choose(old, x.actor, 6, sanction=True))
        self.assertEqual(x.sanctions, 0)
    def test_role_identity_is_not_enough_after_progress(self):
        x = Lease(); old = x.serial
        x.choose(old, x.actor, 1, next_stage=2)
        self.assertFalse(x.choose(old, x.actor, 1, close=True))
    def test_valid_review_does_not_imply_treasury_movement(self):
        x = Lease()
        for stage in (2, 3, 4, 6, 7, 9, 10):
            self.assertTrue(x.choose(x.serial, x.actor, x.stage, next_stage=stage))
        x.choose(x.serial, x.actor, x.stage, close=True)
        self.assertEqual(x.paid, 0)


if __name__ == '__main__':
    report = source_checks()
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(LifecycleContracts),
                               unittest.defaultTestLoader.loadTestsFromTestCase(SkillContracts),
                               unittest.defaultTestLoader.loadTestsFromTestCase(PublicCrimeContracts)])
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful(): raise SystemExit(1)
    report['lifecycle_contract_examples_passed'] = 5
    report['skill_source_evaluator_tests_passed'] = 5
    report['discovery_source_contracts_checked'] = True
    report['public_crime_source_predicate_tests_passed'] = 3
    (ROOT/'docs/CENSOR-VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
