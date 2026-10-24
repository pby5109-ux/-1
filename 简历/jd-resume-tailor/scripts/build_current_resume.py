"""Check current schema-v2 snapshots; build only the legacy September 17 template.

Only word/document.xml changes; all other ZIP parts remain byte-identical.
Use --import-baseline once to establish the content source; normal builds read JSON.
--check accepts current long-campus snapshots, but does not certify build compatibility.
"""
from pathlib import Path, PureWindowsPath
from copy import deepcopy
from zipfile import ZipFile
import argparse
import hashlib
import json
import re
import sys
from lxml import etree as E
from validate_resume_content import evidence_index, load_json, DEFAULT_PROFILE, DEFAULT_PROJECTS

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent / '定制投递/通用嵌入式-20260917/彭博裕-嵌入式软件工程师-简历-20260917.docx'
BASE_HASH = 'e2160a961da34277ba97fa7511ce3621e81519716e475f9f78e609e9f741a23e'
CONTENT = ROOT / 'references/current-content.json'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def q(n): return '{'+NS['w']+'}'+n
def text(e): return ''.join(e.xpath('.//w:t/text()', namespaces=NS))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def read_base():
    if digest(BASE) != BASE_HASH:
        raise ValueError('Baseline changed: inspect and approve a new template before building')
    with ZipFile(BASE) as z:
        root = E.fromstring(z.read('word/document.xml'))
    return root, root.find('w:body', NS)

def item(p):
    label, value = text(p).removeprefix('• ').split('：', 1)
    return {'label': label, 'text': value, 'source_refs': ['baseline-20260917']}

def bootstrap():
    if CONTENT.exists(): raise ValueError('Content source already exists; edit it, never re-import over it')
    _, b = read_base()
    projects=[]
    for pid, i in zip(['instrument','lora_node','car_contest'], [8,14,20]):
        cells=b[i].xpath('./w:tr/w:tc',namespaces=NS)
        projects.append({'id':pid,'name':text(cells[0]),'keywords':text(cells[1]),
            'intro':item(b[i+1]),'duty':item(b[i+2]),'bullets':[item(b[j]) for j in range(i+3,i+6)]})
    data={'schema_version':2,'approved':True,'content_revision':'20260917-internship-v1',
        'approval_record':{'source':'本任务用户指定9月17日通用模板并要求加入此前提供的实习、校园一句话/无校园双版；随后授权同步JD与skill',
            'scope':'保留基准三项目与技能，新增实习，校园压缩；不表示本轮独立复测项目指标'},
        'sources':{'baseline-20260917':{'path':str(BASE),'sha256':BASE_HASH,'status':'user_selected_existing_content'},
            'internship-user':{'status':'user_provided','reference':'简历内容讨论与定稿记录.md / 2026-09-17实习暂定稿'},
            'campus-user':{'status':'user_confirmed_facts_condensed','reference':'科创部部长、人员协调、校级活动及真实设备故障应对'}},
        'header':{'name':'彭博裕','target':'嵌入式软件工程师','contact':'电话：17668025109   邮箱：pbyuqianrushi@163.com   2027届'},
        'education':[text(c) for c in b[2].xpath('./w:tr/w:tc',namespaces=NS)],
        'honors':[item(b[i]) for i in [4,5,6]],'projects':projects,
        'enterprise':{'name':'烟台东方威思顿电气有限公司','role':'智能电表测试实习生','period':'2025.10—2025.11','bullets':[
            {'label':'产品认知','text':'围绕智能电表及用电信息采集终端，结合PCBA布局梳理电源、采样、计量、通信与安全防护模块，理解三相四线计量基础及主要器件的连接关系。','source_refs':['internship-user']},
            {'label':'开发板实践','text':'参与电能表开发板操作及相关测试，结合培训学习工况事件、远程费控和主动上报流程，梳理输入条件、软件处理与设备响应之间的联系。','source_refs':['internship-user']},
            {'label':'通信与排查','text':'学习RS485与电力线载波的传输方式及载波耦合原理，围绕采集异常整理“供电接线—信号输入—通信参数—软件状态”的分层排查思路，为通信测试与问题定位提供参考。','source_refs':['internship-user']}]},
        'campus':{'text':'担任校学生会科创部部长，统筹成员分工与跨部门协作，组织校级宣讲及校园活动，具备组织协调、现场执行与突发问题处理能力。','source_refs':['campus-user']},
        'skills':[item(b[i]) for i in range(31,36)],
        'layout':{'heading_before_twips':100,'line_twips':230},
        'review_notes':['量化及贡献保留用户选定基准，本轮未新做源码或硬件验证。','旧证据快照与用户新定稿不一致时按事实来源与日期核对，不把批准措辞当作测试证据。','Python/内核熟练度沿基准保留，针对新JD扩大范围前须核对。']}
    CONTENT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(CONTENT)

