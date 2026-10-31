"""Read-only, evidence-limited balance snapshot from a CK3 save and session logs.

Uses native title treasury stocks, not character income caches or personal Gold.
Eventstats execution counters are distinct from eligibility query counts. Missing
scalar numeric identities serialize zero; references retain their native type.
This tool does not edit saves, run the game, or reconstruct expired history.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

from inspect_common_fund_save import block, entries, section


def variables(text):
    result = {}
    pattern = r'flag=(\w+)\s+(?:tick=\d+\s+)?data=\{\s+type=(\w+)(?:\s+identity=([^\s}]+))?'
    for match in re.finditer(pattern, text):
        kind, identity = match[2], match[3]
        if kind == 'value':
            result[match[1]] = float(identity or 0) / 100000
        elif identity is not None:
            result[match[1]] = {'type': kind, 'identity': identity}
    return result


def fingerprint(path):
    return {'name': path.name, 'bytes': path.stat().st_size,
            'modified_utc': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def day_number(date):
    year, month, day = map(int, date.split('.'))
    return year * 365 + sum([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][:month-1]) + day-1


def audit(save, logs):
    before = fingerprint(save)
    if zipfile.is_zipfile(save):
        with zipfile.ZipFile(save) as archive:
            text = archive.read('gamestate').decode('utf-8-sig')
    else:
        text = save.read_text(encoding='utf-8-sig')
    date = re.search(r'meta_date=([^\s]+)', text)[1]
    titles = {}
    for match in re.finditer(r'^(\d+)=\{\n\tkey=(h_china|e_minister\w*)\s', text, re.M):
        data = block(text, match.start())
        cash = re.search(r'^\ttreasury=\{\s+value=([^\s}]+)', data, re.M)
        holder = re.search(r'^\tholder=(\d+)', data, re.M)
        titles[match[2]] = {'id': int(match[1]), 'holder': int(holder[1]) if holder else None,
                             'treasury': float(cash[1]) if cash else None,
                             'variables': {k: v for k, v in variables(data).items()
                                           if k.startswith(('mam_cf_', 'mam_pc_'))}}
    projects = []
    wars = dict(entries(section(text, 'wars')))
    for ident, data in entries(section(text, 'great_projects')):
        kind = re.search(r'great_project_type=(\w+)', data)
        if not kind:
            continue
        flags = variables(data)
        if 'mam_pc_' not in data and not kind[1].startswith(('minister_project_', 'grand_campaign', 'strengthen_capital')):
            continue
        contributions = [{'slot': m[3], 'actor': int(m[1]), 'funded': int(m[1]) != 4294967295}
                         for m in re.finditer(r'contributor=(\d+)\s+great_project=(\d+)\s+project_contribution="([^"]+)"', data)]
        war_reference = flags.get('grand_campaign_war')
        linked_war = None
        if isinstance(war_reference, dict) and war_reference['type'] == 'war':
            war_id = int(war_reference['identity'])
            war = wars.get(war_id, '')
            linked_war = {'id': war_id, 'exists': bool(war)}
            for side in ['attacker', 'defender']:
                side_match = re.search(r'^\t\t\t' + side + r'=\{', war, re.M)
                side_data = block(war, side_match.start()) if side_match else ''
                linked_war[side + '_participants'] = [int(value) for value in re.findall(r'\bcharacter=(\d+)', side_data)]
            cb_match = re.search(r'casus_belli=\{', war)
            cb = block(war, cb_match.start()) if cb_match else ''
            for field in ['type', 'attacker', 'defender']:
                match = re.search(r'\b' + field + r'=([^\s{}]+)', cb)
                if match:
                    linked_war[field] = match[1]
        founder = re.search(r'\bfounder=(\d+)', data)
        started = re.search(r'\bstart_time=([^\s}]+)', data)
        remaining = re.search(r'^\t\t\t\tdays=(\d+)', data, re.M)
        projects.append({'id': ident, 'type': kind[1], 'status': re.search(r'status=(\w+)', data)[1],
                         'founder': int(founder[1]) if founder else None,
                         'start_date': started[1] if started else None,
                         'saved_construction_days': int(remaining[1]) if remaining else None,
                         'linked_war': linked_war,
                         'contributions': contributions,
                         'variables': {k: v for k, v in flags.items() if k.startswith(('mam_pc_', 'grand_campaign_'))}})
    stories = []
    for match in re.finditer(r'^\t\t(\d+)=\{\n\t\t\tstory_cycle=mam_revenue_fund_story\s', text, re.M):
        data = block(text, match.start())
        stories.append({'id': int(match[1]), 'variables': variables(data)})
    event_path = logs / 'eventstats.csv'
    event_text = event_path.read_text(encoding='utf-8-sig')
    event_rows = {}
    for row in csv.DictReader(io.StringIO(event_text), delimiter=';'):
        ident = row['#ID']
        if ident.startswith(('mam_fund.', 'mam_ministry.', 'mam_senior.', 'tgp_china_ministry.')):
            event_rows[ident] = {k: row[k] for k in ['IsValidToTriggerCount', 'ImmediateEffectCount', 'ExecuteCount', 'Sum', '%']}
    debug = (logs / 'debug.log').read_text(encoding='utf-8-sig', errors='replace')
    errors = (logs / 'error.log').read_text(encoding='utf-8-sig', errors='replace')
    debug_counts = {}
    for line in debug.splitlines():
        marker = re.search(r'\): (MAM_[^\r\n]+)', line)
        if marker:
            debug_counts[marker[1]] = debug_counts.get(marker[1], 0) + 1
    locations = {}
    for location in re.findall(r'Script location: ([^\r\n]+)', errors):
        if 'mam_' in location:
            locations[location] = locations.get(location, 0) + 1
    # A native primary frame can be called by a mod callback. Keep that context
    # instead of silently dropping native errors just because the first frame
    # has no mam_ prefix. These are associations, not automatic causation.
    contexts = {}
    for match in re.finditer(r'  Error: ([^\r\n]+)\r?\n  Script location: ([^\r\n]+)((?:\r?\n    file: [^\r\n]+)*)', errors):
        if 'mam_' in match[2] + match[3]:
            key = match[1] + ' | ' + match[2]
            contexts[key] = contexts.get(key, 0) + 1
    # eventstats is sometimes flushed only when the session exits. A file from
    # the previous run is not evidence of current execution counts or timing.
    stats_older_than_logs = max((logs / name).stat().st_mtime for name in ['debug.log', 'error.log']) - event_path.stat().st_mtime
    stale_stats = stats_older_than_logs > 3600
    stats_before_save = save.stat().st_mtime - event_path.stat().st_mtime
    realm = titles['h_china']['variables']
    report = {'save': before, 'game_date': date, 'day_number': day_number(date),
              'save_modified': False, 'log_files': [fingerprint(logs / name) for name in ['debug.log', 'error.log', 'eventstats.csv']],
              'fiscal_laws': {law: text.count('mam_revenue_authority_' + law) for law in ['reserved', 'limited', 'expanded']},
              'statement_age_days': day_number(date) - realm.get('mam_cf_statement_date', day_number(date)),
              'titles': titles, 'current_projects': projects, 'retained_fiscal_stories': stories,
              'pending_fiscal_stories': sum(story['variables'].get('mam_cf_pending', 0) == 1 for story in stories),
              'payment_hold_marker_count': text.count('mam_cf_payment_hold'),
              'eventstats_usable_for_this_run': not stale_stats,
              'eventstats_snapshot_precedes_save_seconds': round(stats_before_save, 3),
              'eventstats_may_be_partial': not stale_stats and stats_before_save > 60,
              'eventstats_age_relative_to_logs_seconds': round(stats_older_than_logs, 3),
              'eventstats_warning': ('Likely previous-session data; excluded from current-run conclusions.' if stale_stats else
                                     'Timestamp check alone does not prove session identity; compare counters and logs.'),
              'eventstats': event_rows, 'debug_markers': debug_counts,
              'mod_error_locations': dict(sorted(locations.items(), key=lambda item: -item[1])),
              'errors_with_mod_call_context': dict(sorted(contexts.items(), key=lambda item: -item[1])),
              'limitations': ['End balances do not prove no earlier transient deficits.',
                             'Event queries and scheduled checks are not payments or successful projects.',
                             'Completed/expired projects, stories and receipts may be absent from the final save.',
                             'Debug logging is selective; a missing success marker is not proof no expenditure happened.',
                             'The latest transfer diagnostic is not a complete transaction history.',
                             'The run is not a matched vanilla control or a controlled law comparison.']}
    assert fingerprint(save) == before, 'Save changed while inspected'
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('save', type=Path)
    parser.add_argument('--logs', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.save, args.logs)
    assert args.report.resolve() != args.save.resolve(), 'Report must not overwrite save'
    args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'game_date': result['game_date'], 'statement_age_days': result['statement_age_days'],
                      'treasuries': {k: v['treasury'] for k, v in result['titles'].items()},
                      'pending_fiscal_stories': result['pending_fiscal_stories'], 'save_modified': result['save_modified']}))
