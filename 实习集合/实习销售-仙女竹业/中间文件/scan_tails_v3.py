# -*- coding: utf-8 -*-
"""孤行扫描v3：逐行列出全部宽度<100pt的行＋下一行开头，人工判定是否为段落短尾行。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import fitz

pdf = r"D:\APP\project_practice\codex-project\实习集合\实习销售-仙女竹业\彭博裕-客户经理.pdf"
doc = fitz.open(pdf)
page = doc[0]
d = page.get_text("dict")
lines = []
for b in d["blocks"]:
    if b["type"] != 0:
        continue
    for ln in b["lines"]:
        t = "".join(sp["text"] for sp in ln["spans"]).strip()
        if t:
            lines.append((ln["bbox"][1], ln["bbox"][0], ln["bbox"][2] - ln["bbox"][0], t))
lines.sort()
print("== 宽度<100pt的行（y / x0 / 宽 / 文本 | 下一行）==")
for i, (y, x0, w, t) in enumerate(lines):
    if w < 100:
        nxt = lines[i + 1][3][:16] if i + 1 < len(lines) else "(页尾)"
        print(f"  y={y:6.1f} x0={x0:5.1f} w={w:5.1f}  {t[:24]!r:28s} | 下一行: {nxt!r}")
print("== 完 ==")
