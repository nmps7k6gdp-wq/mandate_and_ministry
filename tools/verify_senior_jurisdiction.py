"""Limited interpreter for MAM jurisdiction source. Not a CK3 engine emulator.
Runs the actual snapshot, claim, parent and restoration helpers against small
character/title graphs. Native appointment eligibility and callbacks need CK3.
"""
from pathlib import Path
from dataclasses import dataclass, field
import re
import itertools

ROOT = Path(__file__).resolve().parents[1]
TIERS = {"tier_barony": 1, "tier_county": 2, "tier_duchy": 3,
         "tier_kingdom": 4, "tier_empire": 5, "tier_hegemony": 6}


def parse(text):
    text = re.sub(r'"(?:\\.|[^"\\])*"|#[^\n]*',
                  lambda m: m[0] if m[0].startswith('"') else '', text)
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|>=|<=|!=|\?=|[={}<>]|[^\s={}<>!]+', text)
    i = 0
    def body():
        nonlocal i
        out = []
        while i < len(tokens):
            if tokens[i] == '}':
                i += 1
                return out
            k, op = tokens[i:i + 2]
            i += 2
            if tokens[i] == '{':
                i += 1
                v = body()
            else:
                v = tokens[i]
                i += 1
            out.append((k, op, v))
        return out
    return body()


@dataclass(eq=False)
class E:
    name: str
    kind: str
    attrs: dict = field(default_factory=dict)
    vars: dict = field(default_factory=dict)
    ops: list = field(default_factory=list)
    def __repr__(self):
        return self.name


def subst(node, args):
    if isinstance(node, list):
        return [(subst(k, args), o, subst(v, args)) for k, o, v in node]
    for k, v in args.items():
        node = node.replace('$' + k + '$', v)
    return node


