# -*- coding: utf-8 -*-
"""-01 母版修正：移除"协议开发"条的分界线（项目经历末项后接栏目标题，无需分隔线）。
分界线规则澄清（用户10-05）：仅项目与项目之间加分界线；每个项目经历区的最后一个项目不加。"""
import hashlib, zipfile
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn

BASE = Path(r"D:\APP\project_practice\codex-project\简历\简历修改版本\模板简历（随时跟新）\模板简历\彭博裕-嵌入式软件工程师-01.docx")
EXPECTED = "1315F5710F1FE829"
OUT = Path(r"D:\APP\project_practice\codex-project\简历\中间文件\模板更新-20261003\彭博裕-嵌入式软件工程师-01.docx")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest().upper()


def main():
    if not sha256(BASE).startswith(EXPECTED):
        print(f'ERROR: 基准哈希不符：{sha256(BASE)[:16]}'); return 2
    doc = Document(BASE)

    removed = 0
    for p in doc.paragraphs:
        t = p.text.strip()
        core = t[2:] if t.startswith("• ") else t
        if core.split("：", 1)[0] == "协议开发":
            pPr = p._p.find(qn('w:pPr'))
            if pPr is not None:
                pBdr = pPr.find(qn('w:pBdr'))
                if pBdr is not None:
                    pPr.remove(pBdr); removed += 1
    if removed != 1:
        print(f'ERROR: pBdr 移除 {removed}/1'); return 2

    OUT.parent.mkdir(parents=True, exist_ok=True)
    staged = OUT.with_name(OUT.stem + '.staged.docx')
    doc.save(staged)
    with zipfile.ZipFile(staged) as e:
        edited = e.read('word/document.xml')
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as o, zipfile.ZipFile(BASE) as z:
        for item in z.infolist():
            o.writestr(item, edited if item.filename == 'word/document.xml' else z.read(item.filename))
    staged.unlink()

    diff = []
    with zipfile.ZipFile(BASE) as a, zipfile.ZipFile(OUT) as b:
        assert b.testzip() is None
        for name in a.namelist():
            if hashlib.sha256(a.read(name)).hexdigest() != hashlib.sha256(b.read(name)).hexdigest():
                diff.append(name)
    print("已移除：协议开发分界线"); print("差异部件：", diff)
    if diff != ['word/document.xml']:
        print('ERROR: 差异部件异常'); return 2
    print('OK:', OUT)
    return 0


raise SystemExit(main())