def require(condition, message):
    if not condition:
        raise ValueError(message)

def source_file_issues(d, workspace_root=None):
    """Read-only freshness check; never update hashes to hide a changed source."""
    workspace=Path(workspace_root) if workspace_root is not None else ROOT.parent.parent
    issues=[]
    for ref, source in d.get('sources', {}).items():
        if not isinstance(source, dict) or 'path' not in source:
            continue
        raw=source['path']
        expected=source.get('sha256')
        if not isinstance(raw, str) or not raw.strip():
            issues.append(f'{ref}: invalid source path')
            continue
        if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', expected):
            issues.append(f'{ref}: missing or invalid SHA256')
            continue
        path=Path(raw)
        if raw.startswith(('\\\\', '//')) or (PureWindowsPath(raw).is_absolute() and not path.is_absolute()):
            issues.append(f'{ref}: source unavailable for local checking on this host')
            continue
        if not path.is_absolute():
            path=workspace/path
        try:
            if not path.is_file():
                issues.append(f'{ref}: source file missing or not a file')
            elif digest(path).lower() != expected.lower():
                issues.append(f'{ref}: source file changed; recorded hash is stale')
        except (OSError, ValueError):
            issues.append(f'{ref}: source file unreadable')
    return issues

def check_content(d, strict_sources=False, workspace_root=None):
    """Report structure separately from freshness; strict mode is a preflight gate."""
    validate(d)
    issues=source_file_issues(d, workspace_root)
    for issue in issues:
        print('WARNING: '+issue)
    pending=d.get('sync_status') == 'partial_pending_protected_wording_sync'
    if pending:
        print('WARNING: protected wording sync remains pending; use the selected PDF plus approved deltas, not this whole snapshot')
    if strict_sources and (issues or pending):
        print('ERROR: source freshness or wording sync unresolved; no files generated', file=sys.stderr)
        return 2
    print('OK schema-v2 structure and reference policy; NOT fact, approval, template compatibility or PDF quality verification')
    return 0