class VM:
    def __init__(self):
        self.defs = {}
        for rel in ['common/scripted_triggers/mam_personnel_triggers.txt',
                    'common/scripted_triggers/mam_senior_appointment_triggers.txt',
                    'common/scripted_triggers/mam_senior_jurisdiction_triggers.txt',
                    'common/scripted_effects/mam_senior_jurisdiction_effects.txt',
                    'common/scripted_effects/mam_senior_parent_effects.txt',
                    'common/scripted_effects/mam_senior_choice_basis_effects.txt',
                    'common/scripted_effects/mam_senior_choice_consequence_effects.txt',
                    'common/scripted_effects/mam_senior_sponsorship_effects.txt',
                    'common/scripted_effects/mam_senior_confirmation_effects.txt',
                    'common/scripted_effects/mam_senior_imperial_preview_effects.txt']:
            self.defs.update({k: v for k, o, v in parse((ROOT / rel).read_text(encoding='utf-8-sig'))})
        self.entities = []
        self.scopes = {}
        self.local = {}
        self.stack = []
        self.empty_switches = []

    @property
    def cur(self):
        return self.stack[-1]

    def new(self, name, kind, **attrs):
        e = E(name, kind, attrs)
        self.entities.append(e)
        self.scopes[name] = e
        return e

    def char(self, name, liege=None):
        return self.new(name, 'char', liege=liege, alive=True, celestial=True, minister=False)

    def title(self, name, tier, parent, holder):
        title = self.new(name, 'title', tier=tier, de_jure_liege=parent, holder=holder)
        if tier == 1 and parent and parent.attrs['tier'] == 2:
            capital = 'capital_barony' not in parent.attrs
            province = self.new(name + '_province', 'province', is_county_capital=capital)
            title.attrs['title_province'] = province
            if capital:
                parent.attrs['capital_barony'] = title
        return title

    def primary(self, char):
        ts = [e for e in self.entities if e.kind == 'title' and e.attrs['holder'] is char]
        return max(ts, key=lambda e: e.attrs['tier'], default=None)

    def top(self, char):
        seen = set()
        while char and char.attrs.get('liege'):
            assert char not in seen, ('cycle', char)
            seen.add(char)
            char = char.attrs['liege']
        return char

    def below(self, char, lord):
        return char is not lord and any(x is lord for x in self.ancestors(char, 'liege'))

    def ancestors(self, e, attr):
        seen = set()
        while e and self.attr(e, attr):
            e = self.attr(e, attr)
            assert e not in seen, ('cycle', e)
            seen.add(e)
            yield e

    def attr(self, e, key):
        if not e:
            return None
        if key.startswith('var:'):
            return e.vars.get(key[4:])
        if key == 'primary_title':
            return self.primary(e)
        if key == 'top_liege':
            return self.top(e)
        if key == 'is_alive':
            return e.attrs.get('alive', True)
        if key == 'is_independent_ruler':
            return e.kind == 'char' and e.attrs.get('liege') is None
        if key == 'is_governor':
            p = self.primary(e)
            return bool(e.kind == 'char' and e.attrs.get('liege') and p and p.attrs['tier'] >= 2)
        if key in ['is_landless_type_title', 'is_noble_family_title', 'is_leased_out',
                   'is_head_of_faith', 'is_at_war', 'is_imprisoned']:
            return e.attrs.get(key, False)
        if key == 'is_adult':
            return True
        return e.attrs.get(key)

    def resolve(self, s):
        if not isinstance(s, str):
            return s
        if s in TIERS:
            return TIERS[s]
        if s in ['yes', 'no']:
            return s == 'yes'
        try:
            return float(s)
        except ValueError:
            pass
        path = s.split('.')
        head = path.pop(0)
        if head.startswith('scope:'):
            e = self.scopes.get(head[6:])
        elif head == 'this':
            e = self.cur
        elif head == 'prev':
            e = self.stack[-2] if len(self.stack) > 1 else None
        elif head == 'root':
            e = self.stack[0]
        elif head in ['holder', 'liege', 'primary_title', 'top_liege', 'de_jure_liege', 'title_province', 'tier'] or head.startswith('var:'):
            e = self.attr(self.cur, head)
        else:
            return s.strip('"')
        for part in path:
            e = self.attr(e, part) if isinstance(e, E) else None
        return e

    def in_context(self, e, fn):
        if not isinstance(e, E):
            self.empty_switches.append(e)
            return False
        self.stack.append(e)
        try:
            return fn()
        finally:
            self.stack.pop()

    def fields(self, body):
        return {k: v for k, o, v in body}

    def limit(self, body):
        return next((v for k, o, v in body if k == 'limit'), [])

    def content(self, body):
        return [(k, o, v) for k, o, v in body if k not in ['limit', 'list', 'variable']]

    def collection(self, k, v):
        if k.endswith('in_list'):
            d = self.fields(v)
            return list(self.cur.vars.get(d['variable'], [])) if 'variable' in d else list(self.local.get(d['list'], []))
        if k.endswith('held_title'):
            return [e for e in self.entities if e.kind == 'title' and e.attrs['holder'] is self.cur]
        if k == 'every_vassal_or_below':
            return [e for e in self.entities if e.kind == 'char' and self.below(e, self.cur)]
        if k == 'every_owned_story':
            return [e for e in self.entities if e.kind == 'story' and e.attrs.get('owner') is self.cur]
        if k == 'every_in_de_jure_hierarchy':
            return [e for e in self.entities if e.kind == 'title' and self.cur in list(self.ancestors(e, 'de_jure_liege'))]
        raise ValueError(k)

    def args(self, v):
        return {k: a for k, o, a in v} if isinstance(v, list) else {}

    def condition(self, seq):
        result = True
        branch = False
        for k, o, v in seq:
            if k == 'trigger_if':
                branch = self.condition(self.limit(v))
                answer = self.condition(self.content(v)) if branch else True
            elif k == 'trigger_else':
                answer = self.condition(v) if not branch else True
            else:
                answer = self.test(k, o, v)
            result = result and answer
        return result

    def test(self, k, o, v):
        if k in ['save_temporary_scope_as', 'save_scope_as']:
            self.scopes[v] = self.cur
            return True
        if k in ['OR', 'AND', 'NOT']:
            if k == 'OR':
                return any(self.test(*x) for x in v)
            if k == 'AND':
                return self.condition(v)
            return not self.condition(v)
        if k == 'exists':
            return self.resolve(v) is not None
        if k == 'has_variable':
            return v in self.cur.vars
        if k == 'is_in_list':
            return self.cur in self.local.get(v, [])
        if k == 'any_in_list' or k == 'any_held_title':
            return any(self.in_context(e, lambda: self.condition(self.content(v))) for e in self.collection(k, v))
        if k == 'has_tgp_dlc_trigger':
            return self.resolve(v)
        if k == 'government_has_flag':
            return self.cur.attrs.get('celestial', False)
        if k in ['vassal_contract_has_flag', 'has_title_law_flag', 'has_realm_law_flag']:
            return self.cur.attrs.get('civilian', True)
        if k == 'tgp_is_any_minister':
            return self.cur.attrs.get('minister', False) == self.resolve(v)
        if k == 'target_is_de_jure_liege_or_above':
            return self.resolve(v) in [self.cur] + list(self.ancestors(self.cur, 'de_jure_liege'))
        if k == 'is_vassal_or_below_of':
            return self.below(self.cur, self.resolve(v))
        if k == 'story_type':
            return self.cur.attrs.get('story_type') == v
        if k == 'always':
            return self.resolve(v)
        if k in self.defs:
            answer = self.condition(subst(self.defs[k], self.args(v)))
            return answer if isinstance(v, list) else answer == self.resolve(v)
        if isinstance(v, list):
            return self.in_context(self.resolve(k), lambda: self.condition(v))
        a = self.attr(self.cur, k) if k.startswith('is_') else self.resolve(k)
        b = self.resolve(v)
        if o == '=':
            return a == b
        if o == '!=':
            return a != b
        if a is None or b is None:
            raise ValueError(('unset comparison', k, o, v))
        return {'>': lambda: a > b, '<': lambda: a < b,
                '>=': lambda: a >= b, '<=': lambda: a <= b}[o]()

    def effects(self, seq):
        chosen = False
        for k, o, v in seq:
            if k in ['if', 'else_if']:
                if k == 'if':
                    chosen = False
                if not chosen and self.condition(self.limit(v)):
                    self.effects(self.content(v))
                    chosen = True
            elif k == 'else':
                if not chosen:
                    self.effects(v)
                chosen = True
            elif k in ['save_scope_as', 'save_temporary_scope_as']:
                self.scopes[v] = self.cur
            elif k == 'save_scope_value_as':
                d = self.fields(v)
                self.scopes[d['name']] = self.resolve(d['value'])
            elif k == 'set_variable':
                d = self.fields(v)
                self.cur.vars[d['name']] = self.resolve(d['value'])
            elif k == 'remove_variable':
                self.cur.vars.pop(v, None)
            elif k == 'add_to_variable_list':
                d = self.fields(v)
                self.cur.vars.setdefault(d['name'], []).append(self.resolve(d['target']))
            elif k == 'add_to_list':
                self.local.setdefault(v, []).append(self.cur)
            elif k == 'remove_from_list':
                self.local.get(v, []).remove(self.cur)
            elif k.startswith('every_'):
                for e in self.collection(k, v):
                    self.in_context(e, lambda: self.effects(self.content(v)) if self.condition(self.limit(v)) else None)
            elif k == 'create_title_and_vassal_change':
                d = self.fields(v)
                self.scopes[d['save_scope_as']] = self.new('tx' + str(len(self.entities)), 'txn')
            elif k in ['change_title_holder', 'change_title_holder_include_vassals']:
                d = self.fields(v)
                province = self.cur.attrs.get('title_province')
                assert not (province and province.attrs.get('is_county_capital')), 'CK3 forbids direct capital-barony transfer'
                self.resolve(d['change']).ops.append(('title', self.cur, self.resolve(d['holder']), k.endswith('include_vassals')))
            elif k == 'change_liege':
                d = self.fields(v)
                self.resolve(d['change']).ops.append(('liege', self.cur, self.resolve(d['liege']), False))
            elif k == 'resolve_title_and_vassal_change':
                self.commit(self.resolve(v))
            elif k in ['debug_log', 'custom_tooltip']:
                pass
            elif k in self.defs:
                self.effects(subst(self.defs[k], self.args(v)))
            elif k == 'hidden_effect':
                self.effects(v)
            elif o == '?=' and not isinstance(self.resolve(k), E):
                pass
            elif isinstance(v, list):
                self.in_context(self.resolve(k), lambda: self.effects(v))
            else:
                raise ValueError((k, o, v))

    def commit(self, tx):
        lift = []
        for op, obj, new, include in tx.ops:
            if op == 'title' and include:
                old = obj.attrs['holder']
                lift += [(e, new) for e in self.entities if e.kind == 'char' and e.attrs.get('liege') is old]
        for op, obj, new, include in tx.ops:
            if op == 'title':
                obj.attrs['holder'] = new
                # County capitals are inseparable from county ownership in CK3.
                capital = obj.attrs.get('capital_barony')
                if capital:
                    capital.attrs['holder'] = new
        for e, new in lift:
            e.attrs['liege'] = new
        for op, obj, new, include in tx.ops:
            if op == 'liege':
                assert obj is not new
                assert self.primary(new).attrs['tier'] > self.primary(obj).attrs['tier'], ('rank', obj, new)
                obj.attrs['liege'] = new
        tx.ops.clear()

    def call(self, e, name, **args):
        self.in_context(e, lambda: self.effects(subst(self.defs[name], args)))

    def check(self, e, name):
        return self.in_context(e, lambda: self.condition(self.defs[name]))


