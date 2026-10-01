import json, hashlib, re
from pathlib import Path
from pypdf import PdfReader

root = Path(r'E:\嵌入式学习资料（开发板加freertos）\面试八股文\八股文-外部获取')
out = Path(__file__).parent / 'external'
out.mkdir(exist_ok=True)
records = []
for n, p in enumerate(sorted(root.glob('*.pdf'))):
    pages = [page.extract_text() or '' for page in PdfReader(p).pages]
    target = out / f'{n}.txt'
    target.write_text('\n\n'.join(f'=== PDF PAGE {i+1} ===\n{t}' for i,t in enumerate(pages)), encoding='utf-8')
    records.append({'id': n, 'source': str(p), 'pages': len(pages), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'text': str(target)})
    print(f'FILE {n}: {p.name}; {len(pages)} pages')
    for i,t in enumerate(pages):
        clean = re.sub(r'\s+', ' ', t)
        print(f'{i+1}: {clean[:115]}')
(out / 'manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
