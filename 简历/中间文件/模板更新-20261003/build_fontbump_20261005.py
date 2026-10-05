# -*- coding: utf-8 -*-
"""-01 母版更新：实习三条换用户 10-05 精简稿；全文字号加大一档
（正文8.5→9pt、栏目标题10→11pt、19→21、18→20），行距214→200补偿保一页。"""
import copy, hashlib, zipfile
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn

BASE = Path(r"D:\APP\project_practice\codex-project\简历\简历修改版本\模板简历（随时跟新）\模板简历\彭博裕-嵌入式软件工程师-01.docx")
EXPECTED = "5992566855149656"
OUT = Path(r"D:\APP\project_practice\codex-project\简历\中间文件\模板更新-20261003\彭博裕-嵌入式软件工程师-01.docx")

P1_INTRO = "集成示波器、数字万用表、可调直流电源与信号发生器，支持波形实时显示及频率、幅度测量，频率测量误差极小，电压与电阻测量误差1%；支持DC-DC升压电路实现直流稳压输出；信号发生器输出正弦、方波等，频率覆盖50 Hz～80 kHz。"
INTERNSHIP_NEW = [
    ("产品认知", "围绕DTZY178三相四线智能电表，结合手册与电表主板梳理主控、采样计量、通信及显示模块，认识主要器件与各模块的连接关系。"),
    ("功能理解", "结合产品培训与手册阅读，了解电量计量、远程费控与数据上报功能，梳理测量输入、主控处理与设备响应各环节之间的对应联系。"),
    ("通信排查", "参与电表采集异常排查，通过供电测量、RS485线路检查与载波模块状态观察，定位线路短路及模块异常，确认处理后采集恢复正常运行。"),
]
SIZE_MAP = {"17": "18", "18": "20", "19": "21", "20": "22"}   # 半点值：8.5→9、9→10、9.5→10.5、10→11
LINE_OLD, LINE_NEW = "214", "186"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest().upper()


def replace_runs(paragraph, segments):
    old = list(paragraph.runs)
    if not old:
        raise ValueError('空段落')
    styles = [copy.deepcopy(r._r.rPr) if r._r.rPr is not None else None for r in old]
    for r in old:
        paragraph._p.remove(r._r)
    for text, idx in segments:
        run = paragraph.add_run(text)
        st = styles[min(idx, len(styles) - 1)]
        if st is not None:
            run._r.insert(0, copy.deepcopy(st))


def main():
    if not sha256(BASE).startswith(EXPECTED):
        print(f'ERROR: 基准哈希不符：{sha256(BASE)[:16]}'); return 2
    doc = Document(BASE)

    # 1) 实习三条
    intern = 0
    for p in doc.paragraphs:
        t = p.text.strip()
        core = t[2:] if t.startswith("• ") else t
        label = core.split("：", 1)[0]
        if t.startswith("项目简介：集成示波器"):
            replace_runs(p, [("项目简介：", 0), (P1_INTRO, 1)])
            print('仪器简介已精简')
        for nl, ntext in INTERNSHIP_NEW:
            if label == nl and core[len(label) + 1:] != ntext:
                replace_runs(p, [(f"• {nl}：", 0), (ntext, 1)])
                intern += 1
    if intern != 3:
        print(f'ERROR: 实习三条命中 {intern}/3'); return 2
    print('实习三条已更新')

    # 1b) 表头联系行保持 9pt（10pt 会把"2027届"挤换行）
    for p in doc.tables[0].cell(0, 0).paragraphs:
        if "电话：" in p.text:
            for r in p.runs:
                rPr = r._r.find(qn('w:rPr'))
                if rPr is not None:
                    for tag in ('w:sz', 'w:szCs'):
                        e = rPr.find(qn(tag))
                        if e is not None:
                            e.set(qn('w:val'), '18')
            print('联系行已回 9pt')

    # 2) 字号整体提一档
    body = doc.element.body
    n = 0
    for run in body.iter(qn('w:r')):
        rPr = run.find(qn('w:rPr'))
        if rPr is None:
            continue
        for tag in ('w:sz', 'w:szCs'):
            e = rPr.find(qn(tag))
            if e is not None and e.get(qn('w:val')) in SIZE_MAP:
                e.set(qn('w:val'), SIZE_MAP[e.get(qn('w:val'))]); n += 1
    print(f'字号提升 {n} 处')

    # 3) 行距 214→200（仅正文 auto 行）
    m = 0
    for p in doc.paragraphs:
        pPr = p._p.find(qn('w:pPr'))
        if pPr is None:
            continue
        sp = pPr.find(qn('w:spacing'))
        if sp is not None and sp.get(qn('w:line')) == LINE_OLD and sp.get(qn('w:lineRule')) == 'auto':
            sp.set(qn('w:line'), LINE_NEW); m += 1
    print(f'行距 {m} 处 {LINE_OLD}→{LINE_NEW}')

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
    print("差异部件：", diff)
    if diff != ['word/document.xml']:
        print('ERROR: 差异部件异常'); return 2
    print('OK:', OUT)
    return 0


raise SystemExit(main())
