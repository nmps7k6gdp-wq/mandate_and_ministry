"""Foreign missions, safe Wall upgrades and living campaign completion state.

Staged-builder upgrade only. Native inputs and protected Personnel are read
only. No war creation, pledge replay, money creation or save editing occurs.
"""
from pathlib import Path
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT / 'tools/verify_revenue_source.py'))['parse']
contracts = runpy.run_path(str(ROOT / 'tools/revenue_safety_contracts.py'))


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8-sig')


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n', encoding='utf-8-sig' if path.suffix in {'.txt', '.yml'} else 'utf-8')


def once(text, old, new):
    assert text.count(old) == 1, ('Unexpected source anchor', old)
    return text.replace(old, new, 1)


def edit(rel, key, fn):
    text = read(rel); node = next(n for n in parse(text) if n.key == key)
    write(rel, text[:node.start] + fn(text[node.start:node.end]) + text[node.end:])


triggers = 'common/scripted_triggers/mam_revenue_common_triggers.txt'
def mission_border(s):
    top = parse(s)[0]
    border = next(n for n in top.walk() if n.key == 'trigger_if' and
                  any(c.key == 'limit' and any(x.key == 'var:mam_cf_project_type' and x.value == '1' for x in c.children) for c in n.children))
    code = s[border.start:border.end].replace('trigger_if =', 'trigger_else_if =', 1)
    code = once(code, 'var:mam_cf_project_type = 1', 'var:mam_cf_project_type = 17')
    return s[:border.end] + '\n  # Missionary work uses the same approved external border, plus native faith/site rules.\n' + code + s[border.end:]
edit(triggers, 'mam_revenue_fund_project_location_trigger', mission_border)

helper = 'common/scripted_effects/mam_revenue_common_completion_safety.txt'
write(helper, r'''
# Province scope. Follow the native Mandala/Cathedral remove-old/set-new pattern
# only for known lower Wall levels. Never remove an unrelated great building.
mam_revenue_fund_upgrade_wall_section_effect = {
 save_scope_as = mam_cf_wall_site
 if = { limit = { NOT = { has_building_or_higher = the_great_wall_04 } }
  if = { limit = { has_building = the_great_wall_01 } remove_building = the_great_wall_01 }
  if = { limit = { has_building = the_great_wall_02 } remove_building = the_great_wall_02 }
  if = { limit = { has_building = the_great_wall_03 } remove_building = the_great_wall_03 }
  if = { limit = { has_great_building = no }
   set_great_building = the_great_wall_04
   mam_revenue_fund_record_diagnostic_effect = { KEY = wall_section_upgraded }
  }
  else = {
   mam_revenue_fund_record_diagnostic_effect = { KEY = wall_unrelated_building_preserved }
   title:h_china.holder ?= { if = { limit = { is_ai = no }
    send_interface_toast = { type = event_toast_effect_bad title = mam_pc.wall_conflict_title
     left_icon = scope:mam_cf_wall_site right_icon = scope:mam_cf_wall_site
     custom_tooltip = mam_pc.wall_conflict_tt
    }
   } }
  }
 }
}
# Project scope. Native campaigns may contain multiple wars. A missing old war
# is a between-stage condition, not a reason to pay or declare another one.
mam_revenue_fund_campaign_maintenance_effect = {
 if = { limit = { great_project_type = grand_campaign_project
  great_project_owner = title:h_china.holder NOT = { has_variable = mam_pc_closed }
 }
  remove_variable = mam_pc_current_marshal
  title:e_minister_grand_marshal.holder ?= {
   if = { limit = { is_alive = yes top_liege = title:h_china.holder }
    save_scope_as = mam_cf_current_campaign_marshal
   }
  }
  if = { limit = { exists = scope:mam_cf_current_campaign_marshal }
   set_variable = { name = mam_pc_current_marshal value = scope:mam_cf_current_campaign_marshal }
  }
  save_scope_value_as = { name = mam_cf_campaign_phase value = 2 }
  if = { limit = { NOT = { has_variable = mam_pc_current_marshal } }
   save_scope_value_as = { name = mam_cf_campaign_phase value = 3 }
  }
  if = { limit = { has_variable = grand_campaign_war }
   if = { limit = { exists = var:grand_campaign_war }
    save_scope_value_as = { name = mam_cf_campaign_phase value = 1 }
   }
  }
  if = { limit = { scope:mam_cf_campaign_phase != 1
   any_contribution = { contribution_id = attack_1 contribution_is_funded = yes }
   mam_revenue_fund_campaign_objectives_met_trigger = yes
  }
   save_scope_as = mam_cf_completed_campaign
   save_scope_as = great_project
   great_project_owner = { save_scope_as = owner }
   mam_revenue_fund_record_diagnostic_effect = { KEY = campaign_objectives_completed }
   complete_great_project = scope:mam_cf_completed_campaign
  }
  else = {
   if = { limit = { NOT = { has_variable = mam_pc_campaign_phase } }
    set_variable = { name = mam_pc_campaign_phase value = 0 }
   }
   if = { limit = { var:mam_pc_campaign_phase != scope:mam_cf_campaign_phase }
    set_variable = { name = mam_pc_campaign_phase value = scope:mam_cf_campaign_phase }
    if = { limit = { scope:mam_cf_campaign_phase = 2 }
     mam_revenue_fund_record_diagnostic_effect = { KEY = campaign_between_wars }
    }
    else_if = { limit = { scope:mam_cf_campaign_phase = 3 }
     mam_revenue_fund_record_diagnostic_effect = { KEY = campaign_waiting_marshal }
    }
   }
  }
  clear_saved_scope = mam_cf_current_campaign_marshal
 }
}
''')
write('common/scripted_triggers/mam_revenue_common_completion_safety.txt', r'''
# Character/native contribution context. Do not accept payment for a new native
# campaign action when no living current Marshal can execute it.
mam_revenue_fund_campaign_command_ready_trigger = {
 exists = title:h_china.holder exists = title:e_minister_grand_marshal.holder
 title:e_minister_grand_marshal.holder ?= { is_alive = yes top_liege = title:h_china.holder }
}
# Project scope; same all-targets/all-counties objective as native .0002, with
# nonempty targets and safe holder checks. No success for an empty/vacuous list.
mam_revenue_fund_campaign_objectives_met_trigger = {
 any_in_list = { variable = grand_campaign_targets
  any_in_de_jure_hierarchy = { tier = tier_county exists = holder }
 }
 any_in_list = { variable = grand_campaign_targets count = all
  any_in_de_jure_hierarchy = {
   count = all filter = { tier = tier_county }
   exists = holder holder ?= { top_overlord = title:h_china.holder }
  }
 }
}
''')

