"""Rebuild source extracts and validate generated practice artifacts, never the four projects."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from datetime import datetime
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
parser = argparse.ArgumentParser()
parser.add_argument('--pdf-dir', required=True)
parser.add_argument('--host-gcc', required=True)
parser.add_argument('--arm-gcc', required=True)
parser.add_argument('--node', required=True)
args = parser.parse_args()
report = {'generated_at':datetime.now().astimezone().isoformat(), 'source_pdfs':[], 'checks':[]}
for part,expected_pages in [(1,7),(2,8),(3,11),(4,6)]:
    src=Path(args.pdf_dir)/f'嵌入式岗位笔试面试真题讲解1-{part}.pdf'
    reader=PdfReader(src)
    assert len(reader.pages)==expected_pages
    text='\n\n'.join(f'=== PDF物理页码 {i+1} ===\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages))
    text=re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','',text)
    (HERE/f'原文提取1-{part}.txt').write_text(text,encoding='utf-8')
    report['source_pdfs'].append({'name':src.name,'pages':len(reader.pages),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
qs=json.loads((HERE/'题库源数据.json').read_text(encoding='utf-8'))['questions']
ids=[q['id'] for q in qs]
assert ids==[f'C{i:02d}' for i in range(1,53)]
for file in ['01-题目卷.md','02-答案与解析.md']:
    body=(ROOT/file).read_text(encoding='utf-8')
    assert re.findall(r'^### (C\d{2})｜',body,re.M)==ids
    assert body.count('~~~')%2==0
    assert '\ufffd' not in body
assert '#### 答案与解析' not in (ROOT/'01-题目卷.md').read_text(encoding='utf-8')
report['structure']=json.loads((HERE/'结构验证.json').read_text(encoding='utf-8'))

class PageCheck(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.links=[]; self.scripts=[]; self.in_script=False; self.answers=0; self.open_answers=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.append(d['id'])
        if tag=='a' and 'href' in d:self.links.append(d['href'])
        if tag=='details' and d.get('class')=='answer':
            self.answers+=1;self.open_answers+=('open' in d)
        if tag=='script':
            assert 'src' not in d, 'Offline page must not fetch scripts'
            self.in_script=True
    def handle_endtag(self,tag):
        if tag=='script':self.in_script=False
    def handle_data(self,data):
        if self.in_script:self.scripts.append(data)
page=PageCheck();page.feed((ROOT/'03-手机自测版.html').read_text(encoding='utf-8'))
assert len(page.ids)==len(set(page.ids))
assert page.answers==52 and page.open_answers==0
for href in page.links:
    if href.startswith('#'):assert href[1:] in page.ids
    elif not urlsplit(href).scheme:
        assert (ROOT/unquote(urlsplit(href).path)).is_file(), href
report['html_static']={'unique_ids':True,'answers_default_closed':52,'local_links_valid':True,'external_scripts':0,'browser_visual_or_click_test':'NOT RUN: browser safety policy blocked file URL; no workaround attempted'}

build=HERE/'构建缓存'
build.mkdir(exist_ok=True)
def run(name, command, expect=0):
    result=subprocess.run([str(x) for x in command],capture_output=True,text=True,encoding='utf-8',errors='replace')
    entry={'name':name,'command':[str(x) for x in command],'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    entry['passed']=(result.returncode==expect) if expect is not None else result.returncode!=0
    report['checks'].append(entry)
    if not entry['passed']:
        (HERE/'验证报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        raise RuntimeError(name+' failed\n'+result.stdout+result.stderr)
    return result

run('host compiler version',[args.host_gcc,'--version'])
run('ARM compiler version',[args.arm_gcc,'--version'])
script_file=build/'mobile-script.js'
script_file.write_text('\n'.join(page.scripts),encoding='utf-8')
run('mobile JavaScript syntax',[args.node,'--check',script_file])
for optimization in ['-O0','-O2']:
    exe=build/('test'+optimization+'.exe')
    run('host compile '+optimization,[args.host_gcc,'-std=c11',optimization,'-Wall','-Wextra','-Wpedantic','-Wno-sign-compare','-Werror',HERE/'测试参考实现.c','-o',exe])
    run('host run '+optimization,[exe])
for src in ['参考实现.c','核对ARM模型.c']:
    run('ARM compile '+src,[args.arm_gcc,'-std=c11','-O2','-Wall','-Wextra','-Wpedantic','-Werror','-mcpu=cortex-m3','-mthumb','-c',HERE/src,'-o',build/(src+'.o')])

# Deliberately invalid snippets: compile diagnostics only, never execute.
invalid={
    'constant_increment':'#define LIMIT 3\nvoid f(void){LIMIT++;}\n',
    'suffix_after_parens':'#define YEAR (60*60*24*365)UL\nunsigned long x=YEAR;\n',
    'pointer_bitwise':'void f(int *p){p &= ~7;}\n',
    'cpp_scope_in_c':'int x;int f(void){return ::x;}\n',
    'write_const':'void f(void){const int x=1;x=2;}\n',
    'cast_array':'void f(unsigned long x){(void)(int *[])x;}\n',
}
for name,code in invalid.items():
    src=build/(name+'.c');src.write_text(code,encoding='utf-8')
    run('expected diagnostic '+name,[args.host_gcc,'-std=c11','-pedantic-errors','-fsyntax-only',src],expect=None)
report['boundaries']=['Host tests are not hardware tests.','ARM -c validates compilation/model only, not linking or board execution.','UB question examples were not executed.','No source-project build/flash or project code changes.']
report['all_passed']=all(x['passed'] for x in report['checks'])
report['reference_code_sha256']=hashlib.sha256((HERE/'参考实现.c').read_bytes()).hexdigest()
(HERE/'验证报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'questions':52,'pdf_pages':sum(p['pages'] for p in report['source_pdfs']),'checks':len(report['checks']),'all_passed':report['all_passed']},ensure_ascii=False))
