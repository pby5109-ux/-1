import sys, json, hashlib, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
from pypdf import PdfReader

BASE = Path(__file__).parent
manifest = json.loads((BASE / 'sources.json').read_text(encoding='utf-8'))
out = []
for i, name in enumerate(manifest):
    p = Path(name)
    try:
        if p.suffix.lower() == '.pdf':
            reader = PdfReader(p)
            pages = [page.extract_text() or '' for page in reader.pages]
        else:
            with zipfile.ZipFile(p) as z:
                root = ET.fromstring(z.read('word/document.xml'))
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            pages = ['\n'.join(''.join(el.itertext()) for el in root.findall('.//w:t', ns))]
        dest = BASE / ('%02d.txt' % i)
        dest.write_text('\n\n'.join('=== PDF PAGE %d ===\n%s' % (n+1,t) for n,t in enumerate(pages)), encoding='utf-8')
        entry = dict(id=i, source=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), pages=len(pages), characters=sum(map(len,pages)), empty_pages=[n+1 for n,t in enumerate(pages) if len(t.strip())<30], text=str(dest))
        out.append(entry)
        print(json.dumps(entry, ensure_ascii=False), flush=True)
    except Exception as e:
        out.append(dict(id=i, source=str(p), error=str(e)))
        print('ERROR', i, str(e), flush=True)
(BASE / 'manifest.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