effects = 'common/scripted_effects/mam_revenue_common_project_orders.txt'
edit(effects, 'mam_revenue_fund_project_driver_effect', lambda s: once(s,
    '   mam_revenue_fund_notify_campaign_war_effect = yes',
    '   mam_revenue_fund_notify_campaign_war_effect = yes\n   mam_revenue_fund_campaign_maintenance_effect = yes'))
# Clear the named candidate on entry too: an earlier project must not leave a
# stale commander when the title becomes vacant between scans.
edit(helper, 'mam_revenue_fund_campaign_maintenance_effect', lambda s: once(s,
    '  remove_variable = mam_pc_current_marshal',
    '  clear_saved_scope = mam_cf_current_campaign_marshal\n  remove_variable = mam_pc_current_marshal'))
bindings = 'common/scripted_effects/mam_revenue_common_invoice_bindings.txt'
def campaign_invoice_readiness(s):
    additions = []
    for branch in parse(s)[0].children:
        if branch.key not in {'if', 'else_if'}:
            continue
        code = s[branch.start:branch.end]
        if 'great_project_type = grand_campaign_project' not in code:
            continue
        eligibility = next(n for n in branch.walk() if n.key == 'limit' and
                           any(c.key.startswith('mam_revenue_fund_invoice_eligible_') for c in n.children))
        additions.append(s.index('{', eligibility.start) + 1)
    assert len(additions) == 20
    for at in sorted(additions, reverse=True):
        s = s[:at] + '\n mam_revenue_fund_campaign_command_ready_trigger = yes\n' + s[at:]
    return s
edit(bindings, 'mam_revenue_fund_bind_invoice_effect', campaign_invoice_readiness)

