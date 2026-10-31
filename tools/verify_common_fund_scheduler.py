"""Due-date/lease regressions and generated-source wiring, not a CK3 emulator."""
from dataclasses import dataclass
import json
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT / 'tools/verify_revenue_source.py'))['parse']


def definitions():
    result = {}
    for folder in ['common/scripted_effects', 'common/on_action', 'common/script_values']:
        for path in (ROOT / folder).glob('*revenue*.txt'):
            text = path.read_text(encoding='utf-8-sig')
            for node in parse(text):
                if node.children:
                    result[node.key] = (text[node.start:node.end], node)
    return result


@dataclass
class Clock:
    emperor: int = 1
    owner: int = 1
    weekly_due: int | None = 0
    month_due: int | None = None
    adopted: bool = True
    custodian: bool = True
    count: int = 0

    def reconcile(self, day):
        if self.adopted and self.custodian and (self.month_due is None or self.month_due <= day):
            self.month_due = day + 25
            self.count += 1

    def recover(self, day):
        # Startup/title gains/documented quarterly fallback. Reconciliation has
        # an independent due gate; multiple recovery calls are safe.
        self.reconcile(day)
        if self.weekly_due is None or self.weekly_due < day or self.owner != self.emperor:
            self.weekly_due = day + 1
            self.owner = self.emperor

    def tick(self, day, actor=None):
        if actor is None:
            actor = self.emperor
        if actor != self.emperor or self.weekly_due is None or self.weekly_due > day:
            return
        self.reconcile(day)
        self.weekly_due = day + 7
        self.owner = self.emperor


