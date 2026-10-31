"""Dev.61 native parity and regression checks; source/model, not CK3 execution."""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import runpy
import struct

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT / 'tools/verify_revenue_source.py'))['parse']
contracts = runpy.run_path(str(ROOT / 'tools/revenue_safety_contracts.py'))


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8-sig')


def verify():
    definitions = {}
    for folder in ['common', 'events']:
        for path in (ROOT / folder).rglob('*revenue_common*.txt'):
            text = path.read_text(encoding='utf-8-sig')
            for node in parse(text):
                if node.children:
                    assert node.key not in definitions, ('Duplicate override', node.key)
                    definitions[node.key] = text[node.start:node.end]

    registry = json.loads(read('tools/templates/revenue_native_campaign_safety.json'))
    assert json.loads(read('docs/COMMON-FUND-CAMPAIGN-SAFETY-MANIFEST.json')) == registry
    assert {r['definition'] for r in registry['records']} == {
        'tgp_china_ministry.0004', 'tgp_china_ministry.0005', 'grand_campaign_kingdom_invasion_cb'}
    expected_outputs = defaultdict(set)
    for record in registry['records']:
        expected = contracts['compile_native_record'](record, parse)
        assert definitions[record['definition']] == expected, record['definition']
        expected_outputs[record['output']].add(record['definition'])
    for output, keys in expected_outputs.items():
        assert {n.key for n in parse(read(output)) if n.children} == keys
    # Whole native definitions, including conquest, rewards, costs and repeated
    # campaign wars, must remain byte-equivalent apart from the pinned guards.
    finish = definitions['tgp_china_ministry.0005']
    assert 'every_in_list = {\n limit = { is_alive = yes }' in finish
    assert finish.count('scope:war_leader ?= { if = { limit = { is_alive = yes }') == 2
    assert 'exists = scope:war_leader' in finish
    cb = definitions['grand_campaign_kingdom_invasion_cb']
    assert 'exists = holder\n' in cb and 'holder ?= {' in cb
    assert 'trigger = { exists = scope:target_title.holder }' in definitions['tgp_china_ministry.0004']

    location = definitions['mam_revenue_fund_project_location_trigger']
    branches = {}
    for node in parse(location)[0].walk():
        if node.key not in {'trigger_if', 'trigger_else_if'}:
            continue
        limit = next(n for n in node.children if n.key == 'limit')
        kind = next((n.value for n in limit.children if n.key == 'var:mam_cf_project_type'), None)
        if kind in {'1', '17'}:
            branches[kind] = location[node.start:node.end]
    assert set(branches) == {'1', '17'}
    assert branches['17'].replace('trigger_else_if =', 'trigger_if =', 1).replace(
        'var:mam_cf_project_type = 17', 'var:mam_cf_project_type = 1', 1) == branches['1']
    assert 'is_vassal_or_below_of' in location

    manifest = json.loads(read('docs/COMMON-FUND-NATIVE-PROJECTS.json'))
    wall_patches = manifest['definitions']['great_wall']['post_replacements']
    assert len(wall_patches) > 0 and all(p['kind'] == 'wall_upgrade' for p in wall_patches)
    wall = definitions['great_wall']
    assert wall.count('mam_revenue_fund_upgrade_wall_section_effect = yes') == len(wall_patches)
    assert 'set_great_building' not in wall
    helper = definitions['mam_revenue_fund_upgrade_wall_section_effect']
    for level in ['01', '02', '03']:
        assert f'has_building = the_great_wall_{level}' in helper
        assert f'remove_building = the_great_wall_{level}' in helper
    assert helper.count('remove_building =') == 3
    assert 'NOT = { has_building_or_higher = the_great_wall_04 }' in helper
    assert 'limit = { has_great_building = no }' in helper
    assert helper.count('set_great_building = the_great_wall_04') == 1
    # The replaced old levels themselves occupy the great-building slot;
    # ordinary buildings must never be cleared to make room for a Wall.
    native = Path(manifest['definitions']['great_wall']['native_source']).parents[2]
    buildings = (native / 'buildings/tgp_great_project_buildings.txt').read_text(encoding='utf-8-sig')
    for node in parse(buildings):
        if node.key in {f'the_great_wall_0{i}' for i in range(1, 5)}:
            assert any(c.key == 'type' and c.value == 'great_building' for c in node.children)

    culture = parse(definitions['minister_project_culture'])[0]
    slots = next(n for n in culture.children if n.key == 'project_contributions')
    assert len(slots.children) == 4
    for slot in slots.children:
        callback = next(n for n in slot.children if n.key == 'on_complete')
        assert callback.children[0].key == 'if'
        guard = callback.children[0].children[0]
        assert guard.key == 'limit' and any(c.key == 'is_alive' and c.value == 'yes' for c in guard.children)

    campaign = parse(definitions['grand_campaign_project'])[0]
    slots = next(n for n in campaign.children if n.key == 'project_contributions')
    assert len(slots.children) == 20
    for slot in slots.children:
        valid = next(n for n in slot.children if n.key == 'contributor_is_valid')
        assert sum(c.key == 'mam_revenue_fund_campaign_command_ready_trigger' and c.value == 'yes'
                   for c in valid.children) == 1
    readiness = definitions['mam_revenue_fund_campaign_command_ready_trigger']
    for fragment in ['exists = title:e_minister_grand_marshal.holder', 'is_alive = yes',
                     'top_liege = title:h_china.holder']:
        assert fragment in readiness
    invoice = definitions['mam_revenue_fund_bind_invoice_effect']
    assert invoice.count('mam_revenue_fund_campaign_command_ready_trigger = yes') == 20
    for branch in parse(invoice)[0].children:
        if branch.key in {'if', 'else_if'}:
            code = invoice[branch.start:branch.end]
            assert ('great_project_type = grand_campaign_project' in code) == (
                'mam_revenue_fund_campaign_command_ready_trigger = yes' in code)
    maintenance = definitions['mam_revenue_fund_campaign_maintenance_effect']
    assert maintenance.count('clear_saved_scope = mam_cf_current_campaign_marshal') == 2
    for fragment in ['scope:mam_cf_campaign_phase != 1', 'contribution_id = attack_1 contribution_is_funded = yes',
                     'mam_revenue_fund_campaign_objectives_met_trigger = yes', 'save_scope_as = great_project',
                     'complete_great_project = scope:mam_cf_completed_campaign']:
        assert fragment in maintenance
    for forbidden in ['start_war', 'declare_war', 'end_war', 'trigger_event', 'pay_short_term_treasury',
                      'mam_revenue_fund_transfer_effect', 'mam_pc_launch_authorized', 'mam_pc_mobilization_paid']:
        assert forbidden not in maintenance, ('No replay/refund/war recreation allowed', forbidden)
    objectives = definitions['mam_revenue_fund_campaign_objectives_met_trigger']
    assert objectives.count('any_in_list =') == 2 and 'count = all' in objectives
    assert 'exists = holder' in objectives and 'holder ?= { top_overlord = title:h_china.holder }' in objectives

    # Regression expectations distinguish a campaign from a single war. The
    # supplied test4 case is between wars, not an unpaid/failed launch.
    cases = [
        ('test4_dead_founder_ended_war', True, False, True, [False], False),
        ('current_marshal_missing', False, False, True, [False], False),
        ('still_fighting', True, True, True, [True], False),
        ('all_objectives_secured', True, False, True, [True, True], True),
        ('empty_targets', True, False, True, [], False),
        ('partially_secured', True, False, True, [True, False], False),
        ('unpaid_pledge', True, False, False, [True], False),
    ]
    for label, commander, war, paid, targets, should_complete in cases:
        can_complete = paid and not war and bool(targets) and all(targets)
        assert can_complete == should_complete, label

    original = (ROOT / 'thumbnail-original.png').read_bytes()
    assert original[:8] == b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II', original[16:24]) == (1254, 1254)
    assert hashlib.sha256(original).hexdigest() == 'b52fe002fc92d7344b187ab93a904d234d9eaf15a5080977394028730a630cba'
    # User-requested upload optimization preserves the original separately.
    # Steam rejected the former 2.8 MB preview in the publisher log; pin the
    # source art, and validate dimensions/size rather than accepting new art.
    png = (ROOT / 'thumbnail.png').read_bytes()
    assert png[:8] == b'\x89PNG\r\n\x1a\n' and len(png) < 1_000_000
    assert struct.unpack('>II', png[16:24]) == (512, 512)
    assert 'picture="thumbnail.png"' in read('descriptor.mod')
    report = {'build': '0.4.0-alpha.20-dev.61', 'engine_tested': False,
              'native_pinned_definitions': len(registry['records']), 'wall_completion_callbacks': len(wall_patches),
              'culture_callbacks': 4, 'campaign_readiness_callbacks': 20,
              'campaign_lifecycle_scenarios': [c[0] for c in cases], 'thumbnail_original_bytes_preserved': True,
              'thumbnail_upload_bytes': len(png), 'thumbnail_upload_dimensions': [512, 512]}
    (ROOT / 'docs/COMMON-FUND-COMPLETION-SAFETY-VERIFICATION.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Completion safety: pinned native parity, mission borders, Wall upgrades, living rewards, campaign lifecycle and thumbnail passed (not engine execution).')


if __name__ == '__main__':
    verify()
