"""Read-only extraction of native project, pledge and linked-war evidence.

Supports plaintext gamestate or its CK3 zip container. Numeric script values
use the save's 100000 fixed-point scale. This is not a general save editor.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile


def block(text,start):
    opening=text.index('{',start);depth=0;quoted=False;escaped=False
    for at in range(opening,len(text)):
        c=text[at]
        if quoted:
            if escaped:escaped=False
            elif c=='\\':escaped=True
            elif c=='"':quoted=False
        elif c=='"':quoted=True
        elif c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:return text[start:at+1]
    raise ValueError('Unclosed save block')


def section(text,name):
    m=re.search(r'^'+re.escape(name)+r'=\{',text,re.M)
    return block(text,m.start()) if m else ''


def entries(text):
    for m in re.finditer(r'^\t\t(\d+)=\{',text,re.M):
        yield int(m[1]),block(text,m.start())


def flags(text):
    result={}
    for m in re.finditer(r'flag=(\w+)\s+(?:tick=\d+\s+)?data=\{\s+type=(\w+)\s+identity=([^\s}]+)',text):
        value=float(m[3])/100000 if m[2]=='value' else m[3]
        result[m[1]]={'type':m[2],'value':value}
    return result


def inspect(path):
    original_hash=hashlib.sha256(path.read_bytes()).hexdigest()
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:text=z.read('gamestate').decode('utf-8-sig')
    else:text=path.read_text(encoding='utf-8-sig')
    projects=[]
    wars=dict(entries(section(text,'wars')))
    for key,data in entries(section(text,'great_projects')):
        kind=re.search(r'great_project_type=(\w+)',data)
        if not kind:continue
        if kind[1] not in {'grand_campaign_project','strengthen_capital'} and 'flag=mam_pc_' not in data:continue
        variables=flags(data)
        pledges={m[3]:{'contributor':int(m[1]),'funded':int(m[1])!=4294967295}
                 for m in re.finditer(r'contributor=(\d+)\s+great_project=(\d+)\s+project_contribution="([^"]+)"',data)}
        record={'id':key,'type':kind[1],
                'status':re.search(r'status=(\w+)',data)[1],
                'completed':bool(re.search(r'completed=yes',data)),
                'founder':int(re.search(r'founder=(\d+)',data)[1]),
                'contributions':pledges,
                'variables':{k:v for k,v in variables.items() if k.startswith(('mam_pc_','grand_campaign_'))}}
        warref=variables.get('grand_campaign_war',{}).get('value')
        if warref is not None:
            war=wars.get(int(warref),'')
            record['linked_war']={'id':int(warref),'exists':bool(war)}
            if war:
                cb=re.search(r'casus_belli=\{',war)
                details=block(war,cb.start()) if cb else ''
                for name in ['type','attacker','defender']:
                    m=re.search(r'\b'+name+r'=([^\s{}]+)',details)
                    if m:record['linked_war'][name]=m[1]
                m=re.search(r'\bname="([^"]+)"',war)
                if m:record['linked_war']['name']=m[1]
        if all(k in variables for k in ['mam_pc_attempt_before','mam_pc_attempt_after','mam_pc_attempt_price']):
            record['last_attempt_debit']=variables['mam_pc_attempt_before']['value']-variables['mam_pc_attempt_after']['value']
        projects.append(record)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==original_hash, 'Save changed while inspected'
    return {'source_save':path.name,'sha256':original_hash,
            'game_date':re.search(r'meta_date=([^\s]+)',text)[1],
            'save_modified':False,'projects':projects}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('save',type=Path)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    result=inspect(args.save)
    if args.report:args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='projects'}))
    for project in result['projects']:
        print(json.dumps({'id':project['id'],'type':project['type'],'status':project['status'],
                          'funded_pledges':sum(c['funded'] for c in project['contributions'].values()),
                          'linked_war':project.get('linked_war')}))
