"""Current template v2: one content source, optional one-sentence campus section.

Only word/document.xml changes; all other ZIP parts remain byte-identical.
Use --import-baseline once to establish the content source; normal builds read JSON.
"""
from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile
import argparse
import hashlib
import json
from lxml import etree as E

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

def validate(d):
    assert d['schema_version']==2 and d['approved'] is True, 'Explicit approval required'
    assert d['approval_record']['source'] and d['content_revision']
    assert len(d['education'])==4 and len(d['projects'])==3
    assert len({p['id'] for p in d['projects']})==3
    assert len(d['enterprise']['bullets'])==3
    assert d['campus']['text'].count('。')==1 and '\n' not in d['campus']['text']
    assert 3 <= len(d['skills']) <= 6
    entries=d['honors']+d['skills']+d['enterprise']['bullets']+[d['campus']]
    for p in d['projects']:
        assert p['name'] and p['keywords'] and 1<=len(p['bullets'])<=4
        entries += [p['intro'],p['duty']]+p['bullets']
    for it in entries:
        assert it['text'].strip() and it['source_refs']
        assert all(s in d['sources'] for s in it['source_refs'])
    assert d['layout']['line_twips']>=230, 'Do not compress line height below reference'
    return True

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
    validate(d)
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
    p.add_argument('--internship',choices=['yes','no'],default='yes')
    p.add_argument('--campus',choices=['yes','no','both'],default='both');a=p.parse_args()
    if a.import_baseline: bootstrap()
    else:
        d=json.loads(a.content.read_text(encoding='utf-8'));validate(d)
        if a.check: print('OK content structure and source references (not an independent fact verification)')
        else:
            assert a.out_dir
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
