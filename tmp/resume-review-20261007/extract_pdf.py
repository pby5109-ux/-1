# -*- coding: utf-8 -*-
# dxp-grad-resume-builder 评审分支 Step1：读全原件（文字层 + 字号分布 + 版面渲染）
# 重建方法：D:\Anaconda\python.exe extract_pdf.py（依赖 PyMuPDF）
import fitz
from pathlib import Path

PDF = Path(r"D:\APP\project_practice\codex-project\简历\简历修改版本\模板简历（随时跟新）\模板简历\彭博裕-嵌入式软件工程师-01.pdf")
OUT = Path(r"D:\APP\project_practice\codex-project\tmp\resume-review-20261007")
OUT.mkdir(parents=True, exist_ok=True)

doc = fitz.open(PDF)
print("pages:", len(doc))
for pno, page in enumerate(doc):
    # 1) 文字层（保留 block/line 顺序，用于与视觉顺序比对）
    txt = page.get_text("text")
    (OUT / f"p{pno+1}_text.txt").write_text(txt, encoding="utf-8")

    # 2) 字号分布（按字符数加权）
    d = page.get_text("dict")
    sizes = {}
    for blk in d["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for span in line["spans"]:
                s = round(span["size"], 1)
                sizes[s] = sizes.get(s, 0) + len(span["text"])
    print(f"--- page {pno+1} font-size distribution (size: chars) ---")
    for s in sorted(sizes):
        print(f"  {s}pt : {sizes[s]} chars")

    # 3) 全页 170dpi
    page.get_pixmap(dpi=170).save(str(OUT / f"p{pno+1}_full_170.png"))

    # 4) 300dpi 分块（纵向四等分，页宽全幅）
    w, h = page.rect.width, page.rect.height
    for i in range(4):
        clip = fitz.Rect(0, h * i / 4, w, h * (i + 1) / 4)
        page.get_pixmap(dpi=300, clip=clip).save(str(OUT / f"p{pno+1}_seg{i+1}_300.png"))

# 实习经历区域高倍渲染（定位三处疑似缺字：y 约 700-820pt 区间）
page = doc[0]
words = page.get_text("words")
ys = [w0[1] for w0 in words]
print("word count:", len(words))
rects = page.search_for("通信排查")
for r in rects:
    print("通信排查 at:", r)
    clip = fitz.Rect(0, r.y0 - 90, page.rect.width, r.y1 + 90)
    page.get_pixmap(dpi=350, clip=clip).save(str(OUT / "internship_zoom_350.png"))
print("done ->", OUT)
