import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'packages'))
import pymupdf as fitz
base=Path(r'D:/APP/project_practice/codex-project/简历/简历修改版本/模板简历（随时跟新）/模板简历/彭博裕-嵌入式软件工程师-10.pdf')
d=fitz.open(base)
for b in d[0].get_text('dict')['blocks']:
    if b['type']!=0: continue
    for line in b['lines']:
        for s in line['spans']:
            if s['bbox'][1]>700 or '99%' in s['text']:
                print(repr(s['text']),s['font'],s['size'],s['bbox'],s['origin'])
print('fonts',d[0].get_fonts())
