#!/usr/bin/env python3
"""按 2026-09-17 确认的新结构，从不可变的嵌入式母版生成简历 DOCX。

与 jd-resume-tailor/scripts/build_resume.py 的旧管线不同：新结构为
5 条技能、3 个项目（各含"项目简介／项目职责"行＋3 条描述）、无企业实践、
校园经历一句话、竞赛与荣誉 3 行、无自我评价。母版哈希不符时停止。
"""

from __future__ import annotations

import copy
import hashlib
import sys
import zipfile
from pathlib import Path

from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.text.paragraph import Paragraph

MASTER = Path(
    r"D:\APP\project_practice\codex-project\简历\jd-resume-tailor\assets\embedded-master-20260904.docx"
)
EXPECTED_HASH = "FD387ED647C59727CF0E6B99B0839377FF8015C85592A4AD587013D394A3433B"

PHOTO_SOURCE = Path("C:/Users/彭/OneDrive/Pictures/Camera Roll/exec-3b85f6e1-966f-4a47-98d3-711d8c31d691.png")
PHOTO_TARGET = "word/media/image1.jpeg"
PHOTO_POS_EMU = (6297930, 255270)   # 相对页面左上角：x=495.9pt, y=20.1pt
PHOTO_WIDTH_EMU = 720000            # 宽 56.7pt，高按新图比例换算
PROJECT_TITLE_WIDTHS = [6500, 3938]      # 项目标题：左名称 / 右关键词
CAMPUS_TITLE_WIDTHS = [7179, 3259]       # 校园经历：左单位职务 / 右日期
PAGE_TOP_MARGIN_TWIPS = 280          # 上页边距 14pt（母版 0.28in≈20.2pt）
CONTACT_SPACE_BEFORE_TWIPS = 200     # 姓名与联系方式之间加 10pt 间距


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def replace_runs(paragraph: Paragraph, segments) -> None:
    """用 (文本, 样式索引) 段替换段落内容，样式索引指向原段落已有 run 的格式。"""
    old_runs = list(paragraph.runs)
    if not old_runs:
        raise ValueError("模板段落没有可继承格式的 run")
    styles = [copy.deepcopy(run._r.rPr) if run._r.rPr is not None else None for run in old_runs]
    for run in old_runs:
        paragraph._p.remove(run._r)
    for text, style_index in segments:
        new_run = paragraph.add_run(text)
        style = styles[min(style_index, len(styles) - 1)]
        if style is not None:
            new_run._r.insert(0, copy.deepcopy(style))


def set_font_size(paragraph: Paragraph, half_points: str) -> None:
    """强制设定段落内所有 run 的字号（半磅）。"""
    for run in paragraph.runs:
        rPr = run._r.get_or_add_rPr()
        for tag in ("w:sz", "w:szCs"):
            size = rPr.find(qn(tag))
            if size is None:
                size = rPr.makeelement(qn(tag), {})
                rPr.append(size)
            size.set(qn("w:val"), half_points)


def remap_body_font(document, mapping: dict[str, str]) -> int:
    """按半磅映射统一缩放正文字号，用于填满一页；姓名与栏目标题不在映射内。"""
    changed = 0
    for run in document.element.body.iter(qn("w:r")):
        rPr = run.find(qn("w:rPr"))
        if rPr is None:
            continue
        for tag in ("w:sz", "w:szCs"):
            size = rPr.find(qn(tag))
            if size is None:
                continue
            current = size.get(qn("w:val"))
            if current in mapping:
                size.set(qn("w:val"), mapping[current])
                changed += 1
    return changed


def thicken_heading_rules(document, half_points: str = "12") -> int:
    """加粗栏目标题下的蓝色分隔线（w:pBdr/w:bottom 的 sz 为 1/8 磅）。"""
    headings = {"教育背景", "竞赛与荣誉", "项目经历", "校园经历", "专业技能"}
    changed = 0
    for paragraph in document.paragraphs:
        if paragraph.text.strip() not in headings:
            continue
        pPr = paragraph._p.find(qn("w:pPr"))
        if pPr is None:
            continue
        pBdr = pPr.find(qn("w:pBdr"))
        if pBdr is None:
            continue
        bottom = pBdr.find(qn("w:bottom"))
        if bottom is not None:
            bottom.set(qn("w:sz"), half_points)
            changed += 1
    return changed


