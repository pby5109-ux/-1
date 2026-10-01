# -*- coding: utf-8 -*-
"""Word COM 导出 PDF + fitz 页数/留白/关键串检查。用法：export_and_check.py <docx> <pdf>"""
import sys, os, time
import fitz

docx_path = os.path.abspath(sys.argv[1])
pdf_path = os.path.abspath(sys.argv[2])

import win32com.client
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
try:
    d = word.Documents.Open(docx_path, ReadOnly=False)
    d.SaveAs2(pdf_path, FileFormat=17)
    pages = d.ComputeStatistics(2)  # wdStatisticPages
    d.Close(False)
finally:
    word.Quit()
print("Word报告页数:", pages)

doc = fitz.open(pdf_path)
print("PDF实际页数:", len(doc))
page = doc[0]
maxy = 0
for b in page.get_text("dict")["blocks"]:
    if b["type"] == 0:
        maxy = max(maxy, b["bbox"][3])
print(f"正文最低点 y={maxy:.1f}pt / 页高841.9 → 底部留白≈{841.9-maxy:.1f}pt")

text = "".join(p.get_text() for p in doc).replace(" ", "").replace("\u00a0", "").replace("\n", "")
required = ["客户经理", "湘潭市仙女竹业有限公司", "销售实习生", "2024.06—2024.10", "上海日用品展览会",
            "100余名", "数十万元级", "优秀销售实习生", "组织统筹", "现场应急",
            "基于STM32的多功能综合测量平台", "基于MSPM0与K230的移动目标瞄准系统",
            "方案统筹", "需求拆解", "技术基础", "工程素养", "C1驾驶证", "WPS", "2027届", "专业综合测评排名前10%",
            "蓝桥杯省级三等奖", "电子设计大赛校级一等奖"]
forbidden = ["LoRa", "威思顿", "智能电表", "嵌入式软件工程师", "竹制品", "竹材", "FreeRTOS",
             "科创组织", "现场保障", "编程基础", "内核与实时系统", "开发板实践", "目标筛选", "光照适配"]
miss = [s for s in required if s.replace(" ", "") not in text]
bad = [s for s in forbidden if s.replace(" ", "") in text]
print("必需串缺失:", miss if miss else "无")
print("禁串出现:", bad if bad else "无")
