"""Approval/execution separation and compact campaign correspondence.

Run only through the full builder, after dev.55. Never clear uncertain payment
holds or pay a native slot again merely to silence a repeated approval window.
"""
from pathlib import Path
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
parse = runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']


def edit(rel, key, fn):
    p = ROOT/rel
    text = p.read_text(encoding='utf-8-sig')
    node = next(n for n in parse(text) if n.key == key)
    p.write_text(text[:node.start]+fn(text[node.start:node.end])+text[node.end:], encoding='utf-8-sig')


queue = 'common/scripted_effects/mam_revenue_common_queue_effects.txt'
edit(queue, 'mam_revenue_fund_resolve_effect', lambda s: s.replace(
    'clear_saved_scope = mam_cf_next_actor', '''clear_saved_scope = mam_cf_next_actor
 if = { limit = { mam_revenue_fund_live_case_trigger = yes mam_revenue_fund_project_request_covered_trigger = yes }
  mam_revenue_fund_close_effect = { RESULT = 1 }
  debug_log = "MAM_PROJECT_BUDGET: covered queued invoice retired; existing authorization retained"
 }''', 1))

# Commit already rechecks live state. Bound an explanatory mobilization value
# to the current revised amount as well, so the letter never promises more.
edit(queue, 'mam_revenue_fund_bind_effect', lambda s: s.replace(
    'value = scope:mam_cf_file.var:mam_pc_mobilization_quote', '''value = {
     value = scope:mam_cf_file.var:mam_pc_mobilization_quote
     max = { value = scope:mam_cf_quote subtract = scope:mam_cf_file.var:mam_pc_minimum min = 0 }
    }''', 1))

preview = 'common/scripted_effects/mam_revenue_common_preview_effects.txt'
edit(preview, 'mam_revenue_fund_preview_effect', lambda s: s.replace(
    'custom_tooltip = mam_pc.reserve_budget_tt', '''custom_tooltip = mam_pc.reserve_budget_tt
  if = { limit = { scope:mam_cf_file = { has_variable = mam_pc_campaign_launch } }
   custom_tooltip = mam_pc.launch_authority_tt
  }''', 1))

events = 'events/mam_revenue_common_events.txt'
for event in ['mam_fund.1', 'mam_fund.8']:
    # An old queued launch label must not ask for military permission again
    # after an institutional launch mandate has already been recorded.
    edit(events, event, lambda s: s.replace(
        'scope:mam_cf_file = { has_variable = mam_pc_campaign_launch }',
        'scope:mam_cf_file = { has_variable = mam_pc_campaign_launch } scope:mam_cf_selected_project = { var:mam_pc_launch_authorized = 0 }', 1))

local = ROOT/'localization/english/mam_revenue_common_l_english.yml'
loc = {}
for line in local.read_text(encoding='utf-8-sig').splitlines()[1:]:
    match = re.fullmatch(r' ([\w.]+):0 (".*")', line)
    if match:
        loc[match[1]] = json.loads(match[2])
loc.update({
    'mam_pc.campaign_request_desc': 'Please approve #high [mam_cf_quote|0]#! [treasury_i] for #high [mam_cf_selected_project.GetName]#!, including up to [mam_cf_mobilization|0] [treasury_i] for mobilization.\n\nThis authorizes the Grand Marshal’s pledge and may begin war. Revenue will use the common fund.',
    'mam_pc.budget_request_desc': 'Please reserve #high [mam_cf_quote|0]#! [treasury_i] for contributions to #high [mam_cf_selected_project.GetName]#!.\n\nRevenue will release common funds as eligible ministries fulfill their pledges. This changes the remaining budget; it does not repeat an earlier payment or campaign launch authorization.',
    'mam_pc.launch_authority_tt': 'Authorize the Grand Marshal’s required native pledge, which can begin the Grand Campaign war. Up to [mam_cf_mobilization|0] [treasury_i] of this budget provides one-time mobilization. Native pledge costs and existing operating commitments remain protected.',
    'mam_pc.budget_approved_desc': 'A remaining budget of #high [mam_cf_quote|0]#! [treasury_i] is reserved for #high [mam_cf_selected_project.GetName]#!.\n\nCovered contributions can now proceed. Cash remains in common custody until needed; this approval does not pay the same pledge twice.'
})
local.write_text('l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items())+'\n',encoding='utf-8-sig')
p = ROOT/'descriptor.mod'
p.write_text(re.sub(r'version="[^"]+"','version="0.4.0-alpha.20-dev.56"',p.read_text(encoding='utf-8-sig'),count=1),encoding='utf-8')
print('Applied dev.56 approval deduplication, execution diagnostics and compact campaign letters.')
