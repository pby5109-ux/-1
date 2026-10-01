# -*- coding: utf-8 -*-
"""大华股份-嵌入式软件工程师（华消）J24089 定制 v2。
基准仍为磁盘 -10.docx（内容较用户 08:40 PDF 旧，差异按 current-content.json 权威文本修正）：
1) LoRa 槽位简介/职责恢复为内容库 LoRa 文案（磁盘 docx 遗留瞄准文案）；
2) 瞄准简介去掉"并开启激光"（用户 09-28 08:40 -10.pdf 最新口径）；
3) 通信与协议加 TCP/UDP/HTTP（用户确认做过实验），与"自定义帧协议设计"合句保证单行；
4) 开发与调试加 IAR（用户确认使用过）。
融合定位一条保留磁盘 docx 正确内容（用户 PDF 中该条疑似粘贴覆盖成模型训练内容，不采用）。"""
import copy, hashlib, zipfile
from pathlib import Path
from docx import Document
from docx.text.paragraph import Paragraph

BASE = Path(r"D:\APP\project_practice\codex-project\简历\简历修改版本\模板简历（随时跟新）\模板简历\彭博裕-嵌入式软件工程师-10.docx")
EXPECTED = "E911EF38DCA4D0C6"
OUT = Path(r"D:\APP\project_practice\codex-project\简历\中间文件\大华股份-20260928\彭博裕-嵌入式软件工程师-10.docx")

LORA_INTRO = "基于STM32F103C8T6，完成集环境数据采集、周期无线上报与网关异常记录于一体的低功耗监测节点，实现整机休眠电流实测约54µA；按1100mAh电池容量及既定上报工况，预留裕量后估算续航约8个月。"
LORA_DUTY = "负责方案选型、软件开发与整板调试。"
AIM_INTRO = "面向循迹小车行驶中的激光自动瞄准，结合K230 KPU高速推理单元，实现AI目标检测与几何视觉，完成矩形靶标识别、靶心定位及瞄准偏差反馈。不同环境下目标识别率达98%；整机实测启动后2秒内完成瞄准，打靶误差＜1.5cm，小车稳定行驶时误差＜2cm。"
SKILL_通信与协议 = "熟悉UART、I²C、SPI、TCP/UDP、HTTP等常用通信协议与自定义帧协议设计，使用过通信、采集与定时控制类外设。"
SKILL_开发与调试 = "熟练使用Keil、IAR、STM32CubeMX、VS Code等开发工具，能使用CMake/GCC、Git完成工程构建与版本管理；结合原理图、数据手册及示波器、万用表等仪器定位软硬件问题。"
P3_功耗优化 = "结合Stop模式、代码优化、供电门控与休眠控制，抑制GPIO漏电并隔离断电外设信号，将整板待机电流控制在µA级。"


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


def labelled(paragraph, label, text, bullet=False):
    prefix = f"• {label}：" if bullet else f"{label}："
    replace_runs(paragraph, [(prefix, 0), (text, 1)])


def main():
    full = sha256(BASE)
    if not full.startswith(EXPECTED):
        print(f'ERROR: 基准哈希不符：{full[:16]}'); return 2
    doc = Document(BASE)

    done = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if t.startswith("项目简介：面向小车行驶过程中的激光自动瞄准"):
            labelled(p, "项目简介", LORA_INTRO); done.append("LoRa简介")
        elif t == "项目职责：负责视觉算法、灰度采集与OLED/按键交互。":
            labelled(p, "项目职责", LORA_DUTY); done.append("LoRa职责")
        elif t.startswith("项目简介：面向循迹小车行驶中的激光自动瞄准"):
            labelled(p, "项目简介", AIM_INTRO); done.append("瞄准简介")
        else:
            core = t[2:] if t.startswith("• ") else t
            label = core.split("：", 1)[0]
            if label == "通信与协议":
                labelled(p, label, SKILL_通信与协议); done.append("通信与协议")
            elif label == "开发与调试":
                labelled(p, label, SKILL_开发与调试); done.append("开发与调试")
            elif label == "功耗优化":
                labelled(p, label, P3_功耗优化, bullet=True); done.append("功耗优化缩句")
    need = ["LoRa简介", "LoRa职责", "瞄准简介", "通信与协议", "开发与调试", "功耗优化缩句"]
    if sorted(done) != sorted(need):
        print(f'ERROR: 补丁命中不全：{done}'); return 2
    print("已改：", "、".join(done))

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
