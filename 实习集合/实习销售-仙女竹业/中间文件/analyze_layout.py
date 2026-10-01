# -*- coding: utf-8 -*-
"""测量 -10.pdf 的版式架构：页面尺寸、字体/字号/颜色清单、分节顺序、分隔线、照片位置。
输出人类可读摘要；本文件与输出 JSON 属可重建的中间产物，来源与重建方法见本目录。"""
import fitz, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SRC = r"D:\APP\project_practice\codex-project\简历\简历修改版本\模板简历（随时跟新）\彭博裕-嵌入式软件工程师-10.pdf"
OUT = r"D:\APP\project_practice\codex-project\简历\中间文件\销售简历-20260925\layout-dump.json"

doc = fitz.open(SRC)
print(f"页数: {len(doc)}")
page = doc[0]
r = page.rect
print(f"页面尺寸: {r.width:.1f} x {r.height:.1f} pt  (A4=595x842)")

d = page.get_text("dict")
spans = []
images = []
for block in d["blocks"]:
    if block["type"] == 1:
        images.append(block["bbox"])
        continue
    for line in block["lines"]:
        for span in line["spans"]:
            spans.append({
                "text": span["text"],
                "font": span["font"],
                "size": round(span["size"], 2),
                "color": f"#{span['color']:06X}",
                "flags": span["flags"],
                "bbox": [round(v, 1) for v in span["bbox"]],
            })

print(f"\n照片/图片对象: {len(images)} 个")
for bb in images:
    print(f"  bbox={bb}  宽={bb[2]-bb[0]:.1f}pt 高={bb[3]-bb[1]:.1f}pt")

print("\n== 字体组合清单（字体/字号/颜色/加粗 → 出现次数 + 样例） ==")
combos = {}
for s in spans:
    key = (s["font"], s["size"], s["color"], bool(s["flags"] & 16))
    combos.setdefault(key, []).append(s["text"])
for key in sorted(combos, key=lambda k: -len(combos[k])):
    texts = combos[key]
    sample = " | ".join(t.strip() for t in texts[:3] if t.strip())[:60]
    print(f"  {key[0]:<28} {key[1]:>5.2f}pt {key[2]} bold={key[3]}  x{len(texts):<3} 样例: {sample}")

print("\n== 文本行流（按 y 分组，标注 x 起点 → 判断栏式结构） ==")
lines = []
for block in d["blocks"]:
    if block["type"] == 1:
        continue
    for line in block["lines"]:
        t = "".join(sp["text"] for sp in line["spans"]).strip()
        if not t:
            continue
        x0, y0 = line["bbox"][0], line["bbox"][1]
        sz = max(sp["size"] for sp in line["spans"])
        lines.append((round(y0, 1), round(x0, 1), round(sz, 1), t))
lines.sort()
for y, x, sz, t in lines:
    print(f"  y={y:>6.1f} x={x:>6.1f} {sz:>4.1f}pt  {t[:52]}")

print("\n== 矢量线条（分隔线/表格框线） ==")
for dr in page.get_drawings():
    for item in dr["items"]:
        if item[0] == "l":
            p1, p2 = item[1], item[2]
            print(f"  line ({p1.x:.1f},{p1.y:.1f}) -> ({p2.x:.1f},{p2.y:.1f})  color={dr.get('color')}")
        elif item[0] == "re":
            rr = item[1]
            print(f"  rect {rr}  color={dr.get('color')} fill={dr.get('fill')}")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"page": [r.width, r.height], "images": images, "spans": spans}, f, ensure_ascii=False, indent=1)
print(f"\n完整span数据已存 {OUT}")
