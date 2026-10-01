# -*- coding: utf-8 -*-
"""销售简历拼装脚本（预览版）。
基准：简历/简历修改版本/模板简历（随时跟新）/彭博裕-嵌入式软件工程师-含实习与校园.docx（09-18版，仅取其版式骨架，正文全部替换为销售版定稿候选）。
结构操作：实习块与校园块前移至项目经历之前；删除LoRa项目块；校园短段替换为两条加粗标签条目。
用法：python build_sales_resume.py <输出docx路径> <字号pt> <行距w:line> <段前twips>
只 word/document.xml 与基准不同，其余 ZIP 部件逐字节保留（沿用既定契约）。"""
import copy, hashlib, sys, zipfile
from pathlib import Path
from docx import Document
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

BASE = Path(r"D:\APP\project_practice\codex-project\简历\简历修改版本\模板简历（随时跟新）\旧版简历\9.26\彭博裕-嵌入式软件工程师-含实习与校园.docx")
W = qn

# ---------- 销售版定稿候选正文（来源：实习销售-仙女竹业/内容讨论与候选.md 2026-09-25冻结清单） ----------
P1 = {
    "title": "基于STM32的多功能综合测量平台",
    "kw": "多功能集成 · 统筹推进 · 指标交付",
    "intro": "将示波器、数字万用表、信号发生器与可调直流电源四类功能整合为一台多用途测量设备，独立推进从方案设计、开发调试到整板交付的全过程，测量误差控制在1 Hz/1%。",
    "duty": "负责整体方案与软硬件调试，推进各功能模块按节点交付。",
    "bullets": [
        ("方案统筹", "按“采集—处理—显示—输出”划分四个功能模块的职责与接口，制定各模块开发顺序与验证节点，按计划完成整板联调。"),
        ("问题攻坚", "围绕整机误差指标定位偏差来源，通过参考基准估算、量程档位识别与分压偏置补偿完成多量程换算修正，收敛到频率误差1 Hz、电压电阻误差1%。"),
        ("交付闭环", "完成四类功能的整板实测与问题修正，交付功能完整、指标可复现、可现场演示的成品。"),
    ],
}
P2 = {
    "title": None,  # 基于MSPM0与K230的移动目标瞄准系统（保持基准原题）
    "kw": "跨角色协作 · 需求对接 · 团队交付",
    "intro": "团队课题中负责AI训练部署与视觉定位方向，结合K230 KPU推理单元实现AI目标检测与几何视觉，与运动控制方向队友协作完成整机交付；整机实测启动2秒内瞄准、打靶误差＜1.5cm、稳定行驶误差＜2cm（团队指标）。",
    "duty": "负责视觉算法、灰度采集与跨模块对接。",
    "bullets": [
        ("需求拆解", "把“命中移动目标”的总体目标拆分为视觉识别与云台控制两段可执行需求，明确两端输入输出与验收口径，作为视觉与控制两端协作的统一基准。"),
        ("接口沟通", "与控制方向队友以串口协议约定数据格式与偏差语义，并跑通AI检测框与几何定位双路输出的融合；联调中按现象快速区分识别侧或执行侧问题，高效定位到人。"),
        ("团队交付", "在竞赛时间约束下与队友按节点集成联调，整机达成2秒内瞄准、＜1.5cm/＜2cm的实测指标。"),
    ],
}
INTERNSHIP = {
    "company": "湘潭市仙女竹业有限公司",
    "role": "销售实习生",
    "date": "2024.06—2024.10",
    "bullets": [
        ("销售业绩", "代表公司参加上海日用品展览会并担任柜台营销员，主动开发客源、接待洽谈客户100余名，围绕客户关注点组织产品介绍，促成多个万元级订单与数十万元级订单，获评公司“优秀销售实习生”。"),
        ("产品与工艺", "入职后系统学习公司产品线、品质标准与生产工艺，能结合材质、工艺与适用场景完整讲解产品价值，把产品优势转译为客户关注的价值点，以专业度支撑现场成交。"),
        ("市场推广", "随公司赴多地开展产品宣传与推介，面对不同地区、不同类型的客户群体调整讲解内容与方式，在一线销售与陌生客户沟通中持续积累实战经验。"),
    ],
}
CAMPUS = [
    ("组织统筹", "担任校学生会科创部部长，管理约50名成员，组织电赛、西门子杯、蓝桥杯及国产MCU厂商校级宣讲，负责人员分工、跨部门协调与流程安排，保障活动按计划落地。"),
    ("现场应急", "统筹文艺晚会、校园歌手大赛等200余人活动的设备保障，制定主备双方案；音频设备突发故障时按预案切换备用设备，快速恢复现场声音，保障活动继续进行。"),
]
SKILLS = [
    ("技术基础", "物联网工程专业背景，熟悉嵌入式系统、传感器与常用通信协议（UART、I²C、SPI），能阅读原理图与数据手册等技术资料，可独立完成设备调试与产品演示。"),
    ("工程素养", "结合示波器、万用表等仪器定位软硬件问题，习惯以实测数据支撑结论；能使用CMake/GCC、Git完成构建与版本管理。"),
    ("办公技能", "熟练使用WPS/Office完成文档撰写、数据整理与演示材料制作。"),
    ("AI工具", "熟练使用Codex、Claude Code、DeepSeek Harness、ZCode等工具搭建工作流，辅助资料整理与演示内容制作，快速完成产品设计与开发。"),
    ("资质", "机动车C1驾驶证，适应出差与驻外工作。"),
]
INTENT_OLD, INTENT_NEW = "嵌入式软件工程师", "客户经理"
# 项目简介/职责按出现顺序计数：#1=综合测量 #2=LoRa(将删除，不改) #3=K230
REWRITE = {
    "项目简介#1": ("项目简介", P1["intro"]),
    "项目职责#1": ("项目职责", P1["duty"]),
    "架构交互": ("方案统筹", P1["bullets"][0][1]),
    "并发优化": ("问题攻坚", P1["bullets"][1][1]),
    "测量与调试": ("交付闭环", P1["bullets"][2][1]),
    "项目简介#3": ("项目简介", P2["intro"]),
    "项目职责#3": ("项目职责", P2["duty"]),
    "目标筛选": ("需求拆解", P2["bullets"][0][1]),
    "中心定位": ("接口沟通", P2["bullets"][1][1]),
    "光照适配": ("团队交付", P2["bullets"][2][1]),
    "产品认知": ("销售业绩", INTERNSHIP["bullets"][0][1]),
    "开发板实践": ("产品与工艺", INTERNSHIP["bullets"][1][1]),
    "通信与排查": ("市场推广", INTERNSHIP["bullets"][2][1]),
    "比赛获奖": ("比赛获奖", "蓝桥杯省级三等奖；电子设计大赛校级一等奖。"),
    "编程基础": ("技术基础", SKILLS[0][1]),
    "内核与实时系统": ("工程素养", SKILLS[1][1]),
    "通信与协议": ("办公技能", SKILLS[2][1]),
    "开发与调试": ("AI工具", SKILLS[3][1]),
    "AI工具": ("资质", SKILLS[4][1]),
}
HEADINGS = {"教育背景", "竞赛与荣誉", "项目经历", "实习经历", "校园经历", "专业技能"}