def align_table_text_left(document, table_indexes) -> int:
    """表格改左对齐并归零左边距留白，消除标题相对正文约1.7pt的居中偏移。"""
    changed = 0
    for index in table_indexes:
        tblPr = document.tables[index]._tbl.find(qn("w:tblPr"))
        if tblPr is None:
            continue
        cell_mar = tblPr.find(qn("w:tblCellMar"))
        if cell_mar is not None:
            left = cell_mar.find(qn("w:left"))
            if left is not None:
                left.set(qn("w:w"), "0")
                changed += 1
        jc = tblPr.find(qn("w:jc"))
        if jc is not None:
            jc.set(qn("w:val"), "left")
            changed += 1
    return changed


def set_line_spacing(document, line_twips: str = "230") -> int:
    """收紧正文行距（1.008→0.975倍），为恢复的校园经历条目腾出版面。"""
    changed = 0
    for paragraph in document.paragraphs:
        if not paragraph.text.strip():
            continue
        pPr = paragraph._p.find(qn("w:pPr"))
        if pPr is None:
            continue
        spacing = pPr.find(qn("w:spacing"))
        if spacing is not None and spacing.get(qn("w:line")):
            spacing.set(qn("w:line"), line_twips)
            changed += 1
    return changed


def drop_header_rule(document) -> int:
    """删除页首单元格底部的蓝色分隔线（教育背景上方那条）。"""
    removed = 0
    for cell in document.tables[0].rows[0].cells:
        tcPr = cell._tc.find(qn("w:tcPr"))
        if tcPr is None:
            continue
        borders = tcPr.find(qn("w:tcBorders"))
        if borders is None:
            continue
        bottom = borders.find(qn("w:bottom"))
        if bottom is not None:
            borders.remove(bottom)
            removed += 1
    return removed


def float_photo(document, cx_emu: int, cy_emu: int) -> int:
    """证件照改为浮动锚定，不再参与表格行高计算，页首因此可以整体上移。"""
    WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
    A = "http://schemas.openxmlformats.org/drawingml/2006/main"
    inline = next((e for e in document.element.body.iter() if e.tag == "{%s}inline" % WP), None)
    if inline is None:
        return 0
    x_emu, y_emu = PHOTO_POS_EMU
    anchor = parse_xml(
        '<wp:anchor %s distT="0" distB="0" distL="0" distR="0" simplePos="0" '
        'relativeHeight="251658240" behindDoc="0" locked="0" layoutInCell="1" allowOverlap="1">'
        '<wp:simplePos x="0" y="0"/>'
        '<wp:positionH relativeFrom="page"><wp:posOffset>%d</wp:posOffset></wp:positionH>'
        '<wp:positionV relativeFrom="page"><wp:posOffset>%d</wp:posOffset></wp:positionV>'
        '<wp:extent cx="%d" cy="%d"/>'
        '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:wrapNone/>'
        "</wp:anchor>" % (nsdecls("wp", "a", "r"), x_emu, y_emu, cx_emu, cy_emu)
    )
    for tag, ns in (("docPr", WP), ("cNvGraphicFramePr", WP), ("graphic", A)):
        child = inline.find("{%s}%s" % (ns, tag))
        if child is not None:
            anchor.append(copy.deepcopy(child))
    inline.getparent().replace(inline, anchor)
    return 1


def set_project_keywords(document, indexes, widths) -> int:
    """项目标题行：左侧单元格放名称，右侧单元格放技术关键词并右对齐到行尾。"""
    changed = 0
    for index in indexes:
        table = document.tables[index]
        for cell, width in zip(table.rows[0].cells, widths):
            tcPr = cell._tc.find(qn("w:tcPr"))
            tcW = tcPr.find(qn("w:tcW")) if tcPr is not None else None
            if tcW is not None:
                tcW.set(qn("w:w"), str(width))
                tcW.set(qn("w:type"), "dxa")
                changed += 1
    return changed