def fixture():
    v = VM()
    emp = v.char('emperor')
    h = v.title('realm', 6, None, emp)
    eg = v.char('old_empire', emp)
    et = v.title('empire_office', 5, h, eg)
    kg = v.char('old_king', eg)
    kt = v.title('kingdom_office', 4, et, kg)
    d1 = v.title('duchy_own', 3, kt, kg)
    c1 = v.title('county_own', 2, d1, kg)
    b1 = v.title('barony_own', 1, c1, kg)
    duke = v.char('duke', kg)
    d2 = v.title('duchy_vassal', 3, kt, duke)
    c2 = v.title('county_duke', 2, d2, duke)
    b2 = v.title('barony_duke', 1, c2, duke)
    count = v.char('count', duke)
    c3 = v.title('county_vassal', 2, d2, count)
    b3 = v.title('barony_count', 1, c3, count)
    # Deliberate imperial land inside the same de-jure kingdom: never captured.
    extra = v.title('unrelated_imperial_county', 2, d1, emp)
    # Private family estate must remain with its owner.
    family = v.title('family_estate', 1, None, kg)
    family.attrs['is_noble_family_title'] = True
    newk = v.char('new_king', emp)
    newe = v.char('new_empire', emp)
    return v


def capture(v, office, name):
    t = v.scopes[office]
    old = t.attrs['holder']
    emp = v.scopes['emperor']
    f = v.new(name, 'story', owner=emp, story_type='mam_senior_appointment_story')
    f.vars.update(mam_senior_title=t, mam_senior_realm=v.scopes['realm'], mam_senior_pending=1)
    v.call(old, 'mam_senior_snapshot_vassals_effect', FILE='scope:' + name, TITLE='scope:' + office)
    tx = v.new('custody_tx' + name, 'txn')
    v.scopes['mam_appointment_change'] = tx
    v.call(old, 'mam_senior_queue_custody_effect', FILE='scope:' + name, TITLE='scope:' + office,
           OLD='scope:' + old.name, NEW='scope:emperor')
    v.commit(tx)
    assert v.check(f, 'mam_senior_pending_trigger')
    return f