manifest_path = 'docs/COMMON-FUND-NATIVE-PROJECTS.json'
manifest = json.loads(read(manifest_path))
for name in ['great_wall', 'minister_project_culture', 'grand_campaign_project']:
    entry = manifest['definitions'][name]
    native = Path(entry['native_source']).read_text(encoding='utf-8-sig')
    project = next(n for n in parse(native) if n.key == name)
    slots = next(n for n in project.children if n.key == 'project_contributions')
    replacements = entry.setdefault('post_replacements', [])
    if name == 'great_wall':
        for slot in slots.children:
            callback = next((n for n in slot.children if n.key == 'on_complete'), None)
            if callback is None:
                continue
            old = native[callback.start:callback.end]
            if 'set_great_building = the_great_wall_04' in old:
                replacements.append({'kind': 'wall_upgrade', 'old': old,
                    'new': old.replace('set_great_building = the_great_wall_04', 'mam_revenue_fund_upgrade_wall_section_effect = yes'),
                    'reason': 'Safely replace known lower Wall levels before installing level 4; preserve unrelated great buildings and native rewards.'})
    elif name == 'minister_project_culture':
        grouped = {}
        for slot in slots.children:
            callback = next(n for n in slot.children if n.key == 'on_complete')
            old = native[callback.start:callback.end]
            grouped[old] = grouped.get(old, 0) + 1
        for old, count in grouped.items():
            body = old[old.index('{')+1:-1]
            replacements.append({'kind': 'living_culture_reward', 'old': old,
                'new': 'on_complete = {\n if = { limit = { is_alive = yes }\n' + body + '\n}\n}',
                'expected_count': count,
                'reason': 'Personal completion rewards/toasts apply only to living actual contributors; provincial project effects are unchanged.'})
    else:
        for slot in slots.children:
            valid = next(n for n in slot.children if n.key == 'contributor_is_valid')
            entry['insertions'].append({'at': native.index('{', valid.start)+1-project.start,
                'text': '\n# MAM: no paid native campaign action without a living current commander.\nmam_revenue_fund_campaign_command_ready_trigger = yes\n'})
    assembled = native[project.start:project.end]
    for addition in sorted(entry['insertions'], key=lambda e: (e['at'], e['text']), reverse=True):
        at = addition['at']; assembled = assembled[:at] + addition['text'] + assembled[at:]
    assembled = contracts['apply_project_replacements'](name, assembled, replacements)
    outputs = []
    for path in (ROOT / 'common/great_projects/types').glob('zz_mam_revenue_common*.txt'):
        if any(n.key == name for n in parse(path.read_text(encoding='utf-8-sig'))):
            outputs.append(path)
    assert len(outputs) == 1
    edit(str(outputs[0].relative_to(ROOT)), name, lambda s, assembled=assembled: assembled)
write(manifest_path, json.dumps(manifest, indent=2))

# Pinned native event/CB overrides. No original game file is edited. The full
# original definition survives except the explicitly recorded living/holder
# guards, so conquest, legitimacy and native multi-war behavior stay intact.
registry = json.loads(read('tools/templates/revenue_native_campaign_safety.json'))
outputs = {}
for record in registry['records']:
    outputs.setdefault(record['output'], []).append(contracts['compile_native_record'](record, parse))
for output, definitions in outputs.items():
    prefix = 'namespace = tgp_china_ministry\n\n' if output.startswith('events/') else ''
    write(output, prefix + '\n\n'.join(definitions))
write('docs/COMMON-FUND-CAMPAIGN-SAFETY-MANIFEST.json', json.dumps(registry, indent=2))

local = 'localization/english/mam_revenue_common_l_english.yml'
write(local, read(local) + '\n' + '\n'.join(' '+k+':0 '+json.dumps(v, ensure_ascii=False) for k,v in {
    'mam_pc.wall_conflict_title': 'A Wall Section Could Not Be Upgraded',
    'mam_pc.wall_conflict_tt': 'Another great building occupies [mam_cf_wall_site.GetName]. It has been preserved. The Wall project did not replace it.'
}.items()))
write('descriptor.mod', re.sub(r'version="[^"]+"', 'version="0.4.0-alpha.20-dev.61"', read('descriptor.mod'), count=1))
print('Applied dev.61 mission borders, safe Wall upgrades, living campaign rewards/targets and native multi-war maintenance.')
