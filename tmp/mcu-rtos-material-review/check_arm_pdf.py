from pathlib import Path
import json,re
from pypdf import PdfReader
from PIL import Image, ImageOps, ImageDraw

root=Path(__file__).resolve().parents[2]
folder=Path(__file__).parent
data=json.loads((root/'记忆与产物/03-知识资料/ARM面试修订内容.json').read_text(encoding='utf-8'))
r=PdfReader(root/'记忆与产物/03-知识资料/Cortex系列-ARM面试修订版.pdf')
assert len(r.pages)==45
assert len(r.outline)==45
for i,q in enumerate(data['questions']):
    text=r.pages[i+3].extract_text()
    assert q['id'] in text,(i,'id')
    assert '先读指南' in text and '没懂再查' in text,(i,'references')
    for label,body in q['body']:
        assert label in text,(i,label)
        assert re.sub(r'\s+','',body) in re.sub(r'\s+','',text),(i,'body')
    assert re.search(r'p\d+',q['read'])
    for a,b in re.findall(r'p(\d+)(?:～(\d+))?',q['read']+' '+q['more']):
        assert 1<=int(a)<=322 and (not b or int(a)<=int(b)<=322)
    assert len(text)>400
assert sum(len(p.get('/Annots',[])) for p in r.pages)>=50
files=sorted(folder.glob('arm-detailed-[0-9][0-9].png'))
assert len(files)==45
for start in range(0,len(files),9):
    sheet=Image.new('RGB',(900,1290),'#c9d3db')
    d=ImageDraw.Draw(sheet)
    for j,path in enumerate(files[start:start+9]):
        im=Image.open(path).convert('RGB')
        im.thumbnail((290,401))
        x=(j%3)*300+5;y=(j//3)*430+22
        sheet.paste(im,(x,y));d.text((x,y-17),path.stem,fill='black')
    sheet.save(folder/f'arm-detailed-contact-{start//9+1}.png')
report={'pages':len(r.pages),'questions':40,'bookmarks':len(r.outline),'all_questions_have_individual_references':True,'all_body_text_preserved':True,'rendered_pages':len(files),'status':'PASS'}
(folder/'arm-detailed-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