def complete(v, f, char):
    emp = v.scopes['emperor']
    v.scopes['mam_jurisdiction_file'] = f
    # Personal-part queues use the actual source; root grant/liege postconditions
    # and automatic capital ownership are modeled, not executed by the CK3 engine.
    tx = v.new('destination_tx' + f.name, 'txn')
    v.scopes['mam_appointment_change'] = tx
    v.call(f, 'mam_senior_queue_personal_parts_effect', OLD='scope:emperor', NEW='scope:' + char.name)
    tx.ops.append(('title', f.vars['mam_senior_title'], char, False))
    tx.ops.append(('liege', char, emp, False))
    v.commit(tx)
    f.vars.update(mam_senior_appointee=char, mam_senior_pending=0)
    for fn in ['mam_senior_restore_parent_effect', 'mam_senior_restore_vassals_effect',
               'mam_senior_release_custody_lock_effect', 'mam_senior_wake_child_parent_repairs_effect']:
        v.call(f, fn)
    assert not v.empty_switches, v.empty_switches


def main():
    count = 0
    # Nested versus direct kingdom qualification and ordinary handover.
    for direct in [False, True]:
        v = fixture()
        if direct:
            v.scopes['old_king'].attrs['liege'] = v.scopes['emperor']
        assert v.check(v.scopes['old_king'], 'mam_senior_supported_hierarchy_trigger')
        f = capture(v, 'kingdom_office', 'kf')
        assert v.scopes['barony_own'] in f.vars['mam_senior_parts']
        assert v.scopes['unrelated_imperial_county'] not in f.vars['mam_senior_jurisdiction_titles']
        complete(v, f, v.scopes['new_king'])
        assert v.scopes['new_king'].attrs['liege'] is v.scopes['old_empire']
        assert v.scopes['duke'].attrs['liege'] is v.scopes['new_king']
        assert v.scopes['count'].attrs['liege'] is v.scopes['duke']
        for t in ['duchy_own', 'county_own', 'barony_own']:
            assert v.scopes[t].attrs['holder'] is v.scopes['new_king'], t
        assert v.scopes['unrelated_imperial_county'].attrs['holder'] is v.scopes['emperor']
        assert v.scopes['family_estate'].attrs['holder'] is v.scopes['old_king']
        count += 1
    # Lower governor dies while the kingdom is in custody.
    v = fixture(); f = capture(v, 'kingdom_office', 'kf')
    v.scopes['duke'].attrs['alive'] = False
    for t in ['duchy_vassal', 'county_duke', 'barony_duke']:
        v.scopes[t].attrs['holder'] = v.scopes['emperor']
    v.scopes['count'].attrs['liege'] = v.scopes['emperor']
    complete(v, f, v.scopes['new_king'])
    for t in ['duchy_vassal', 'county_duke', 'barony_duke']:
        assert v.scopes[t].attrs['holder'] is v.scopes['new_king'], t
    assert v.scopes['count'].attrs['liege'] is v.scopes['new_king']
    count += 1
    # Original vassal keeps pre-existing mixed lower holdings, without losing allegiance.
    v = fixture()
    other = v.title('other_kingdom', 4, None, v.scopes['emperor'])
    outside = v.title('outside_county', 2, other, v.scopes['duke'])
    f = capture(v, 'kingdom_office', 'kf'); complete(v, f, v.scopes['new_king'])
    assert v.scopes['duke'].attrs['liege'] is v.scopes['new_king']
    assert outside.attrs['holder'] is v.scopes['duke']
    count += 1
    # Every ordering of simultaneous king/empire captures and completions.
    for capture_order in itertools.permutations(['K', 'E']):
        for finish_order in itertools.permutations(['K', 'E']):
            v = fixture(); fs = {}
            for kind in capture_order:
                fs[kind] = capture(v, 'kingdom_office' if kind == 'K' else 'empire_office', kind + 'f')
            for kind in finish_order:
                complete(v, fs[kind], v.scopes['new_king' if kind == 'K' else 'new_empire'])
            assert v.scopes['kingdom_office'].attrs['holder'] is v.scopes['new_king']
            assert v.scopes['new_king'].attrs['liege'] is v.scopes['new_empire'], (capture_order, finish_order)
            for title in ['duchy_own', 'county_own', 'barony_own']:
                assert v.scopes[title].attrs['holder'] is v.scopes['new_king'], (capture_order, finish_order, title)
            assert v.scopes['duke'].attrs['liege'] is v.scopes['new_king']
            count += 1
    # An already completed kingdom remains intact through a later empire vacancy.
    v = fixture(); kf = capture(v, 'kingdom_office', 'kf'); complete(v, kf, v.scopes['new_king'])
    ef = capture(v, 'empire_office', 'ef'); complete(v, ef, v.scopes['new_empire'])
    assert v.scopes['new_king'].attrs['liege'] is v.scopes['new_empire']
    assert v.scopes['county_own'].attrs['holder'] is v.scopes['new_king']
    count += 1
    # Foreign or central-ministry empire holder is not a valid provincial superior.
    for invalid in ['foreign', 'minister']:
        v = fixture(); f = capture(v, 'kingdom_office', 'kf')
        if invalid == 'foreign':
            foreign = v.char('foreign_emperor'); v.title('foreign_realm', 6, None, foreign)
            v.scopes['old_empire'].attrs['liege'] = foreign
        else:
            v.scopes['old_empire'].attrs['minister'] = True
        complete(v, f, v.scopes['new_king'])
        assert v.scopes['new_king'].attrs['liege'] is v.scopes['emperor']
        count += 1
    # A lifted baron returns to the count even while the duke's move is queued.
    v = fixture()
    baron = v.char('baron', v.scopes['count'])
    bt = v.title('barony_vassal', 1, v.scopes['county_vassal'], baron)
    f = capture(v, 'kingdom_office', 'kf')
    baron.attrs['liege'] = v.scopes['emperor']
    complete(v, f, v.scopes['new_king'])
    assert baron.attrs['liege'] is v.scopes['count']
    assert v.scopes['count'].attrs['liege'] is v.scopes['duke']
    count += 1
    # A count lifted during empire custody returns under its existing duke/king.
    v = fixture(); f = capture(v, 'empire_office', 'ef')
    v.scopes['count'].attrs['liege'] = v.scopes['emperor']
    complete(v, f, v.scopes['new_empire'])
    assert v.scopes['count'].attrs['liege'] is v.scopes['duke']
    assert v.scopes['duke'].attrs['liege'] is v.scopes['old_king']
    assert v.scopes['old_king'].attrs['liege'] is v.scopes['new_empire']
    count += 1
    # A changed de-jure empire holder is resolved at commit, not capture.
    v = fixture(); f = capture(v, 'kingdom_office', 'kf')
    v.scopes['empire_office'].attrs['holder'] = v.scopes['new_empire']
    complete(v, f, v.scopes['new_king'])
    assert v.scopes['new_king'].attrs['liege'] is v.scopes['new_empire']
    count += 1
    # An unrelated heir's outside jurisdiction is never dragged under this king.
    v = fixture(); f = capture(v, 'kingdom_office', 'kf')
    heir = v.char('outside_heir', v.scopes['emperor'])
    other = v.title('other_kingdom', 4, None, v.scopes['emperor'])
    v.title('outside_county', 2, other, heir)
    for title in ['duchy_vassal', 'county_duke', 'barony_duke']:
        v.scopes[title].attrs['holder'] = heir
    v.scopes['duke'].attrs['alive'] = False
    complete(v, f, v.scopes['new_king'])
    assert heir.attrs['liege'] is v.scopes['emperor']
    count += 1
    # Older snapshots repair only their recorded holdings and vassal titles.
    v = fixture(); emp = v.scopes['emperor']; newk = v.scopes['new_king']
    v.scopes['kingdom_office'].attrs['holder'] = newk
    v.scopes['duke'].attrs['liege'] = emp
    for title in ['duchy_own', 'county_own']:
        v.scopes[title].attrs['holder'] = emp
    old = v.new('legacy_file', 'story', owner=emp, story_type='mam_senior_appointment_story')
    old.vars.update(mam_senior_title=v.scopes['kingdom_office'], mam_senior_realm=v.scopes['realm'],
                    mam_senior_pending=0, mam_senior_appointee=newk, mam_senior_vassal_snapshot=1,
                    mam_senior_parts=[v.scopes['duchy_own'], v.scopes['county_own']],
                    mam_senior_vassal_titles=[v.scopes['duchy_vassal']])
    v.call(emp, 'mam_senior_repair_existing_jurisdictions_effect')
    assert v.scopes['duchy_own'].attrs['holder'] is newk
    assert v.scopes['county_own'].attrs['holder'] is newk
    assert v.scopes['duke'].attrs['liege'] is newk
    assert v.scopes['unrelated_imperial_county'].attrs['holder'] is emp
    assert v.scopes['family_estate'].attrs['holder'] is v.scopes['old_king']
    assert v.scopes['realm'].vars['mam_senior_jurisdiction_migrated_dev43'] == 1
    # A migration stamp prevents future deliberate transfers being undone.
    v.scopes['county_own'].attrs['holder'] = emp
    v.call(emp, 'mam_senior_repair_existing_jurisdictions_effect')
    assert v.scopes['county_own'].attrs['holder'] is emp
    assert not v.empty_switches, v.empty_switches
    count += 1
    # Promoting the old kingdom governor into the vacant parent empire creates
    # a separate kingdom appointment, without allowing the empire to take its land.
    v = fixture(); ef = capture(v, 'empire_office', 'ef')
    kf = capture(v, 'kingdom_office', 'kf')
    complete(v, ef, v.scopes['old_king'])
    assert v.scopes['kingdom_office'].attrs['holder'] is v.scopes['emperor']
    complete(v, kf, v.scopes['new_king'])
    assert v.scopes['new_king'].attrs['liege'] is v.scopes['old_king']
    assert v.scopes['county_own'].attrs['holder'] is v.scopes['new_king']
    count += 1
    # A single empire governor's own secondary kingdom remains one exact bundle.
    v = fixture(); eg = v.scopes['old_empire']
    for title in ['kingdom_office', 'duchy_own', 'county_own', 'barony_own']:
        v.scopes[title].attrs['holder'] = eg
    v.scopes['duke'].attrs['liege'] = eg
    ef = capture(v, 'empire_office', 'ef'); complete(v, ef, v.scopes['new_empire'])
    for title in ['kingdom_office', 'duchy_own', 'county_own', 'barony_own']:
        assert v.scopes[title].attrs['holder'] is v.scopes['new_empire']
    assert v.scopes['duke'].attrs['liege'] is v.scopes['new_empire']
    count += 1
    # A county vacancy during empire custody returns into the surviving kingdom,
    # rather than becoming the incoming empire governor's personal county.
    v = fixture(); ef = capture(v, 'empire_office', 'ef')
    v.scopes['count'].attrs['alive'] = False
    for title in ['county_vassal', 'barony_count']:
        v.scopes[title].attrs['holder'] = v.scopes['emperor']
    complete(v, ef, v.scopes['new_empire'])
    assert v.scopes['county_vassal'].attrs['holder'] is v.scopes['duke']
    assert v.scopes['barony_count'].attrs['holder'] is v.scopes['duke']
    assert v.scopes['duke'].attrs['liege'] is v.scopes['old_king']
    assert v.scopes['old_king'].attrs['liege'] is v.scopes['new_empire']
    count += 1
    # Stale files cannot clear a newer custody lock or satisfy its pending guard.
    v = fixture(); old = capture(v, 'kingdom_office', 'oldfile')
    new = v.new('newfile', 'story', owner=v.scopes['emperor'])
    new.vars.update(old.vars); v.scopes['kingdom_office'].vars['mam_senior_custody_file'] = new
    assert not v.check(old, 'mam_senior_pending_trigger')
    v.call(old, 'mam_senior_release_custody_lock_effect')
    assert v.scopes['kingdom_office'].vars['mam_senior_custody_file'] is new
    count += 1
    # Six missing shortlist slots are harmless even if CK3 evaluates their previews.
    for slot in ['default', 'lateral', 'promotion', 'first_office', 'preferred', 'marked']:
        v = fixture()
        candidate = 'scope:mam_senior_' + slot
        for helper in ['mam_senior_choice_basis_tooltip_effect', 'mam_senior_choice_consequences_tooltip_effect',
                       'mam_senior_sponsorship_preview_effect', 'mam_senior_schedule_nomination_effect']:
            v.call(v.scopes['old_king'], helper, CANDIDATE=candidate, PERSONAL='no', SPONSOR='root')
        assert 'mam_selected_nominee' not in v.scopes
        assert not v.empty_switches
        count += 1
    # A default candidate alone cannot expose an empty lateral-transfer option.
    v = fixture()
    event = dict((k, b) for k, o, b in parse((ROOT / 'events/mam_senior_appointment_events.txt').read_text(encoding='utf-8-sig')))
    lateral = next(b for k, o, b in event['mam_senior.1'] if k == 'option'
                   and any(kk == 'custom_tooltip' and vv == 'mam_senior.lateral_tt' for kk, oo, vv in b))
    visibility = next(b for k, o, b in lateral if k == 'show_as_unavailable')
    v.scopes['mam_senior_default'] = v.scopes['old_king']
    v.defs['mam_senior_actor_trigger'] = [('always', '=', 'yes')]  # Valid Personnel authority premise.
    assert not v.in_context(v.scopes['old_king'], lambda: v.condition(visibility))
    v.scopes['mam_senior_lateral'] = v.scopes['old_empire']
    assert v.in_context(v.scopes['old_king'], lambda: v.condition(visibility))
    assert not v.empty_switches
    count += 1
    # Capital baronies are forbidden independently, while a secondary holding can move.
    v = fixture()
    assert not v.check(v.scopes['barony_own'], 'mam_senior_direct_title_transfer_allowed_trigger')
    other = v.title('secondary_barony', 1, v.scopes['county_own'], v.scopes['old_king'])
    assert v.check(other, 'mam_senior_direct_title_transfer_allowed_trigger')
    tx = v.new('illegal_capital_tx', 'txn'); v.scopes['illegal_tx'] = tx
    try:
        v.in_context(v.scopes['barony_own'], lambda: v.effects([('change_title_holder', '=',
            [('holder', '=', 'scope:emperor'), ('change', '=', 'scope:illegal_tx')])]))
        raise AssertionError('Illegal capital transfer was accepted')
    except AssertionError as exc:
        assert str(exc) == 'CK3 forbids direct capital-barony transfer'
    count += 1
    print(f'PASS {count} jurisdiction scenarios evaluated against the actual helper source.')
    print('Limited graph/source checks only: CK3 native transactions, succession and callback order still require in-game tests.')


if __name__ == '__main__':
    main()
