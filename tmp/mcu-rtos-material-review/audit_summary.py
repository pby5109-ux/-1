import json,re,unicodedata
from pathlib import Path
root=Path(__file__).parent
rows=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
for row in rows:
    print(row['id'],Path(row['source']).name,row.get('pages'),row.get('characters'),row.get('error',''))
groups={}
for row in rows: groups.setdefault(row['sha256'],[]).append(row['id'])
print('IDENTICAL_SHA256', [x for x in groups.values() if len(x)>1])
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s))
full=norm((root/'52.txt').read_text(encoding='utf-8'))
for i in range(40,52):
    s=(root/f'{i:02}.txt').read_text(encoding='utf-8')
    lines=[norm(x) for x in s.splitlines() if len(norm(x))>=20 and not x.startswith('===')]
    matches=sum(x in full for x in lines)
    print('SPLIT_OVERLAP',i,matches,len(lines),'long_lines_in_81_page_book')
