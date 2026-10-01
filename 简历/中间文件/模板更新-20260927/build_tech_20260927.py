# -*- coding: utf-8 -*-
"""技术岗三组合（00/01/10）统一重建：项目顺序改为 仪器→瞄准→LoRa，
正文按用户 09-27 更新的 -01 版逐字沿用（M 字母按视觉修正），字号 8.5→9pt。
基准：旧版简历/9.26/彭博裕-嵌入式软件工程师-含实习无校园.docx。只替换 word/document.xml。"""
import copy, hashlib, sys, zipfile
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

BASE = Path(r"D:\APP\project_practice\codex-project\简历\简历修改版本\模板简历（随时跟新）\旧版简历\9.26\彭博裕-嵌入式软件工程师-含实习无校园.docx")
EXPECTED = "C42B86ED97E858E116FCD5524ACFDADA49CE5E7E97C41AEB7F2B3747178346F2"
FONT_PT = sys.argv[5] if len(sys.argv) > 5 else "8.5"   # 正文字号
SIZE_MAP = ({"15": "18", "16": "18", "18": "20", "19": "21", "20": "22"} if FONT_PT == "9"
            else {"15": "17", "16": "17"})   # 9pt 档整体提一级；8.5pt 档仅正文提半级
LINE_TWIPS = sys.argv[2] if len(sys.argv) > 2 else "240"
HEAD_TWIPS = sys.argv[3] if len(sys.argv) > 3 else "60"

