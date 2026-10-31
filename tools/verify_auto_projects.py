"""Native planning continuation and logged-engine-error regressions.

Source verification only; not a CK3 runtime or a claim that a project launched.
"""
import json
import pathlib
import re
import runpy

ROOT=pathlib.Path(__file__).resolve().parents[1]
parse=runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']


def verify():
    texts={p:p.read_text(encoding='utf-8-sig') for folder in ['common','events'] for p in (ROOT/folder).rglob('*revenue_common*.txt')}
    definitions={n.key:(text[n.start:n.end],n) for text in texts.values() for n in parse(text) if n.value is None}
    all_text='\n'.join(texts.values())
    permanent=set(re.findall(r'save_scope_as\s*=\s*(mam_cf_\w+)',all_text))
    temporary=set(re.findall(r'save_temporary_scope_as\s*=\s*(mam_cf_\w+)',all_text))
    assert not permanent&temporary, ('Event target lifetime collision',permanent&temporary)
    values=set(re.findall(r'save_scope_value_as\s*=\s*\{\s*name\s*=\s*(mam_cf_\w+)',all_text))
    temp_values=set(re.findall(r'save_temporary_scope_value_as\s*=\s*\{\s*name\s*=\s*(mam_cf_\w+)',all_text))
    assert not values&temp_values, ('Scope-value lifetime collision',values&temp_values)
    manifest=json.loads((ROOT/'docs/COMMON-FUND-AI-START-MANIFEST.json').read_text())
    auto=definitions['mam_revenue_fund_auto_start_effect'][0]
    check=definitions['mam_revenue_fund_check_auto_start_effect'][0]
    assert 'is_ai = yes' in auto and 'NOT = { has_variable = mam_cf_project_instance }' in auto
    assert 'mam_cf_project_until > current_date' in auto and 'has_variable = mam_cf_payment_hold' in auto
    assert 'current_date add = 7' in auto
    assert 'mam_revenue_fund_prepare_project_budget_effect = yes' in auto
    assert 'mam_revenue_fund_transfer_effect' not in auto, 'A paid grant must not be paid again to plan'
    for entry in manifest['projects']:
        index=entry['type'];name=entry['project']
        assert f'can_plan_great_project = great_project_type:{name}' in auto
        assert f'great_project_type = {name} save_scope_as = mam_cf_auto_project' in auto
        native=pathlib.Path(entry['native_source']).read_text(encoding='utf-8-sig')
        node=next(n for n in parse(native) if n.key==name)
        location=next((n for n in node.children if n.key=='is_location_valid'),None)
        original=native[native.index('{',location.start)+1:location.end-1] if location else ''
        helper=definitions[f'mam_revenue_fund_native_start_location_{index}_trigger'][0]
        assert original in helper, ('Native location parity',name)
        if entry['province_filter']=='geographical_region':
            assert f'geographical_region = {entry["filter_target"]}' in helper
    assert auto.count('plan_great_project = {')==len(manifest['projects'])==17
    assert 'every_neighboring_county' in auto and 'holder.top_liege != title:h_china.holder' in auto
    assert 'scope:mam_cf_start_target.holder' in auto and 'every_county_province' in auto
    assert 'title:h_china.holder.capital_province' in auto
    assert 'mam_revenue_fund_project_location_trigger = yes' in auto
    assert 'primary_title.var:mam_cf_project_instance = scope:mam_cf_auto_project' in check
    assert 'scope:mam_cf_start_before subtract = scope:mam_cf_start_price' in check
    assert 'mam_cf_payment_hold' in check and 'id = mam_fund.31 days = 1' in check
    assert 'mam_revenue_fund_auto_start_effect = yes' in definitions['mam_fund.31'][0]
    assert 'mam_revenue_fund_auto_start_effect = yes' in definitions['mam_fund.36'][0]
    assert 'id = mam_fund.36 days = 1' in definitions['mam_revenue_fund_legacy_commit_effect'][0]
    assert 'scope:mam_cf_closed_budget.var:mam_cf_result' not in definitions['mam_revenue_fund_close_effect'][0]
    menu=definitions['mam_fund.5'][0]
    assert 'mam_revenue_fund_preflight_project_choices_effect = yes' in menu
    assert menu.count('scope:mam_cf_start_choice_')==17
    assert 'any_neighboring_county' in definitions['mam_fund.96'][0]
    build=re.search(r'version="([^"]+)"',(ROOT/'descriptor.mod').read_text())[1]
    (ROOT/'docs/COMMON-FUND-AI-START-VERIFICATION.json').write_text(json.dumps({
        'build':build,'native_site_predicates':len(manifest['projects']),
        'source_checks':['paid grant event continuation','weekly retry','native site/region parity',
                         'AI proposal preflight','frontier Marshal target','existing grant without new transfer',
                         'expiry/holder/hold guards','native planning and receipt proof','temporary/permanent aliases disjoint'],
        'engine_tested':False
    },indent=2)+'\n',encoding='utf-8')
    print('PASS: 17 native site predicates, explicit paid-grant AI continuation, lifecycle guards and scope-lifetime regressions.')
    print('NOT TESTED: native planning charges, site filtering in engine, project/pledge callback timing and campaign war launch.')


if __name__=='__main__':verify()
