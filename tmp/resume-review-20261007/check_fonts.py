# -*- coding: utf-8 -*-
# Step1 追查：7.6pt 内容归属 + 字体嵌入状态 + 疑似异常字的字体与渲染
import fitz
from pathlib import Path

PDF = Path(r"D:\APP\project_practice\codex-project\简历\简历修改版本\模板简历（随时跟新）\模板简历\彭博裕-嵌入式软件工程师-01.pdf")
OUT = Path(r"D:\APP\project_practice\codex-project\tmp\resume-review-20261007")
doc = fitz.open(PDF)
page = doc[0]
d = page.get_text("dict")

print("== 7.6pt spans ==")
for blk in d["blocks"]:
    if blk.get("type") != 0:
        continue
    for line in blk["lines"]:
        for span in line["spans"]:
            if round(span["size"], 1) == 7.6:
                print(f"  [{span['font']}] '{span['text']}' bbox={span['bbox']}")

print("== fonts used on page ==")
print(page.get_fonts())

print("== suspicious chars: font per span containing them ==")
targets = ["计量基础", "采集终端", "对比缩小", "故障范围"]
for blk in d["blocks"]:
    if blk.get("type") != 0:
        continue
    for line in blk["lines"]:
        for span in line["spans"]:
            t = span["text"]
            if any(x in t for x in targets):
                print(f"  [{span['font']} {round(span['size'],1)}pt] '{t}'")