P1_TITLE = "基于STM32与freertos的综合测量平台"
P1_INTRO = "集成示波器、数字万用表、可调直流电源和信号发生器，支持波形实时显示及频率、幅度测量，频率测量误差极小，电压与电阻测量误差1%；支持使用DC-DC升压电路实现直流电压稳定输出；信号发生器输出正弦、方波等，频率档位覆盖50 Hz～80 kHz。"
P1_B = {
    "架构交互": "独立完成FreeRTOS移植与软件分层设计，结合邮箱、事件组及信号量，实现最新测量值传递、lcd屏幕按需局部刷新与DMAC传输同步，保障了多并发任务发生时各部分数据实时性。",
    "并发优化": "针对采集与显示共享缓冲区的读写冲突，设计双缓冲与状态机协同机制，管理波形数据的读写权限和切换时机，保证单帧绘制期间数据一致，避免新旧帧混用，并允许新帧准备与当前帧绘制并行。",
    "测量与调试": "基于内部参考电压估算VDDA，结合GPIO档位识别、分压与偏置补偿完成多量程换算，提升测量准确性；优化采样率与波表长度配置、定时参数计算及更新时序，修正低频输出偏差，实现频率切换及时生效。",
}
P2_TITLE = ("基于MSPM0与K230的移动目标瞄准系统", "边缘AI · Python · 机器视觉")
P2_INTRO = "面向循迹小车行驶中的激光自动瞄准，结合K230 KPU高速推理单元，实现AI目标检测与几何视觉，完成矩形靶标识别、靶心定位及瞄准偏差反馈。不同环境下目标识别率达98%；整机实测启动后2秒内完成瞄准并开启激光，打靶误差＜1.5cm，小车稳定行驶时误差＜2cm。"
P2_DUTY = "负责AI训练部署、视觉算法、灰度逻辑与人机交互。"
P2_BULLETS = [
    ("模型训练", "为解决各种环境对识别精度影响，自采多环境靶标图像，通过Make Sense标注并借助AI校验标注质量；在AI Cube完成目标检测模型训练与板端部署，实现不同环境下的矩形靶标准确识别。"),
    ("融合定位", "将AI检测框与几何四角统一到同帧原图坐标并匹配，优先通过四角对角线交点求心；几何失效但AI有效时切换至检测框中心，继续提供靶心位置反馈。"),
    ("稳健反馈", "结合Otsu阈值重估与面积、对边及角度约束过滤干扰，校验靶心有效性后经串口输出双轴偏差；双路均失效时发送无效状态，避免错误坐标参与团队云台瞄准。"),
]
P3_B = {
    "系统开发": "分层封装传感器驱动与采集逻辑，设计RTC周期采集与按键唤醒双事件机制，分别维护采样与显示期限，避免临时查看打乱上报节拍；支持无网关条件下现场查看数据，并通过有效性检查标识采集异常，保障不同情况下数据的有效观测。",
    "功耗优化": "结合Stop模式、代码系统优化、外设供电门控与休眠控制，抑制GPIO漏电并隔离断电外设信号，将整板待机电流控制在µA级。",
    "协议开发": "设计CRC校验、序号匹配及ACK超时有限重试机制，实现上报确认与传输异常处理；开发PC网关处理半包、粘包及坏帧，按节点与序号去重且对重传仍回ACK，完成数据解析及带时间的故障日志记录，支持采集异常追溯。",
}
HONOR_CERT = "英语四级（CET-4）；三好学生、优秀学生、优秀共青团员；优秀实验项目。"
SKILL_通信与协议 = "熟悉UART、I²C、SPI等常用通信协议，具备自定义帧协议设计经验，使用过通信、采集与定时控制类外设。"
SKILL_开发与调试 = "熟练使用Keil、STM32CubeMX、VS Code等开发工具，能使用CMake/GCC、Git完成工程构建与版本管理；结合原理图、数据手册及示波器、万用表等仪器定位软硬件问题。"
SKILL_AI = "熟练使用Codex、Claude Code、DeepSeek Harness、ZCode搭建工作流并实现快速产品设计与开发。"
CAMPUS = {
    "heading": "校园经历",
    "title": ("山东建筑大学校学生会科创部", "部长", "2023.09—2025.06"),
    "bullets": [
        ("科创组织", "统筹约50名成员，参与组织电赛、西门子杯、蓝桥杯及国产MCU产品等校级宣讲，负责人员分工、跨部门协调、宣传物料、会场布置与流程安排，保障活动按计划落地。"),
        ("现场保障", "参与组织文艺晚会、校园歌手大赛等200余人活动，设置双麦克风及主备音响保障方案；音频设备突发故障后按预案切换备用设备，恢复现场声音并保障活动继续进行。"),
    ],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
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


def labelled(paragraph, label, text, bullet=False):
    prefix = f"• {label}：" if bullet else f"{label}："
    replace_runs(paragraph, [(prefix, 0), (text, 1)])


def main():
    variant = sys.argv[1]                       # '00' | '01' | '10'
    out = Path(sys.argv[4])
    if out.exists():
        print(f'ERROR: 输出已存在：{out}'); return 2
    if sha256(BASE) != EXPECTED:
        print(f'ERROR: 基准哈希不符：{sha256(BASE)}'); return 2
    doc = Document(BASE)
    body = doc.element.body
    children = list(body)
    paras = doc.paragraphs

    def para(i):
        return Paragraph(children[i], doc)

    # 1) 荣誉：证书荣誉行更新，删除“项目实践”行
    labelled(para(5), "证书荣誉", HONOR_CERT)
    e6 = children[6]
    e6.getparent().remove(e6)

    # 1b) 项目一标题更新
    replace_runs(doc.tables[2].cell(0, 0).paragraphs[0], [(P1_TITLE, 0)])

    # 2) 项目一（综合测量平台）：简介与三条
    labelled(para(9), "项目简介", P1_INTRO)
    for idx, key in ((11, "架构交互"), (12, "并发优化"), (13, "测量与调试")):
        labelled(para(idx), key, P1_B[key], bullet=True)

    # 3) 项目二：换成瞄准系统（标题表＋简介＋职责＋三条）
    tbl = doc.tables[3]
    name, kw = P2_TITLE
    replace_runs(tbl.cell(0, 0).paragraphs[0], [(name, 0)])
    replace_runs(tbl.cell(0, 1).paragraphs[0], [(kw, 0)])
    labelled(para(15), "项目简介", P2_INTRO)
    labelled(para(16), "项目职责", P2_DUTY)
    for idx, (label, text) in zip((17, 18, 19), P2_BULLETS):
        labelled(para(idx), label, text, bullet=True)

    # 4) 项目三（LoRa）：标题换回 LoRa（基准第三槽是旧瞄准标题），三条更新
    replace_runs(doc.tables[4].cell(0, 0).paragraphs[0], [("低功耗LoRa环境监测节点", 0)])
    replace_runs(doc.tables[4].cell(0, 1).paragraphs[0], [("低功耗管理 · 无线通信 · 网关开发", 0)])
    for idx, key in ((23, "系统开发"), (24, "功耗优化"), (25, "协议开发")):
        labelled(para(idx), key, P3_B[key], bullet=True)

    # 5) 技能两条更新
    for idx, text in ((34, SKILL_通信与协议), (35, SKILL_开发与调试), (36, SKILL_AI)):
        p = para(idx)
        label = p.text.strip().split("：", 1)[0]
        labelled(p, label, text)

    # 6) 实习/校园组合
    if variant == "00":
        for i in (26, 27, 28, 29, 30):
            e = children[i]
            e.getparent().remove(e)
        print("组合00：实习与校园均不写")
    elif variant == "01":
        print("组合01：保留实习经历栏")
    else:
        replace_runs(para(26), [("校园经历", 0)])   # 栏目标题改文字
        tbl = doc.tables[5]                        # 实习机构标题表→校园
        cn, cr, cp = CAMPUS["title"]
        replace_runs(tbl.cell(0, 0).paragraphs[0], [(cn, 0), (f"｜{cr}", 1)])
        replace_runs(tbl.cell(0, 1).paragraphs[0], [(cp, 0)])
        labelled(para(28), CAMPUS["bullets"][0][0], CAMPUS["bullets"][0][1], bullet=True)
        labelled(para(29), CAMPUS["bullets"][1][0], CAMPUS["bullets"][1][1], bullet=True)
        e30 = children[30]
        e30.getparent().remove(e30)                # 原第三条删除
        print("组合10：校园长版（标题行＋两条），实习不写")

    # 7) 字号
    n = 0
    for run in body.iter(qn('w:r')):
        rPr = run.find(qn('w:rPr'))
        if rPr is None: continue
        for tag in ('w:sz', 'w:szCs'):
            e = rPr.find(qn(tag))
            if e is not None and e.get(qn('w:val')) in SIZE_MAP:
                e.set(qn('w:val'), SIZE_MAP[e.get(qn('w:val'))]); n += 1
    print(f"字号提升 {n} 处")

    # 8) 行距/段前
    heads = {"教育背景", "竞赛与荣誉", "项目经历", "实习经历", "校园经历", "专业技能"}
    m = k = 0
    for p in doc.paragraphs:
        pPr = p._p.find(qn('w:pPr'))
        if pPr is None: continue
        sp = pPr.find(qn('w:spacing'))
        if sp is None: continue
        if sp.get(qn('w:line')): sp.set(qn('w:line'), LINE_TWIPS); m += 1
        if p.text.strip() in heads and sp.get(qn('w:before')) not in (None, '0'):
            sp.set(qn('w:before'), HEAD_TWIPS); k += 1
    print(f"行距 {m} 处→{LINE_TWIPS}，段前 {k} 处→{HEAD_TWIPS}")

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