def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest().upper()


def all_paragraphs(doc):
    for p_el in doc.element.body.iter(W("w:p")):
        yield Paragraph(p_el, doc)


def replace_runs(paragraph, segments):
    old = list(paragraph.runs)
    styles = [copy.deepcopy(r._r.rPr) if r._r.rPr is not None else None for r in old]
    for r in old:
        paragraph._p.remove(r._r)
    for text, idx in segments:
        run = paragraph.add_run(text)
        st = styles[min(idx, len(styles) - 1)]
        if st is not None:
            run._r.insert(0, copy.deepcopy(st))


def para_text(el):
    return "".join(t.text or "" for t in el.iter(W("w:t")))


def main():
    out = Path(sys.argv[1])
    font_map = {
        "9": {"16": "18", "18": "19", "19": "20", "20": "21"},
        "8.5": {"16": "17", "18": "18", "19": "20", "20": "21"},
        "8": {},
    }
    size_key = sys.argv[2]
    line = sys.argv[3]
    head = sys.argv[4]
    assert size_key in font_map, "字号仅支持 9/8.5/8"
    print("基准SHA256:", sha(BASE))

    doc = Document(BASE)
    applied = 0
    # 1) 求职意向
    for p in all_paragraphs(doc):
        for r in p.runs:
            if INTENT_OLD in r.text:
                r.text = r.text.replace(INTENT_OLD, INTENT_NEW)
                applied += 1
    # 2) 正文条目与标题行
    seen = {}
    for p in all_paragraphs(doc):
        t = p.text
        if "：" not in t:
            continue
        bullet = t.lstrip().startswith("•")
        body = t.lstrip().lstrip("•").strip()
        label = body.split("：", 1)[0].strip()
        seen[label] = seen.get(label, 0) + 1
        key = label if label not in ("项目简介", "项目职责") else "%s#%d" % (label, seen[label])
        if key not in REWRITE:
            continue
        new_label, new_body = REWRITE[key]
        replace_runs(p, [(("• %s：" % new_label) if bullet else ("%s：" % new_label), 0), (new_body, 1)])
        applied += 1
    # 3) 标题行单元格
    for tbl in doc.element.body.iter(W("w:tbl")):
        txt = para_text(tbl)
        if "综合测量平台" in txt and "FreeRTOS" in txt:
            runs = [r for r in tbl.iter(W("w:r")) if para_text(r)]
            runs[0].findall(W("w:t"))[0].text = P1["title"]
            runs[1].findall(W("w:t"))[0].text = P1["kw"]
            applied += 1
        elif "移动目标瞄准系统" in txt and "几何定位" in txt:
            runs = [r for r in tbl.iter(W("w:r")) if para_text(r)]
            runs[1].findall(W("w:t"))[0].text = P2["kw"]
            applied += 1
        elif "威思顿" in txt:
            runs = [r for r in tbl.iter(W("w:r")) if para_text(r)]
            runs[0].findall(W("w:t"))[0].text = INTERNSHIP["company"]
            runs[1].findall(W("w:t"))[0].text = "｜" + INTERNSHIP["role"]
            runs[2].findall(W("w:t"))[0].text = INTERNSHIP["date"]
            applied += 1
    # 4) 校园短段 → 两条加粗标签条目（复制实习首条的两run结构）
    bullet_tpl = None
    for p in all_paragraphs(doc):
        if p.text.lstrip().startswith("• 销售业绩："):
            bullet_tpl = copy.deepcopy(p._p)
            break
    assert bullet_tpl is not None, "未找到实习首条作为校园条目模板"
    for p in list(all_paragraphs(doc)):
        if p.text.startswith("担任校学生会科创部部长"):
            for label, body in CAMPUS:
                el = copy.deepcopy(bullet_tpl)
                runs = [r for r in el.iter(W("w:r")) if para_text(r)]
                runs[0].findall(W("w:t"))[0].text = "• %s：" % label
                runs[1].findall(W("w:t"))[0].text = body
                p._p.addprevious(el)
            p._p.getparent().remove(p._p)
            applied += 1
            break
    # 5) 结构：删除LoRa块；实习块+校园块前移到项目经历之前
    body = doc.element.body
    def find_heading(name):
        for p in all_paragraphs(doc):
            if p.text.strip() == name and p._p.find(qn("w:pPr")) is not None:
                return p._p
        raise AssertionError("未找到标题 " + name)
    def tbl_marker(m):
        for tbl in body.iter(W("w:tbl")):
            if m in para_text(tbl):
                return tbl
        raise AssertionError("未找到表格 " + m)
    lora_tbl = tbl_marker("低功耗LoRa")
    k230_tbl = tbl_marker("移动目标瞄准系统")
    cur = lora_tbl
    doomed = [cur]
    cur = cur.getnext()
    while cur is not None and cur is not k230_tbl:
        doomed.append(cur)
        cur = cur.getnext()
    for el in doomed:
        body.remove(el)
    h_proj = find_heading("项目经历")
    h_int = find_heading("实习经历")
    h_campus = find_heading("校园经历")
    h_skill = find_heading("专业技能")
    children = list(body)
    def block_range(a, b):
        return children[children.index(a):children.index(b)]
    moving = block_range(h_int, h_campus) + block_range(h_campus, h_skill)
    for el in moving:
        h_proj.addprevious(el)
    # 6) 字号 / 行距 / 段前
    fmap = font_map[size_key]
    n = 0
    for rPr in doc.element.body.iter(W("w:rPr")):
        for tag in ("w:sz", "w:szCs"):
            e = rPr.find(W(tag))
            if e is not None and e.get(W("w:val")) in fmap:
                e.set(W("w:val"), fmap[e.get(W("w:val"))])
                n += 1
    m = k = 0
    for p in all_paragraphs(doc):
        pPr = p._p.find(qn("w:pPr"))
        if pPr is None:
            continue
        sp = pPr.find(qn("w:spacing"))
        if sp is None:
            continue
        if sp.get(qn("w:line")):
            sp.set(qn("w:line"), line)
            m += 1
        if p.text.strip() in HEADINGS and sp.get(qn("w:before")) not in (None, "0"):
            sp.set(qn("w:before"), head)
            k += 1
    # 7) 保存：只替换 word/document.xml
    staged = out.with_name(out.stem + ".staged.docx")
    doc.save(staged)
    with zipfile.ZipFile(staged) as e:
        doc_xml = e.read("word/document.xml")
    staged.unlink()
    with zipfile.ZipFile(BASE) as z, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as o:
        for item in z.infolist():
            o.writestr(item, doc_xml if item.filename == "word/document.xml" else z.read(item.filename))
    print("字号=%d处 行距=%s(%d处) 段前=%s(%d处) 内容替换=%d处" % (n, line, m, head, k, applied))
    print("输出:", out, "SHA256:", sha(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
