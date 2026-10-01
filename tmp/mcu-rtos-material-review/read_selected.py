import sys,json
from pathlib import Path
from pypdf import PdfReader
BASE=Path(__file__).parent
sources=json.loads((BASE/'sources.json').read_text(encoding='utf-8'))
mode=sys.argv[1]
if mode=='pages':
    i=int(sys.argv[2]); raw=(BASE/('%02d.txt'%i)).read_text(encoding='utf-8')
    blocks=raw.split('=== PDF PAGE ')[1:]
    ranges=sys.argv[3:]
    wanted=set()
    for r in ranges:
        a,_,b=r.partition('-');wanted.update(range(int(a),int(b or a)+1))
    for block in blocks:
        n=int(block.split(' ===')[0])
        if n in wanted:print('=== PDF PAGE '+block)
elif mode=='heads':
    for i in map(int,sys.argv[2:]):
        p=BASE/('%02d.txt'%i)
        if not p.exists():continue
        print('\nFILE',i,Path(sources[i]).name)
        for block in p.read_text(encoding='utf-8').split('=== PDF PAGE ')[1:]:
            lines=[s.strip() for s in block.splitlines()[1:] if s.strip()]
            lines=[s for s in lines if s not in ['嵌入式八股文一网打尽版','嵌入式八股文精简版','8/6/2022'] and not __import__('re').match(r'^\d+\s*/\s*\d+$',s)]
            print(block.split(' ===')[0]+': '+' | '.join(lines[:3])[:160])