def verify():
    defs = definitions()
    payroll, node = defs['mam_revenue_fund_payroll_effect']
    assert payroll.count('mam_revenue_fund_month_effect = yes') == 1
    outer = next(n for n in node.children if n.key == 'if')
    assert any(n.key == 'mam_revenue_fund_month_effect' for n in outer.children)
    gate = next(n for n in outer.children if n.key == 'limit')
    gate_keys = {n.key for n in gate.walk()}
    assert {'mam_revenue_emperor_trigger', 'mam_revenue_fund_enabled_trigger', 'var:mam_cf_payroll_due'} <= gate_keys
    assert 'mam_cf_payroll_due <= current_date' in payroll and 'days = 7' in payroll
    assert 'name = mam_cf_payroll_owner value = scope:mam_cf_payroll_sovereign' in payroll
    month = defs['mam_revenue_fund_month_effect'][0]
    assert 'mam_cf_next_month <= current_date' in month and 'current_date add = 25' in month
    assert 'mam_revenue_fund_ready_trigger = yes' in month
    assert 'KEY = reconciled' in month and 'name = mam_cf_statement_date value = current_date' in month
    assert 'mam_revenue_fund_payroll_effect = yes' not in month, 'Immediate scheduler recursion'
    actions = (ROOT / 'common/on_action/mam_revenue_on_actions.txt').read_text(encoding='utf-8-sig')
    assert 'monthly_playable_pulse' not in actions
    assert 'quarterly_playable_pulse = { on_actions = { mam_revenue_fund_monthly } }' in actions
    assert 'on_game_start_after_lobby' in actions and 'on_title_gain' in actions
    assert 'mam_revenue_fund_start_effect = yes' in defs['mam_revenue_fund_monthly'][0]
    assert 'mam_revenue_fund_ensure_payroll_effect = yes' in defs['mam_revenue_fund_start_effect'][0]
    assert 'mam_cf_bootstrap_until <= current_date' in defs['mam_revenue_fund_start_effect'][0]
    need = defs['mam_revenue_need_score'][0]
    assert 'mam_rv_priority' not in need
    assert 'has_variable = mam_cf_programme' in need and 'var:mam_cf_programme = 2' in need
    assert 'mam_revenue_has_recovery_need_trigger = yes' in need
    diag = defs['mam_revenue_fund_record_diagnostic_effect'][0]
    assert 'NOT = { has_variable = mam_cf_diag_$KEY$ }' in diag
    assert 'title:h_china = {' in diag and 'mam_cf_diag_last_$KEY$ value = current_date' in diag
    for forbidden in ['add_gold', 'pay_short_term_treasury', 'remove_variable = mam_cf_payment_hold', 'trigger_event']:
        assert forbidden not in diag, ('Diagnostics changed gameplay', forbidden)
    law_text = (ROOT / 'common/laws/mam_revenue_laws.txt').read_text(encoding='utf-8-sig')
    laws = {n.key: law_text[n.start:n.end] for n in parse(law_text)}
    loc_text = (ROOT / 'localization/english/mam_revenue_l_english.yml').read_text(encoding='utf-8-sig')
    loc = {m[1]: json.loads(m[2]) for line in loc_text.splitlines()
           if (m := re.fullmatch(r' ([\w.]+):0 (".*")', line))}
    assert loc['mam_revenue_fiscal_authority_laws'] == 'Revenue Fiscal Authority'
    for index, (suffix, title) in enumerate([
        ('reserved', 'Imperial Fiscal Control'),
        ('limited', 'Supervised Fiscal Administration'),
        ('expanded', 'Delegated Fiscal Administration')]):
        key = 'mam_revenue_authority_' + suffix
        assert loc[key] == title and loc[key + '_effects']
        assert f'law_group_type = mam_revenue_fiscal_authority_laws index = {index}' in laws[key]
        assert 'pass_cost = { prestige = 150 }' in laws[key]

    # The native reference on this installation is an input, never an output.
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/common/on_action/_on_actions.info').read_text(encoding='utf-8-sig')
    assert 'quarterly_playable_pulse' in native and 'monthly_playable_pulse' not in native
    scenarios = []
    old = Clock(weekly_due=401059, month_due=401014)
    old.tick(401059); old.tick(401059)
    assert old.count == 1 and old.weekly_due == 401066
    scenarios.append('overdue test2 adoption, duplicate same-day worker, no arrears replay')
    clock = Clock()
    for day in range(731):
        clock.tick(day)
        if day % 90 == 0:
            clock.recover(day)
    assert clock.count == 27 and clock.month_due > 730
    scenarios.append('two years: 27 bounded settlements including day zero; quarterly recovery does not duplicate')
    fresh = Clock(adopted=False)
    for day in range(35):
        fresh.tick(day)
    assert fresh.count == 0
    fresh.adopted = True; fresh.recover(35); fresh.tick(35)
    assert fresh.count == 1
    scenarios.append('35-day first adoption, bootstrap and weekly callback on same day')
    absent = Clock(custodian=False)
    for day in range(91):
        absent.tick(day)
    assert absent.count == 0
    absent.custodian = True; absent.recover(91); absent.tick(91)
    assert absent.count == 1
    scenarios.append('custodian vacancy pauses reconciliation and later recovery settles once')
    changed = Clock(weekly_due=7, month_due=0)
    changed.emperor = 2; changed.recover(3); changed.tick(4, actor=1)
    assert changed.count == 1 and changed.weekly_due == 4
    changed.tick(4, actor=2); changed.tick(7, actor=1)
    assert changed.count == 1 and changed.weekly_due == 11
    scenarios.append('succession changes sovereign lease; old callbacks cannot advance it')
    missing = Clock(weekly_due=None)
    missing.recover(90); missing.recover(90); missing.tick(91); missing.tick(91)
    assert missing.count == 1 and missing.weekly_due == 98
    scenarios.append('documented recovery recreates one missing lease; repeated recovery remains safe')
    overdue = Clock(weekly_due=10000, month_due=1)
    overdue.tick(10000)
    assert overdue.count == 1 and overdue.month_due == 10025
    scenarios.append('very old save settles current position once without historical catch-up transfers')
    restored = Clock(count=100, month_due=100, weekly_due=101)
    restored.tick(101); restored.recover(101); restored.tick(101)
    assert restored.count == 101
    scenarios.append('reload retains existing due dates and diagnostic count')
    build = re.search(r'version="([^"]+)"', (ROOT / 'descriptor.mod').read_text())[1]
    (ROOT / 'docs/COMMON-FUND-SCHEDULER-VERIFICATION.json').write_text(json.dumps({
        'build': build, 'source_wiring_verified': True, 'scenarios': scenarios,
        'engine_tested': False, 'interval': 'existing 25-day due guard polled weekly; normally 28 days',
        'protected_contracts': ['no historical replay', 'no new payment timer', 'no approval bypass',
                                'fiscal law names retain saved IDs, level indices and effects',
                                'no cash or hold reset', 'current programme used for relief ranking']
    }, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: scheduler wiring, documented pulse, current relief priority, read-only diagnostics and {len(scenarios)} lease/cadence scenarios.')
    print('NOT TESTED: CK3 execution, actual native transfers or two-year observer outcomes.')


if __name__ == '__main__':
    verify()