def replace_photo(docx_path: Path, source: Path, target: str = PHOTO_TARGET) -> bool:
    """用外部照片替换包内图片，保持文件名与格式，不改动关系与内容类型。"""
    import io
    import zipfile as _zip

    from PIL import Image

    image = Image.open(source).convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=92)
    payload = buffer.getvalue()
    temp = docx_path.with_name(docx_path.stem + ".photo.docx")
    with _zip.ZipFile(docx_path) as zin, _zip.ZipFile(temp, "w", _zip.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = payload if item.filename == target else zin.read(item.filename)
            zout.writestr(item, data)
    temp.replace(docx_path)
    return True


def darken_keywords(paragraph, color: str = "202733", half_points: str = "18") -> int:
    """把项目技术关键词的灰色小字改为与项目名称同色的加粗字。"""
    changed = 0
    for run in paragraph.runs:
        rPr = run._r.get_or_add_rPr()
        for tag, value in (("w:color", color), ("w:sz", half_points), ("w:szCs", half_points)):
            element = rPr.find(qn(tag))
            if element is None:
                element = rPr.makeelement(qn(tag), {})
                rPr.append(element)
            element.set(qn("w:val"), value)
            changed += 1
    return changed


def set_paragraph_space_before(paragraph, twips: int) -> int:
    """调整段落段前距；用于拉开姓名与联系方式之间的间距。"""
    pPr = paragraph._p.get_or_add_pPr()
    spacing = pPr.find(qn("w:spacing"))
    if spacing is None:
        spacing = pPr.makeelement(qn("w:spacing"), {})
        pPr.append(spacing)
    spacing.set(qn("w:before"), str(twips))
    return 1


def resize_inline_photo(document, width_emu: int, height_emu: int) -> int:
    """按新照片比例缩放内嵌证件照，缩小页首行高，使教育背景栏整体上移。"""
    WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
    A = "http://schemas.openxmlformats.org/drawingml/2006/main"
    inline = next((e for e in document.element.body.iter() if e.tag == "{%s}inline" % WP), None)
    if inline is None:
        return 0
    changed = 0
    extent = inline.find("{%s}extent" % WP)
    if extent is not None:
        extent.set("cx", str(width_emu))
        extent.set("cy", str(height_emu))
        changed += 1
    for xfrm in inline.iter("{%s}xfrm" % A):
        ext = xfrm.find("{%s}ext" % A)
        if ext is not None:
            ext.set("cx", str(width_emu))
            ext.set("cy", str(height_emu))
            changed += 1
    return changed


def set_top_margin(document, twips: int) -> int:
    """收紧上页边距，为页首上移留出空间。"""
    from docx.shared import Twips

    for section in document.sections:
        section.top_margin = Twips(twips)
        return 1
    return 0


def normalize_table_widths(document, spec: dict) -> int:
    """统一表格的 grid 与单元格宽度；母版各表 tcW 与 grid 不一致会让表内文字偏移约1.7pt。"""
    changed = 0
    for index, widths in spec.items():
        tbl = document.tables[index]._tbl
        grid = tbl.find(qn("w:tblGrid"))
        if grid is not None:
            for col, width in zip(grid.findall(qn("w:gridCol")), widths):
                col.set(qn("w:w"), str(width))
                changed += 1
        for row in tbl.findall(qn("w:tr")):
            for cell, width in zip(row.findall(qn("w:tc")), widths):
                tcPr = cell.find(qn("w:tcPr"))
                if tcPr is None:
                    continue
                tcW = tcPr.find(qn("w:tcW"))
                if tcW is not None:
                    tcW.set(qn("w:w"), str(width))
                    tcW.set(qn("w:type"), "dxa")
                    changed += 1
    return changed


def set_heading_spacing(document, default_twips: str = "150", overrides: dict | None = None) -> int:
    """调整栏目标题段前距：默认压到页面底部，个别栏目可单独指定（教育背景需要上移）。"""
    headings = {"教育背景", "竞赛与荣誉", "项目经历", "校园经历", "专业技能"}
    overrides = overrides or {}
    changed = 0
    for paragraph in document.paragraphs:
        title = paragraph.text.strip()
        if title not in headings:
            continue
        pPr = paragraph._p.find(qn("w:pPr"))
        if pPr is None:
            continue
        spacing = pPr.find(qn("w:spacing"))
        if spacing is not None:
            spacing.set(qn("w:before"), overrides.get(title, default_twips))
            changed += 1
    return changed


def labelled(paragraph: Paragraph, label: str, text: str, bullet: bool = False) -> None:
    prefix = f"• {label}：" if bullet else f"{label}："
    replace_runs(paragraph, [(prefix, 0), (text, 1)])


EDU = ["2023.09—2027.06", "山东建筑大学", "物联网工程｜本科", "专业综合测评排名前10%"]

HONORS = [
    ("比赛获奖", "全国大学生电子设计竞赛省级二等奖；蓝桥杯省级三等奖。"),
    ("证书荣誉", "英语四级（CET-4）；三好学生、优秀学生（个人）、优秀共青团员。"),
    ("项目实践", "负责组织开放实验项目，并验收优秀。"),
]

PROJECTS = [
    {
        "name": "基于STM32F103RCT6的综合测量平台",
        "keywords": "FreeRTOS · 实时采集 · 事件驱动",
        "intro": "集成示波器、数字万用表、可调直流电源和信号发生器，支持波形实时显示及频率、幅度测量，频率测量误差1 Hz，电压与电阻测量误差1%；支持直流电压稳定输出，信号发生器输出波形与频率可调。",
        "duty": "硬件电路设计、软件架构设计与系统开发调试。",
        "bullets": [
            ("架构交互", "独立完成FreeRTOS移植与软件分层设计，结合邮箱、事件组及信号量，实现最新测量值传递、屏幕按需局部刷新与DMA传输同步。"),
            ("并发优化", "针对采集与显示共享缓冲区的读写冲突，设计双缓冲与状态机协同机制，管理波形数据的读写权限和切换时机，保证单帧绘制期间数据一致，避免新旧帧混用。"),
            ("测量与调试", "采用内部参考电压校准及分压、偏置补偿，提升测量准确性；优化采样率与波表长度配置、定时参数计算及更新时序，修正低频输出偏差，实现频率切换及时生效。"),
        ],
    },
    {
        "name": "低功耗LoRa环境监测节点",
        "keywords": "低功耗管理 · 无线通信 · 网关开发",
        "intro": "基于STM32F103C8T6，完成集环境数据采集、周期无线上报与网关异常记录于一体的低功耗监测节点，实现整机休眠电流实测约54µA；按1100mAh电池容量及既定上报工况，预留裕量后估算续航约8个月。",
        "duty": "负责方案选型、软件开发与整板调试。",
        "bullets": [
            ("系统开发", "分层封装传感器驱动与采集逻辑，设计RTC周期采集与按键唤醒双事件机制，支持无网关条件下现场查看数据，并通过有效性检查标识采集异常。"),
            ("功耗优化", "结合Stop模式、外设供电门控与休眠控制，抑制GPIO漏电并隔离断电外设信号，将整板待机电流控制在µA级。"),
            ("协议开发", "设计CRC校验、序号匹配及ACK超时有限重试机制，实现上报确认与传输异常处理；开发PC网关完成数据解析及带时间的故障日志记录，支持采集异常追溯。"),
        ],
    },
    {
        "name": "基于MSPM0与K230的移动目标瞄准系统",
        "keywords": "机器视觉 · Python · 几何定位",
        "intro": "面向小车行驶过程中的激光自动瞄准，采用灰度阈值分割与矩形检测，结合几何约束筛选靶标、解算靶心并输出瞄准偏差。实现启动后2秒内完成瞄准并开启激光，打靶误差＜1.5cm；小车稳定行驶时误差＜2cm。",
        "duty": "负责视觉算法、灰度采集与OLED/按键交互。",
        "bullets": [
            ("目标筛选", "在矩形检测基础上，融合面积、对边长度差及平行垂直约束校验候选靶框，并按面积优先逐一筛选，避免单一最大框选择造成目标遗漏。"),
            ("中心定位", "利用靶框四角的对角线交点定位靶心，结合交点有效性与坐标边界检查排除异常结果；计算靶心相对画面中心的水平、垂直偏差，经串口输出，为云台调整瞄准方向提供依据。"),
            ("光照适配", "基于Otsu自动估计灰度阈值，通过按键触发重估、帧间保持阈值，实现不同光环境下的阈值校准；对无灰度对比的画面跳过识别并重试，避免无效画面参与阈值估计。"),
        ],
    },
]

CAMPUS_TITLE = ("山东建筑大学校学生会科创部", "部长", "2023.09—2025.06")

CAMPUS_BULLETS = [
    ("科创组织", "统筹约50名成员，参与组织电赛、西门子杯、蓝桥杯及国产MCU产品等校级宣讲，负责人员分工、跨部门协调、宣传物料、会场布置与流程安排，保障活动按计划落地。"),
    ("现场保障", "参与组织文艺晚会、校园歌手大赛等200余人活动，设置双麦克风及主备音响保障方案；音频设备突发故障后按预案切换备用设备，恢复现场声音并保障活动继续进行。"),
]

SKILLS = [
    ("编程基础", "熟悉C语言与Python，掌握常用数据结构，能完成嵌入式模块的代码阅读、改写与调试。"),
    ("内核与实时系统", "熟悉ARM Cortex-M3/M4内核与FreeRTOS实时操作系统，完成过FreeRTOS移植与项目配置；具有任务调度、内存管理及多任务并发的实践经验，能够处理中断服务与任务间的数据传递和同步。"),
    ("通信与协议", "熟悉UART、I²C、SPI等常用通信协议，具备自定义帧协议设计经验，实现过帧格式定义、CRC校验、序号匹配与ACK重传；使用过通信、采集与定时控制类外设。"),
    ("开发与调试", "熟练使用Keil、STM32CubeMX、VS Code等开发工具，能使用CMake/GCC、OpenOCD、Git完成工程构建、下载与版本管理；结合原理图、数据手册及示波器、万用表等仪器定位软硬件问题。"),
    ("AI工具", "熟练使用Codex、Claude Code、DeepSeek Harness、ZCode辅助代码阅读、调试与文档整理。"),
]


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("彭博裕-嵌入式软件工程师-简历-20260917.docx")
    if output.exists():
        print(f"ERROR: 输出已存在，不覆盖：{output}", file=sys.stderr)
        return 2
    if sha256(MASTER) != EXPECTED_HASH:
        print("ERROR: 母版哈希不符，停止生成。", file=sys.stderr)
        return 2

    doc = Document(MASTER)
    paragraphs = doc.paragraphs       # P00..P26
    tables = doc.tables               # T0..T6
    body = doc.element.body
    sect_pr = body.find(qn("w:sectPr"))

    P_EDU_HEAD, P_SKILL_HEAD, P_PROJ_HEAD = 0, 1, 5
    P_SKILL = [2, 3, 4]
    P_BULLET_IDX = [6, 7, 8, 9, 10, 11, 12, 13]
    P_CAMPUS_HEAD = 17
    P_HONOR_HEAD = 20
    P_HONORS = [21, 22, 23]

    # 新段落：以同类母版段落为样式模板
    intro_duty = [(copy.deepcopy(paragraphs[P_SKILL[0]]._p), copy.deepcopy(paragraphs[P_SKILL[0]]._p)) for _ in PROJECTS]
    extra_bullet = copy.deepcopy(paragraphs[P_BULLET_IDX[0]]._p)
    campus_bullets = [copy.deepcopy(paragraphs[P_BULLET_IDX[0]]._p) for _ in CAMPUS_BULLETS]
    campus_table = copy.deepcopy(tables[2]._tbl)  # 与项目标题行同构：左名称＋右日期
    extra_skills = [copy.deepcopy(paragraphs[P_SKILL[0]]._p) for _ in range(2)]

    # 目标顺序
    order = [tables[0]._tbl, paragraphs[P_EDU_HEAD]._p, tables[1]._tbl]
    order += [paragraphs[P_HONOR_HEAD]._p] + [paragraphs[i]._p for i in P_HONORS]
    order += [paragraphs[P_PROJ_HEAD]._p]
    project_bullets = [
        [paragraphs[i]._p for i in P_BULLET_IDX[0:3]],
        [paragraphs[i]._p for i in P_BULLET_IDX[3:6]],
        [paragraphs[i]._p for i in P_BULLET_IDX[6:8]] + [extra_bullet],
    ]
    for index, project in enumerate(PROJECTS):
        order.append(tables[2 + index]._tbl)
        order.append(intro_duty[index][0])
        order.append(intro_duty[index][1])
        order += project_bullets[index]
    order += [paragraphs[P_CAMPUS_HEAD]._p, campus_table] + campus_bullets
    order += [paragraphs[P_SKILL_HEAD]._p] + [paragraphs[i]._p for i in P_SKILL] + extra_skills

    # 删除不在目标顺序中的元素，再按序重排
    keep = {id(element) for element in order} | {id(sect_pr)}
    for child in list(body):
        if id(child) not in keep:
            body.remove(child)
    body.remove(sect_pr)
    for element in order:
        body.append(element)
    body.append(sect_pr)

    # 写入内容
    header_cell = tables[0].cell(0, 0)
    replace_runs(header_cell.paragraphs[0], [("彭博裕", 0), ("   求职意向：嵌入式软件工程师", 1)])
    replace_runs(header_cell.paragraphs[1], [("电话：17668025109   邮箱：pbyuqianrushi@163.com   2027届", 0)])
    set_font_size(header_cell.paragraphs[1], "19")  # 联系方式由8pt提到9.5pt，与求职意向同级
    set_paragraph_space_before(header_cell.paragraphs[1], CONTACT_SPACE_BEFORE_TWIPS)
    tags_paragraph = header_cell.paragraphs[2]._p
    tags_paragraph.getparent().remove(tags_paragraph)

    for index, text in enumerate(EDU):
        replace_runs(tables[1].cell(0, index).paragraphs[0], [(text, 0)])

    replace_runs(paragraphs[P_HONOR_HEAD], [("竞赛与荣誉", 0)])

    for index, (label, text) in enumerate(HONORS):
        labelled(paragraphs[P_HONORS[index]], label, text)

    for index, project in enumerate(PROJECTS):
        table = tables[2 + index]
        replace_runs(table.cell(0, 0).paragraphs[0], [(project["name"], 0)])
        keyword_paragraph = table.cell(0, 1).paragraphs[0]
        replace_runs(keyword_paragraph, [(project["keywords"], 0)])
        darken_keywords(keyword_paragraph)
        labelled(Paragraph(intro_duty[index][0], doc), "项目简介", project["intro"])
        labelled(Paragraph(intro_duty[index][1], doc), "项目职责", project["duty"])

    bullet_slots = [paragraphs[i] for i in P_BULLET_IDX] + [Paragraph(extra_bullet, doc)]
    flat_bullets = [bullet for project in PROJECTS for bullet in project["bullets"]]
    for (label, text), slot in zip(flat_bullets, bullet_slots):
        labelled(slot, label, text, bullet=True)

    campus_name, campus_role, campus_period = CAMPUS_TITLE
    campus_title_table = doc.tables[5]
    replace_runs(
        campus_title_table.cell(0, 0).paragraphs[0],
        [(campus_name, 0), (f"｜{campus_role}", 1)],
    )
    replace_runs(campus_title_table.cell(0, 1).paragraphs[0], [(campus_period, 0)])
    for (label, text), element in zip(CAMPUS_BULLETS, campus_bullets):
        labelled(Paragraph(element, doc), label, text, bullet=True)

    skill_slots = [paragraphs[i] for i in P_SKILL] + [Paragraph(element, doc) for element in extra_skills]
    for (label, text), slot in zip(SKILLS, skill_slots):
        labelled(slot, label, text)

    print("删除页首蓝色横线：", drop_header_rule(doc), "处")
    print("项目标题右列放关键词：", set_project_keywords(doc, (2, 3, 4), PROJECT_TITLE_WIDTHS), "处")
    print("加粗栏目标题分隔线：", thicken_heading_rules(doc), "处")
    print("表格左对齐与留白归零：", align_table_text_left(doc, (1, 2, 3, 4, 5)), "处")
    print(
        "表格列宽统一：",
        normalize_table_widths(
            doc,
            {
                1: [2609] * 4,
                2: list(PROJECT_TITLE_WIDTHS),
                3: list(PROJECT_TITLE_WIDTHS),
                4: list(PROJECT_TITLE_WIDTHS),
                5: list(CAMPUS_TITLE_WIDTHS),
            },
        ),
        "处",
    )
    print("栏目标题间距：", set_heading_spacing(doc, "160", {"教育背景": "0"}), "处")
    print("正文行距收紧：", set_line_spacing(doc, "230"), "处")
    bumped = remap_body_font(doc, {"15": "16", "16": "16"})
    print(f"正文字号统一为8pt：{bumped} 处")

    from PIL import Image

    with Image.open(PHOTO_SOURCE) as photo:
        width, height = photo.size
    cy_emu = int(round(PHOTO_WIDTH_EMU * height / width))
    print("上页边距收紧：", set_top_margin(doc, PAGE_TOP_MARGIN_TWIPS), "处")
    print("证件照缩放：", resize_inline_photo(doc, PHOTO_WIDTH_EMU, cy_emu), "处",
          f"（{PHOTO_WIDTH_EMU / 12700:.1f} x {cy_emu / 12700:.1f} pt）")

    doc.core_properties.title = "彭博裕 - 嵌入式软件工程师 - 通用版 20260917"
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)

    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
    if bad is not None:
        print(f"ERROR: DOCX 损坏成员：{bad}", file=sys.stderr)
        return 2
    replace_photo(output, PHOTO_SOURCE)
    with zipfile.ZipFile(output) as archive:
        hero = archive.read(PHOTO_TARGET)
    print(f"证件照已替换：{len(hero)} 字节")
    print(f"OK: 已生成 {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
