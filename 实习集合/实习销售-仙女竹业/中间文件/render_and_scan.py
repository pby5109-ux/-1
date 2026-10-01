# -*- coding: utf-8 -*-
"""渲染PNG + 孤行扫描v2：报告每个多行文本块的末行宽度，窄于阈值的列出（右侧对齐的日期/关键词属正常窄行，按文本特征豁免）。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import fitz

pdf = r"D:\APP\project_practice\codex-project\实习集合\实习销售-仙女竹业\彭博裕-客户经理.pdf"
png = r"D:\APP\project_practice\codex-project\实习销售-仙女竹业\中间文件\预览-销售简历-20260925.png"
doc = fitz.open(pdf)
page = doc[0]
pix = page.get_pixmap(dpi=150)
pix.save(png)
print("PNG:", png, pix.width, "x", pix.height)

d = page.get_text("dict")
print("== 各多行块末行（宽pt / 末行文本）==")
flags = []
for b in d["blocks"]:
    if b["type"] != 0 or len(b["lines"]) < 2:
        continue
    last = b["lines"][-1]
    t = "".join(sp["text"] for sp in last["spans"]).strip()
    w = last["bbox"][2] - last["bbox"][0]
    first = "".join(sp["text"] for sp in b["lines"][0]["spans"]).strip()[:18]
    mark = ""
    if w < 100:
        mark = "  ← 窄"
        flags.append((first, round(w, 1), t))
    print(f"  [{w:6.1f}] {t[:26]!r:30s} (块首: {first}){mark}")
print("== 窄末行汇总 ==")
for f in flags:
    print("  ", f)
if not flags:
    print("   无（全部末行 ≥100pt）")