def validate(d, profile=None, projects=None):
    """Validate v2 structure and reference policy, not facts, layout or real approval."""
    require(isinstance(d, dict) and d.get('schema_version') == 2, 'schema_version must be 2')
    require(d.get('approved') is True, 'Explicit approval required')
    approval=d.get('approval_record')
    require(isinstance(approval, dict), 'approval_record is required')
    # Current records use approval_note/by/on; historical packages use source/scope.
    has_approval=bool(approval.get('source')) or (
        approval.get('approved_by') == 'user' and bool(approval.get('approved_on'))
        and bool(approval.get('approval_note')))
    require(has_approval and bool(d.get('content_revision')), 'Approval provenance and revision required')
    sources=d.get('sources')
    require(isinstance(sources, dict), 'sources must be an object')
    index=evidence_index(profile if profile is not None else load_json(DEFAULT_PROFILE),
                         projects if projects is not None else load_json(DEFAULT_PROJECTS))
    # String metadata such as content_source is not an evidence ID.
    registered={key for key, value in sources.items()
                if isinstance(value, dict) and value.get('status')}
    require(isinstance(d.get('education'), list) and len(d['education']) == 4,
            'education must contain four fields')
    project_list=d.get('projects')
    require(isinstance(project_list, list) and len(project_list) == 3,
            'This v2 snapshot must contain three selected projects')
    require(all(isinstance(p, dict) for p in project_list), 'project entries must be objects')
    require(len({p.get('id') for p in project_list}) == 3 and all(p.get('id') for p in project_list),
            'Project IDs must be nonempty and unique')
    entries=[]
    for field in ('honors', 'skills'):
        items=d.get(field)
        require(isinstance(items, list) and bool(items), field+' must be a nonempty list')
        entries.extend((field+f'[{i}]', it) for i, it in enumerate(items))
    enterprise=d.get('enterprise')
    require(isinstance(enterprise, dict) and isinstance(enterprise.get('bullets'), list),
            'enterprise.bullets must be a list')
    entries.extend((f'enterprise.bullets[{i}]', it) for i, it in enumerate(enterprise['bullets']))
    campus=d.get('campus')
    require(isinstance(campus, dict), 'campus must be an object')
    mode=campus.get('mode', 'short')
    require(mode in ('long', 'short', 'none'), 'campus.mode must be long, short or none')
    if mode == 'long':
        require(all(campus.get(k) for k in ('name', 'role', 'period')), 'Long campus heading required')
        require(isinstance(campus.get('bullets'), list) and bool(campus['bullets']),
                'Long campus bullets required')
        entries.extend((f'campus.bullets[{i}]', it) for i, it in enumerate(campus['bullets']))
    if mode != 'none':
        short=campus.get('short_text', campus.get('text'))
        if mode == 'short' or short is not None:
            entries.append(('campus.short_text', {'text':short, 'source_refs':campus.get('source_refs')}))
    for i, p in enumerate(project_list):
        require(bool(p.get('name')) and bool(p.get('keywords')), f'project {i} name/keywords required')
        require(isinstance(p.get('bullets'), list) and 1 <= len(p['bullets']) <= 4,
                f'project {i} must contain 1-4 bullets')
        entries.extend((f'project {i}.{field}', p.get(field)) for field in ('intro', 'duty'))
        entries.extend((f'project {i}.bullets[{j}]', it) for j, it in enumerate(p['bullets']))
    for location, it in entries:
        require(isinstance(it, dict) and isinstance(it.get('text'), str) and bool(it['text'].strip()),
                location+': nonempty text required')
        refs=it.get('source_refs')
        require(isinstance(refs, list) and bool(refs) and all(isinstance(r, str) for r in refs),
                location+': source_refs must be a nonempty string list')
        for ref in refs:
            require(ref in index or ref in registered, location+': unknown source_ref '+ref)
            claim=index.get(ref, sources.get(ref))
            require(claim.get('status') not in ('prohibited', 'unresolved', 'design_only')
                    and claim.get('resume_policy') != 'prohibited', location+': prohibited source_ref '+ref)
            if claim.get('resume_policy') == 'allowed_with_qualifier':
                terms=claim.get('required_qualifier_terms', [])
                require(not terms or any(term in it['text'] for term in terms),
                        location+': validation qualifier required for '+ref)
    layout=d.get('layout')
    require(isinstance(layout, dict) and isinstance(layout.get('line_twips'), (int, float))
            and layout['line_twips'] > 0, 'Positive layout.line_twips required')
    return True

def validate_legacy_build(d):
    """Keep unsupported snapshots from silently entering the fixed old renderer."""
    validate(d)
    require(d.get('sync_status') != 'partial_pending_protected_wording_sync',
            'Snapshot wording sync is pending: merge the selected PDF and approved deltas first')
    require(d.get('snapshot_kind') != 'dynamic_template_snapshot',
            'Dynamic snapshot: use the selected current template, not the September 17 renderer')
    campus=d['campus']
    require(campus.get('mode', 'short') == 'short' and isinstance(campus.get('text'), str)
            and campus['text'].count('。') == 1 and '\n' not in campus['text'],
            'Legacy renderer supports only the historical single-sentence campus structure')
    require(len(d['enterprise']['bullets']) == 3 and 3 <= len(d['skills']) <= 6,
            'Legacy renderer requires three enterprise bullets and 3-6 skills')
    require(d['layout']['line_twips'] >= 230,
            'Legacy renderer does not implement newer font/spacing; use current-template tools')

