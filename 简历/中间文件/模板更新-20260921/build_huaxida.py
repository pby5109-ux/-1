#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""华曦达·嵌入式开发工程师 定制版。
基准：旧版简历/9.26/彭博裕-嵌入式软件工程师-含实习与校园.docx（含实习＋短版校园）
改动：删实习栏；正文套用 -10 最新文字；校园改长版（机构标题行＋两条）；
     求职意向改嵌入式开发工程师；正文 8→9pt；行距/段前微调保一页。
只替换 word/document.xml，其余部件与基准逐字节一致。"""
import copy, hashlib, sys, zipfile
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

BASE = Path(r"D:\APP\project_practice\codex-project\简历\简历修改版本\模板简历（随时跟新）\旧版简历\9.26\彭博裕-嵌入式软件工程师-含实习与校园.docx")
EXPECTED = "E6E1227599E3A226CE0A1EA80887E72228D3DD18A7FCBC637F9AE404A6206236"
TARGET = "嵌入式开发工程师"
CAMPUS_MODE = sys.argv[6] if len(sys.argv) > 6 else "long"   # long=长版两条件, short=一句话
INTERNSHIP_INDEXES = (26, 27, 28, 29, 30)
SIZE_MAP = {"16": "18", "18": "20", "19": "21", "20": "22"}   # 正文8→9pt
LINE_TWIPS = sys.argv[2] if len(sys.argv) > 2 else "218"
TOP_MARGIN = sys.argv[4] if len(sys.argv) > 4 else "280"     # 上边距（twips）
BOTTOM_MARGIN = sys.argv[5] if len(sys.argv) > 5 else "259"  # 下边距（twips）
HEAD_TWIPS = sys.argv[3] if len(sys.argv) > 3 else "12"
TEXT_OVERRIDES = {
    "项目简介#1": "集成示波器、数字万用表、可调直流电源和信号发生器，支持波形实时显示及频率、幅度测量，频率测量误差1 Hz，电压与电阻测量误差1%；支持直流电压稳定输出；信号发生器输出正弦、方波等，频率档位覆盖50 Hz～80kHz。",
    "并发优化": "针对采集与显示共享缓冲区的读写冲突，设计双缓冲与状态机协同机制，管理波形数据的读写权限和切换时机，保证单帧绘制期间数据一致，避免新旧帧混用，并允许新帧准备与当前帧绘制并行。",
    "测量与调试": "基于内部参考电压估算VDDA，结合GPIO档位识别、分压与偏置补偿完成多量程换算，提升测量准确性；优化采样率与波表长度配置、定时参数计算及更新时序，修正低频输出偏差，实现频率切换及时生效。",
    "系统开发": "分层封装传感器驱动与采集逻辑，设计RTC周期采集与按键唤醒双事件机制，分别维护采样与显示期限，避免临时查看打乱上报节拍；支持无网关条件下现场查看数据，并通过有效性检查标识采集异常，保障不同情况下数据的有效观测。",
    "功耗优化": "结合Stop模式、代码系统优化、外设供电门控与休眠控制，抑制GPIO漏电并隔离断电外设信号，将整板待机电流控制在µA级。",
    "协议开发": "设计CRC校验、序号匹配及ACK超时有限重试机制，实现上报确认与传输异常处理；开发PC网关处理半包、粘包及坏帧，按节点与序号去重且对重传仍回ACK，完成数据解析及带时间的故障日志记录，支持采集异常追溯。",
    "目标筛选": "在矩形检测基础上，融合面积、对边长度差及平行垂直约束校验候选靶框，并按面积优先逐一筛选，避免单一最大框选择造成目标遗漏，最终实现目标精准判定与定位。",
    "光照适配": "基于Otsu算法自动估计灰度阈值，通过按键触发重估、帧间保持阈值，实现不同光环境下的阈值校准；对无灰度对比的画面跳过识别并重试，避免无效画面参与阈值估计。",
    "AI工具": "熟练使用Codex、Claude Code、DeepSeek Harness、ZCode搭建工作流并实现快速产品设计与开发。",
}
CAMPUS_TITLE = ("山东建筑大学校学生会科创部", "部长", "2023.09—2025.06")
CAMPUS_BULLETS = [
    ("科创组织", "统筹约50名成员，参与组织电赛、西门子杯、蓝桥杯及国产MCU产品等校级宣讲，负责人员分工、跨部门协调、宣传物料、会场布置与流程安排，保障活动按计划落地。"),
    ("现场保障", "参与组织文艺晚会、校园歌手大赛等200余人活动，设置双麦克风及主备音响保障方案；音频设备突发故障后按预案切换备用设备，恢复现场声音并保障活动继续进行。"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest().upper()


def replace_runs(paragraph, segments):
    old = list(paragraph.runs)
    if not old:
        raise ValueError('段落无可继承格式')
    styles = [copy.deepcopy(r._r.rPr) if r._r.rPr is not None else None for r in old]
    for r in old:
        paragraph._p.remove(r._r)
    for text, idx in segments:
        run = paragraph.add_run(text)
        st = styles[min(idx, len(styles) - 1)]
        if st is not None:
            run._r.insert(0, copy.deepcopy(st))


def labelled(paragraph, label, text, bullet=False):
    prefix = f"• {label}：" if bullet else f"{label}："
    replace_runs(paragraph, [(prefix, 0), (text, 1)])


def apply_overrides(doc):
    seen = {}; applied = 0
    for p in doc.paragraphs:
        t = p.text
        if '：' not in t: continue
        bullet = t.lstrip().startswith('•')
        label = t.lstrip().lstrip('•').strip().split('：', 1)[0].strip()
        seen[label] = seen.get(label, 0) + 1
        key = label if label not in ('项目简介', '项目职责') else f"{label}#{seen[label]}"
        if key not in TEXT_OVERRIDES: continue
        labelled(p, label, TEXT_OVERRIDES[key], bullet=bullet)
        applied += 1
    return applied


def build_campus_long(doc):
    """把短版校园句子替换为：机构标题行表格＋两条加粗条目。返回 (表格, 两条段落)。"""
    sentence = None
    proto_bullet = None
    for p in doc.paragraphs:
        t = p.text.strip()
        if sentence is None and t.startswith('担任校学生会科创部部长'):
            sentence = p
        if proto_bullet is None and t.startswith('• 架构交互'):
            proto_bullet = p
    if sentence is None or proto_bullet is None:
        raise ValueError('未找到校园短版句子或条目样板')
    tbl_el = copy.deepcopy(doc.tables[4]._tbl)          # 克隆第三个项目标题表
    b1 = copy.deepcopy(proto_bullet._p)
    b2 = copy.deepcopy(proto_bullet._p)
    sentence._p.addprevious(tbl_el)
    sentence._p.addprevious(b1)
    sentence._p.addprevious(b2)
    sentence._p.getparent().remove(sentence._p)
    # 写入文字
    from docx.table import Table
    campus_table = None
    for t in doc.tables:
        if '基于MSPM0与K230的移动目标瞄准系统' in t.cell(0, 0).text and '2023' not in t.cell(0, 1).text:
            campus_table = t                              # 克隆源仍是项目文字，取第一份
            break
    name, role, period = CAMPUS_TITLE
    replace_runs(campus_table.cell(0, 0).paragraphs[0], [(name, 0), (f'｜{role}', 1)])
    replace_runs(campus_table.cell(0, 1).paragraphs[0], [(period, 0)])
    for (label, text), element in zip(CAMPUS_BULLETS, (b1, b2)):
        labelled(Paragraph(element, doc), label, text, bullet=True)
    return campus_table


def main():
    out = Path(sys.argv[1])
    if out.exists():
        print(f'ERROR: 输出已存在：{out}'); return 2
    if sha256(BASE) != EXPECTED:
        print(f'ERROR: 基准哈希不符：{sha256(BASE)}'); return 2
    print('基准哈希核对通过')
    doc = Document(BASE)
    body = doc.element.body
    children = list(body)
    removed = 0
    for i in INTERNSHIP_INDEXES:
        e = children[i]
        if e.getparent() is not None:
            e.getparent().remove(e); removed += 1
    print(f'实习经历栏已删除（{removed}元素）')
    print('正文覆盖 %d 处' % apply_overrides(doc))
    if CAMPUS_MODE == 'long':
        build_campus_long(doc)
        print('校园经历已改为长版')
    else:
        print('校园经历保持短版一句话')
    header_cell = doc.tables[0].cell(0, 0)
    for run in header_cell.paragraphs[0].runs:
        if '嵌入式软件工程师' in run.text:
            run.text = run.text.replace('嵌入式软件工程师', TARGET)
    print('求职意向 ->', TARGET)
    n = 0
    for run in body.iter(qn('w:r')):
        rPr = run.find(qn('w:rPr'))
        if rPr is None: continue
        for tag in ('w:sz', 'w:szCs'):
            e = rPr.find(qn(tag))
            if e is not None and e.get(qn('w:val')) in SIZE_MAP:
                e.set(qn('w:val'), SIZE_MAP[e.get(qn('w:val'))]); n += 1
    print(f'字号提升 {n} 处')
    m = k = 0
    heads = {'教育背景', '竞赛与荣誉', '项目经历', '专业技能', '校园经历'}
    for p in doc.paragraphs:
        pPr = p._p.find(qn('w:pPr'))
        if pPr is None: continue
        sp = pPr.find(qn('w:spacing'))
        if sp is None: continue
        if sp.get(qn('w:line')): sp.set(qn('w:line'), LINE_TWIPS); m += 1
        if p.text.strip() in heads and sp.get(qn('w:before')) not in (None, '0'):
            sp.set(qn('w:before'), HEAD_TWIPS); k += 1
    print(f'行距 {m} 处→{LINE_TWIPS}，段前 {k} 处→{HEAD_TWIPS}')
    from docx.shared import Twips as _Tw
    for sec in doc.sections:
        sec.top_margin = _Tw(int(TOP_MARGIN))
        sec.bottom_margin = _Tw(int(BOTTOM_MARGIN))
    print(f'页边距：上 {TOP_MARGIN}、下 {BOTTOM_MARGIN} twips')
    out.parent.mkdir(parents=True, exist_ok=True)
    staged = out.with_name(out.stem + '.staged.docx'); doc.save(staged)
    with zipfile.ZipFile(BASE) as z, zipfile.ZipFile(staged) as e:
        edited = e.read('word/document.xml')
    with zipfile.ZipFile(BASE) as z, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as o:
        for item in z.infolist():
            o.writestr(item, edited if item.filename == 'word/document.xml' else z.read(item.filename))
    staged.unlink()
    with zipfile.ZipFile(out) as a:
        if a.testzip() is not None:
            print('ERROR: DOCX 损坏'); return 2
    print('OK:', out)
    return 0


raise SystemExit(main())
