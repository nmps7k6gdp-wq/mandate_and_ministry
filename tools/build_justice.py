"""Justice authoring and narrow, pinned native bridges. Publish via full staging."""
from pathlib import Path
import hashlib
import json
import os
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]
GAME=Path(r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game')
parse=runpy.run_path(str(ROOT/'tools/verify_revenue_source.py'))['parse']
LOC={}; EVENTS=[]


def loc(key,text):
    key='mam_jus.'+key
    assert key not in LOC,key
    LOC[key]=text
    return key


def native_sources(root):
    records=json.loads((root/'docs/JUSTICE-NATIVE-BOUNDARIES.json').read_text(encoding='utf-8'))['definitions']
    result={}
    for item in records:
        s=(GAME/item['source']).read_text(encoding='utf-8-sig')
        n=next(x for x in parse(s) if x.key==item['definition'])
        body=s[n.start:n.end]
        if hashlib.sha256(body.encode('utf-8')).hexdigest()!=item['sha256']:
            raise RuntimeError('Justice native source drift; deliberately compare before migrating: '+item['definition'])
        result[item['definition']]=(s,n)
    return result


def inner(s,n):
    return s[s.index('{',n.start)+1:n.end-1]


def native_bridges(root,write):
    sources=native_sources(root)
    overrides=[]; executors=[]; values=[]; native_triggers=[]; flags=set(); internal_scopes=set()
    actions={1:'imprison_interaction',2:'pardon_interaction',3:'release_from_prison_interaction',4:'execute_prisoner_interaction'}
    metadata={}
    for action,name in actions.items():
        s,n=sources[name]; original=s[n.start:n.end]; patches=[]
        valid=next(c for c in n.children if c.key=='is_valid_showing_failures_only')
        accept=next(c for c in n.children if c.key=='on_accept')
        gate=f'mam_justice_native_gate_trigger = {{ ACTOR = scope:puppet_or_actor TARGET = scope:recipient ACTION = mam_justice_action_{action} }}'
        commit=f'mam_justice_native_commit_trigger = {{ ACTOR = scope:puppet_or_actor TARGET = scope:recipient ACTION = mam_justice_action_{action} }}'
        patches.append((s.index('{',valid.start)+1,s.index('{',valid.start)+1,'\n custom_tooltip = { text = mam_jus.native_authority_tt '+gate+' }\n'))
        patches.append((s.index('{',accept.start)+1,s.index('{',accept.start)+1,'\n if = { limit = { '+commit+' }\n mam_justice_native_begin_effect = yes\n'))
        patches.append((accept.end-1,accept.end-1,f'\n mam_justice_native_observed_effect = {{ ACTION = mam_justice_action_{action} }}\n mam_justice_native_end_effect = yes\n }}\n'))
        for start,end,text in sorted(patches,reverse=True):
            offset=start-n.start; original=original[:offset]+text+original[end-n.start:]
        overrides.append(original)
        # Exact native acceptance body, without the UI wrapper or a second cost.
        body=inner(s,accept)
        for x in accept.walk():
            if x.key in ('save_scope_as','save_temporary_scope_as'):internal_scopes.add(x.value)
            if x.key=='save_scope_value_as':internal_scopes.update(c.value for c in x.children if c.key=='name')
        compiled=re.sub(r'\broot\b','scope:mam_jus_performer',body)
        executors.append(f'mam_justice_native_execute_{action}_effect = {{\n{compiled}\n}}')
        cost=next((c for c in n.children if c.key=='cost'),None)
        resource_keys=[]
        if cost:
            for c in cost.children:
                if c.key not in ('treasury','gold','influence','prestige','piety'):raise RuntimeError(('Unknown native cost',name,c.key))
                expression=inner(s,c) if c.children else 'value = '+c.value
                expression=re.sub(r'\broot\b','scope:mam_jus_performer',expression)
                values.append(f'mam_justice_cost_{action}_{c.key} = {{\n{expression}\n}}')
                if action==1:
                    quote=expression.replace('scope:mam_jus_performer','scope:mam_jus_arrest_performer').replace('scope:puppet_or_actor','scope:mam_jus_arrest_performer').replace('scope:actor','scope:mam_jus_arrest_performer')
                    quote=quote.replace('liege_diarchy_surcharge_interaction_imprison_interaction_value','mam_justice_arrest_prestige_quote_native')
                    values.append(f'mam_justice_arrest_quote_{c.key} = {{\n{quote}\n}}')
                if action==2:
                    quote=expression.replace('pardon_interaction_influence_cost_value','mam_justice_pardon_influence_quote_native').replace('pardon_interaction_treasury_cost_value','mam_justice_pardon_treasury_quote_native')
                    values.append(f'mam_justice_pardon_quote_{c.key} = {{\n{quote}\n}}')
                resource_keys.append(c.key)
        for resource in ('treasury','gold','influence','prestige','piety'):
            if resource not in resource_keys: values.append(f'mam_justice_cost_{action}_{resource} = {{ value = 0 }}')
            if action==1 and resource not in resource_keys: values.append(f'mam_justice_arrest_quote_{resource} = {{ value = 0 }}')
        auto=next((c for c in n.children if c.key=='auto_accept'),None)
        if auto:
            expression=inner(s,auto) if auto.children else 'always = '+auto.value
            expression=re.sub(r'\broot\b','scope:mam_jus_performer',expression)
            native_triggers.append(f'mam_justice_native_auto_{action}_trigger = {{\n{expression}\n}}')
        for c in n.children:
            if c.key=='send_option':
                flag=next((x.value for x in c.children if x.key=='flag'),None)
                if flag:flags.add(flag)
                if flag=='banish':
                    predicates=[inner(s,x) for x in c.children if x.key in ('is_shown','is_valid')]
                    native_triggers.append('mam_justice_native_banish_trigger = {\n'+'\n'.join(predicates)+'\n}')
        flags.update(re.findall(r'scope:(execution_\w+)',body))
        metadata[name]={'action':action,'acceptance_sha256':hashlib.sha256(body.encode()).hexdigest(),'resources':resource_keys}
    # Default unconditional release/standard execution; special mutilation,
    # conversion, coerced vows, puppet and claim options are never selected here.
    flags|={'is_puppet_action','execution_public','execution_devour','execution_sacrifice'}
    values.extend(f'mam_justice_action_{i} = {{ value = {i} }}' for i in range(1,8))
    for native,new,performer in (
        ('liege_diarchy_surcharge_interaction_imprison_interaction_value','mam_justice_arrest_prestige_quote_native','mam_jus_arrest_performer'),
        ('pardon_interaction_influence_cost_value','mam_justice_pardon_influence_quote_native','mam_jus_pardon_performer'),
        ('pardon_interaction_treasury_cost_value','mam_justice_pardon_treasury_quote_native','mam_jus_pardon_performer')):
        s,n=sources[native]
        quote=inner(s,n).replace('scope:puppet_or_actor','scope:'+performer).replace('scope:actor','scope:'+performer)
        quote=re.sub(r'\broot\b','scope:'+performer,quote)
        values.append(new+' = {\n'+quote+'\n}')
    flag_effect='\n'.join('clear_saved_scope = '+name for name in sorted(internal_scopes-{'actor','recipient','puppet_or_actor'}))+'\n'
    flag_effect+='\n'.join('save_scope_value_as = { name = '+flag+' value = no }' for flag in sorted(flags))
    executors.append('mam_justice_native_defaults_effect = {\n'+flag_effect+'\n}')
    cost_bind=[]
    for action in range(1,6):
        native=3 if action==5 else action
        fields=' '.join(f'save_scope_value_as = {{ name = mam_jus_cost_{resource} value = mam_justice_cost_{native}_{resource} }}' for resource in ('treasury','gold','influence','prestige','piety'))
        cost_bind.append(f'{action} = {{ {fields} }}')
    executors.append('mam_justice_native_costs_effect = { switch = { trigger = var:mam_jus_action '+' '.join(cost_bind)+' } }')
    write('common/character_interactions/zz_mam_justice_native.txt','\n\n'.join(overrides))
    write('common/scripted_effects/mam_justice_native_effects.txt','\n\n'.join(executors))
    write('common/scripted_triggers/mam_justice_native_triggers.txt','\n\n'.join(native_triggers))
    write('common/script_values/mam_justice_native_values.txt','\n\n'.join(values))
    # Criminal scheme: a/c already query the newly gated native interactions.
    # b directly invokes the liege, so it needs its own senior-authority gate.
    s,n=sources['scheme_critical_moments.8071']; text=s[n.start:n.end]
    option=next(c for c in n.children if c.key=='option' and any(x.key=='name' and x.value=='scheme_critical_moments.8071.b' for x in c.children))
    trigger=next(c for c in option.children if c.key=='trigger')
    edits=[]
    for opt in [c for c in n.children if c.key=='option']:
        key=next(c.value for c in opt.children if c.key=='name')
        if key not in ('scheme_critical_moments.8071.a','scheme_critical_moments.8071.b','scheme_critical_moments.8071.c'):continue
        action=2 if key.endswith('.c') else 1
        gate=f'mam_justice_native_gate_trigger = {{ ACTOR = root TARGET = scope:criminal ACTION = mam_justice_action_{action} }}'
        commit=f'mam_justice_native_commit_trigger = {{ ACTOR = root TARGET = scope:criminal ACTION = mam_justice_action_{action} }}'
        t=next(c for c in opt.children if c.key=='trigger')
        edits.append((s.index('{',t.start)+1-n.start,'\n'+gate+'\n'))
        effects=[c for c in opt.children if c.key not in ('name','flavor','trigger','ai_chance')]
        actor='scope:criminal.liege' if key.endswith('.b') else 'root'
        edits.append((effects[0].start-n.start,'if = { limit = { '+commit+' }\n'+actor+' = { save_scope_as = puppet_or_actor } scope:criminal = { save_scope_as = recipient } mam_justice_native_begin_effect = yes\n'))
        edits.append((effects[-1].end-n.start,'\n}'))
        edits.append((effects[-1].end-n.start,f'\n{actor} = {{ save_scope_as = puppet_or_actor }} scope:criminal = {{ save_scope_as = recipient }} mam_justice_native_observed_effect = {{ ACTION = mam_justice_action_{action} }} mam_justice_native_end_effect = yes\n'))
    for position,addition in sorted(edits,reverse=True):text=text[:position]+addition+text[position:]
    write('events/mam_justice_native_scheme_events.txt','namespace = scheme_critical_moments\n'+text)
    write('docs/JUSTICE-NATIVE-COMPILER.json',json.dumps(metadata,indent=2))


def option(key,text,effects,tip,condition='',ai='base = 50',stress='',preview=False):
    name=loc(key,text);tooltip=loc(key+'_tt',tip)
    guard='mam_justice_actor_trigger = yes '+condition
    impact='stress_impact = { '+stress+' }' if stress else ''
    preview_text='show_as_tooltip = { if = { limit = { mam_justice_actor_trigger = yes } mam_justice_native_preview_effect = yes } }' if preview else ''
    return f'''option = {{ name = {name} trigger = {{ {guard} }} custom_tooltip = {tooltip} {preview_text}
     if = {{ limit = {{ {guard} }} {impact} hidden_effect = {{ {effects} }} }} ai_chance = {{ {ai} }} }}'''


def event(number,title,prose,choices,letter=False):
    t=loc(str(number)+'_title',title);d=loc(str(number)+'_desc',prose)
    style=('type = letter_event sender = scope:mam_jus_sender opening = { desc = mam_jus.opening }' if letter else
           '''type = character_event theme = intrigue
            left_portrait = { character = scope:mam_jus_subject animation = worry }
            right_portrait = { trigger = { exists = scope:mam_jus_judge scope:mam_jus_judge = { is_alive = yes this != scope:mam_jus_subject } }
             character = scope:mam_jus_judge animation = thinking }''')
    facts='' if letter else '''triggered_desc = { trigger = { scope:mam_jus_subject = { is_imprisoned = yes } } desc = mam_jus.custody_fact }
      triggered_desc = { trigger = { scope:mam_jus_case = { has_variable = mam_jus_source } } desc = mam_jus.referral_fact }
      triggered_desc = { trigger = { scope:mam_jus_case = { has_variable = mam_jus_offer_author OR = {
       var:mam_jus_offer_author = root var:mam_jus_subject = root mam_justice_known_misconduct_trigger = yes
      } } } desc = mam_jus.private_fact }
      triggered_desc = { trigger = { scope:mam_jus_case = { has_variable = mam_jus_mitigation } } desc = mam_jus.mitigation_fact }'''
    if not letter:
        facts+='''
      first_valid = {
       triggered_desc = { trigger = { scope:mam_jus_case = { mam_justice_paid_evidence_trigger = yes } } desc = mam_jus.evidence_appointment }
       triggered_desc = { trigger = { scope:mam_jus_case = { mam_justice_certification_evidence_trigger = yes } } desc = mam_jus.evidence_certification }
       triggered_desc = { trigger = { scope:mam_jus_case = { mam_justice_judicial_evidence_trigger = yes } } desc = mam_jus.evidence_judicial }
      }'''
    if number in (5,6,10):
        facts+='\n'+'\n'.join(f'triggered_desc = {{ trigger = {{ scope:mam_jus_case.var:mam_jus_action = {i} exists = scope:mam_jus_performer }} desc = mam_jus.proposal_{i} }}' for i in range(1,8))
    EVENTS.append(f'''mam_justice.{number} = {{ {style} title = {t}
     trigger = {{ mam_justice_actor_trigger = yes }} desc = {{ desc = {d}
      {facts}
     }} {' '.join(choices)}
     option = {{ name = mam_jus.stale trigger = {{ mam_justice_actor_trigger = no }} ai_chance = {{ base = 100 }} }} }}''')


def filefx(s):return 'scope:mam_jus_case = { '+s+' }'
def move(n,days=7):return f'mam_justice_move_effect = {{ STAGE = {n} DAYS = {days} }}'
def close(result):return f'mam_justice_close_effect = {{ RESULT = {result} }}'


def make_events():
    # Authored separately to keep native compiler and gameplay review readable.
    from build_justice_events import author
    author(loc,event,option,filefx,move,close,EVENTS,LOC)


def generate(root):
    root=Path(root).resolve();parent=Path(os.environ.get('MAM_BUILD_STAGING_DIR',__import__('tempfile').gettempdir())).resolve()
    if not(root.parent.name.startswith('mam-cf-build-') and root.parent.parent==parent):raise RuntimeError('Justice builds require the isolated full stage.')
    LOC.clear();EVENTS.clear()
    def write(rel,text):
        p=root/rel;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(text.strip()+'\n',encoding='utf-8-sig' if p.suffix in ('.txt','.yml') else 'utf-8')
    native_bridges(root,write)
    for template in ('runtime.txt','actions.txt','protocol.txt'):
        for block in (root/'tools/templates/justice'/template).read_text(encoding='utf-8').split('@@ ')[1:]:
            rel,body=block.split('\n',1);write(rel.strip(),body)
    for source,target in [('mam_personnel_confirmation_delegated.dds','mam_justice_authority_delegated.dds'),
                          ('mam_personnel_confirmation_empire.dds','mam_justice_authority_reserved.dds')]:
        p=root/'gfx/interface/icons/laws'/target;p.write_bytes((root/'gfx/interface/icons/laws'/source).read_bytes())
    make_events()
    LOC.update({k:re.sub(r'\[scope:(mam_jus_\w+)',r'[\1',v) for k,v in LOC.items()})
    write('events/mam_justice_events.txt','namespace = mam_justice\n\n'+'\n\n'.join(EVENTS))
    write('localization/english/mam_justice_l_english.yml','l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in LOC.items()))
    p=root/'descriptor.mod';p.write_text(re.sub(r'version="[^"]+"','version="0.4.0-alpha.20-dev.66"',p.read_text(encoding='utf-8'),count=1),encoding='utf-8')
    print(f'Justice generated: {len(EVENTS)} events; {len(LOC)} localization keys. Narrow pinned native bridges; engine acceptance pending.')


if __name__=='__main__':
    import subprocess,sys
    raise SystemExit(subprocess.call([sys.executable,str(ROOT/'tools/build_common_fund.py')]))