def rewrite(p, pieces):
    runs=p.findall('w:r',NS)
    props=[deepcopy(r.find('w:rPr',NS)) for r in runs if r.find('w:rPr',NS) is not None]
    assert props
    for c in list(p):
        if c.tag != q('pPr'): p.remove(c)
    for value, idx in pieces:
        r=E.SubElement(p,q('r'));r.append(deepcopy(props[min(idx,len(props)-1)]))
        t=E.SubElement(r,q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=value
    return p

def labelled(template,it,bullet=False):
    return rewrite(deepcopy(template),[(('• ' if bullet else '')+it['label']+'：',0),(it['text'],1)])

def build(d,output,campus,internship=True):
    validate_legacy_build(d)
    if output.exists(): raise ValueError('Output exists; choose a new revision directory')
    root,b=read_base();old=list(b)
    # Header and education remain reference-derived, including embedded photo.
    hp=old[0].xpath('./w:tr/w:tc[1]/w:p',namespaces=NS)
    rewrite(hp[0],[(d['header']['name'],0),('   求职意向：'+d['header']['target'],1)])
    rewrite(hp[1],[(d['header']['contact'],0)])
    for cell,value in zip(old[2].xpath('./w:tr/w:tc',namespaces=NS),d['education']):
        rewrite(cell.find('w:p',NS),[(value,0)])
    order=old[:4]+[labelled(old[4],v) for v in d['honors']]+[old[7]]
    for p in d['projects']:
        title=deepcopy(old[8]);cells=title.xpath('./w:tr/w:tc/w:p',namespaces=NS)
        rewrite(cells[0],[(p['name'],0)]);rewrite(cells[1],[(p['keywords'],0)])
        order += [title,labelled(old[9],p['intro']),labelled(old[10],p['duty'])]
        order += [labelled(old[11],it,True) for it in p['bullets']]
    if internship:
        order += [rewrite(deepcopy(old[26]),[('实习经历',0)])]
        title=deepcopy(old[27]);cells=title.xpath('./w:tr/w:tc/w:p',namespaces=NS)
        e=d['enterprise']
        rewrite(cells[0],[(e['name'],0),('｜'+e['role'],1)])
        rewrite(cells[1],[(e['period'],0)])
        order += [title]+[labelled(old[11],it,True) for it in e['bullets']]
    if campus:
        cp=rewrite(deepcopy(old[31]),[(d['campus']['text'],1)])
        order += [old[26],cp]
    order += [old[30]]+[labelled(old[31],it) for it in d['skills']]+[old[36]]
    for el in list(b): b.remove(el)
    for el in order: b.append(el)
    for p in b.findall('w:p',NS):
        pr=p.find('w:pPr',NS)
        if pr is not None and pr.find('w:pBdr',NS) is not None and text(p)!='教育背景':
            pr.find('w:spacing',NS).set(q('before'),str(d['layout']['heading_before_twips']))
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(BASE) as src, ZipFile(output,'w') as dst:
        for info in src.infolist():
            blob=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else src.read(info.filename)
            dst.writestr(info,blob)
    with ZipFile(BASE) as src, ZipFile(output) as dst:
        assert dst.testzip() is None
        assert all(src.read(n)==dst.read(n) for n in src.namelist() if n!='word/document.xml')
    assert digest(BASE)==BASE_HASH
    print('OK',output)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--import-baseline',action='store_true');p.add_argument('--content',type=Path,default=CONTENT)
    p.add_argument('--out-dir',type=Path);p.add_argument('--check',action='store_true')
    p.add_argument('--require-current-sources',action='store_true',
                   help='With --check, fail if recorded file hashes are stale/unavailable or wording sync is pending')
    p.add_argument('--internship',choices=['yes','no'],default='yes')
    p.add_argument('--campus',choices=['yes','no','both'],default='both');a=p.parse_args()
    if a.require_current_sources and (not a.check or a.import_baseline):
        p.error('--require-current-sources requires --check and cannot import a baseline')
    if a.import_baseline: bootstrap()
    else:
        d=json.loads(a.content.read_text(encoding='utf-8'))
        if a.check:
            raise SystemExit(check_content(d, a.require_current_sources))
        else:
            assert a.out_dir
            validate_legacy_build(d)
            variants=[True,False] if a.campus=='both' else [a.campus=='yes']
            outputs=[]
            for campus in variants:
                label=('含实习' if a.internship=='yes' else '无实习')+('与校园' if campus else '无校园')
                outputs.append((campus,a.out_dir/('彭博裕-嵌入式软件工程师-'+label+'.docx')))
            targets=[p for _,p in outputs]+[a.out_dir/'approved-content.json',a.out_dir/'selection.json']
            if any(p.exists() for p in targets): raise ValueError('Delivery already exists; use a new revision directory')
            for campus,path in outputs:
                build(d,path,campus,a.internship=='yes')
            (a.out_dir/'approved-content.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            (a.out_dir/'selection.json').write_text(json.dumps({'internship':a.internship,'campus':a.campus,'content_sha256':digest(a.content)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
