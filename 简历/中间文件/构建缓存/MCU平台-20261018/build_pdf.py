"""Patch the selected user PDF; preserve all unrelated layout and content."""
import hashlib,json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
CACHE=Path(__file__).parent
sys.path.insert(0,str(CACHE/'packages'))
import pymupdf as fitz
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import ImageChops,ImageDraw

ROOT=Path(r'D:/APP/project_practice/codex-project/简历')
BASE=ROOT/'简历修改版本/模板简历（随时跟新）/模板简历/彭博裕-嵌入式软件工程师-10.pdf'
OUTDIR=ROOT/'定制投递/MCU平台岗位-嵌入式软件工程师-20261018'
OUT=OUTDIR/'彭博裕-嵌入式软件工程师-10.pdf'
cfg=json.loads((CACHE/'changes.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
norm=lambda s:re.sub(r'\s+','',s)
assert sha(BASE)==cfg['base_sha256'],'Base changed; reread before editing'
assert not OUT.exists(),'Refusing overwrite'
d=fitz.open(BASE)
assert len(d)==1 and abs(d[0].rect.height-841.89)<2
page=d[0]
original=page.get_text(sort=True)
heading=page.search_for('专业技能')
label=page.search_for('编程基础：')
assert len(heading)==1 and len(label)==1
spans=[s for b in page.get_text('dict')['blocks'] if b['type']==0 for line in b['lines'] for s in line['spans']]
first=next(s for s in spans if s['text']=='编程基础：')
start_y=first['origin'][1]
x0=first['origin'][0]
size=first['size']
assert size==9.0
rect=fitz.Rect(x0-.3,label[0].y0-.4,561,830)
metrics=page.search_for('99%')
assert len(metrics)==1
mr=metrics[0]
ms=next(s for s in spans if '99%' in s['text'])

# Remove old text, not merely cover it: text extraction must not retain both copies.
page.add_redact_annot(rect,fill=(1,1,1))
page.add_redact_annot(mr,fill=(1,1,1))
page.apply_redactions(images=0,graphics=0)

# Preserve the original 9pt YaHei style; use native MuPDF font subsetting.
regular=fitz.Font(fontfile='C:/Windows/Fonts/msyh.ttc')
bold=fitz.Font(fontfile='C:/Windows/Fonts/msyhbd.ttc')
page.insert_font(fontname='skillreg',fontfile='C:/Windows/Fonts/msyh.ttc')
page.insert_font(fontname='skillbold',fontfile='C:/Windows/Fonts/msyhbd.ttc')
page.insert_font(fontname='metricfont',fontfile='C:/Windows/Fonts/arial.ttf')
page.insert_text(ms['origin'],'98%',fontname='metricfont',fontsize=ms['size'],color=(.125,.153,.2))

right=559.0
line_height=12.72
y=start_y
line_count=0
for item in cfg['skills']:
    prefix=item['label']+'：'
    page.insert_text((x0,y),prefix,fontname='skillbold',fontsize=size,color=(.125,.153,.2))
    x=x0+bold.text_length(prefix,fontsize=size)+.3
    line=''
    for ch in item['text']:
        trial=line+ch
        if regular.text_length(trial,fontsize=size)>right-x:
            assert line,'Unrenderable glyph'
            page.insert_text((x,y),line,fontname='skillreg',fontsize=size,color=(.125,.153,.2))
            y+=line_height;line_count+=1;x=x0;line=ch
        else:line=trial
    if line:
        page.insert_text((x,y),line,fontname='skillreg',fontsize=size,color=(.125,.153,.2))
        line_count+=1
    y+=line_height
assert y-line_height<827,'Skills overflow; shorten wording, never shrink type'
OUTDIR.mkdir(parents=True,exist_ok=True)
d.subset_fonts()
d.save(OUT,garbage=4,deflate=True)
d.close()

# Check visual preservation outside the precisely scoped edits, using PDFium.
def raster(path):
    doc=pdfium.PdfDocument(str(path));page=doc[0]
    image=page.render(scale=2).to_pil().convert('RGB')
    page.close();doc.close()
    return image
before,after=raster(BASE),raster(OUT)
before.save(CACHE/'base.png');after.save(CACHE/'final.png')
diff=ImageChops.difference(before,after)
mask=ImageDraw.Draw(diff)
for r in [rect,mr]:
    mask.rectangle(tuple(v*2 for v in (r.x0-2,r.y0-2,r.x1+2,r.y1+2)),fill=(0,0,0))
assert diff.getbbox() is None,'Unexpected visual change outside edited areas'
reader=PdfReader(OUT)
text=''.join(p.extract_text() for p in reader.pages)
assert len(reader.pages)==1
for item in cfg['skills']:assert norm(item['text']) in norm(text),item['label']
assert '99%' not in text and norm(text).count('98%')>=2
for phrase in ['17668025109','pbyuqianrushi@163.com','校园经历','54','8个月','丢包率低于5%']:
    assert norm(phrase) in norm(text),phrase
assert '实习经历' not in text
assert sha(BASE)==cfg['base_sha256']
sources={
 'selected-pdf-10':{'path':str(BASE),'sha256':sha(BASE),'status':'user_edited_wording_baseline'},
 'user-metric-20261011':{'status':'user_confirmed_exact_delta','reference':'98%已在skill/current-workflow及current-content中获批'},
 'user-packet-loss-20261018':{'status':'user_confirmed','reference':cfg['packet_loss']}
}
snapshot={
 'schema_version':2,'snapshot_kind':'direct_pdf_patch','approved':True,
 'authorization_mode':'delegated_jd','content_revision':'20261018-mcu10-v1',
 'approval_record':{'approved_by':'user_and_standing_jd_authorization','approved_on':'2026-10-18','approval_note':'用户要求使用10进行修改；技能按常设授权调整。项目只执行此前98%准确授权，新增丢包指标由当轮用户确认实测保留。校园/项目其余原文未改。'},
 'sources':sources,
 'selection':{'campus_variant':'long','internship':'no','combo':'10','project_order':['instrument','car_contest','lora_node']},
 'skills':cfg['skills'],'protected_changes':[cfg['metric_change']],
 'unchanged_content_source':'selected-pdf-10','baseline_text':original,'final_text':text,
 'output':{'path':str(OUT),'sha256':sha(OUT)},
 'validation':{'pages':1,'A4_points':list(reader.pages[0].mediabox),'skills_font_size':size,'skills_lines':line_count,'skills_last_baseline':y-line_height,'unrelated_pixels_changed':0,'old_skills_removed':True,'old_99_removed':True}
}
print(json.dumps(snapshot,ensure_ascii=False,default=float))
