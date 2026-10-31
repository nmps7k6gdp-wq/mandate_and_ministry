"""Narrow, reviewed native safety transformations shared by build and verifier."""
import hashlib
from pathlib import Path


def apply_project_replacements(project, text, replacements):
    for patch in replacements:
        old, new = patch['old'], patch['new']
        count = patch.get('expected_count', 1)
        assert patch.get('reason') and text.count(old) == count, (project, 'Native patch anchor drift')
        kind = patch.get('kind', 'living_campaign_notification')
        if kind == 'living_campaign_notification':
            assert project == 'grand_campaign_project' and count == 1
            assert 'trigger_event = tgp_china_ministry.0008' in old
            assert new == '''every_contribution = {
 limit = { contribution_is_funded = yes }
 contributor ?= {
  if = { limit = { is_alive = yes }
   trigger_event = tgp_china_ministry.0008
  }
 }
}'''
        elif kind == 'wall_upgrade':
            assert project == 'great_wall' and count == 1
            assert old.startswith('on_complete = {')
            assert old.count('set_great_building = the_great_wall_04') == 1
            assert new == old.replace('set_great_building = the_great_wall_04',
                                      'mam_revenue_fund_upgrade_wall_section_effect = yes')
        elif kind == 'living_culture_reward':
            assert project == 'minister_project_culture' and count in {1, 3}
            assert old.startswith('on_complete = {')
            body = old[old.index('{')+1:-1]
            assert new == 'on_complete = {\n if = { limit = { is_alive = yes }\n' + body + '\n}\n}'
        else:
            raise AssertionError(('Unreviewed native project transformation', kind, project))
        text = text.replace(old, new, count)
    return text


def compile_native_record(record, parse):
    source = Path(record['native_source'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == record['native_file_sha256'], 'Native source file drift: ' + str(source)
    text = source.read_text(encoding='utf-8-sig')
    node = next(n for n in parse(text) if n.key == record['definition'])
    result = text[node.start:node.end]
    assert hashlib.sha256(result.encode()).hexdigest() == record['original_sha256'], 'Native definition drift'
    for patch in record['patches']:
        assert patch.get('reason') and result.count(patch['old']) == 1, 'Native safety patch drift'
        result = result.replace(patch['old'], patch['new'], 1)
    return result
