# -*- coding: utf-8 -*-
"""-01 母版：项目经历中三条"项目职责"行整行加粗（标签+内容），用户 10-07 新版式规则。"""
import copy, hashlib, zipfile
from pathlib import Path
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE = Path(r"D:\APP\project_practice\codex-project\简历\简历修改版本\模板简历（随时跟新）\模板简历\彭博裕-嵌入式软件工程师-01.docx")
EXPECTED = "712466C343A4FE5A"
OUT = Path(r"D:\APP\project_practice\codex-project\简历\中间文件\模板更新-20261003\彭博裕-嵌入式软件工程师-01.docx")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest().upper()


def make_bold(paragraph):
    for r in paragraph.runs:
        r.font.bold = True   # python-docx 按 rPr 合法顺序插入 w:b
        rPr = r._r.find(qn('w:rPr'))
        b = rPr.find(qn('w:b'))
        if rPr.find(qn('w:bCs')) is None:
            bCs = OxmlElement('w:bCs')
            b.addnext(bCs)   # bCs 紧随 b
    return len(paragraph.runs)


def main():
    if not sha256(BASE).startswith(EXPECTED):
        print(f'ERROR: 基准哈希不符：{sha256(BASE)[:16]}'); return 2
    doc = Document(BASE)

    hit = 0
    for p in doc.paragraphs:
        t = p.text.strip()
        if t.startswith("项目职责："):
            make_bold(p)
            hit += 1
    if hit != 3:
        print(f'ERROR: 项目职责段命中 {hit}/3'); return 2

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
    print(f"已加粗 {hit} 条项目职责行"); print("差异部件：", diff)
    if diff != ['word/document.xml']:
        print('ERROR: 差异部件异常'); return 2
    print('OK:', OUT)
    return 0


raise SystemExit(main())
