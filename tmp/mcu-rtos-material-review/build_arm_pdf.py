from pathlib import Path
import json, html, re
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor

root=Path(__file__).resolve().parents[2]
data=json.loads((root/'记忆与产物/03-知识资料/ARM面试修订内容.json').read_text(encoding='utf-8'))
qs=data['questions']
assert len(qs)==40
assert len({q['id'] for q in qs})==40
for q in qs:
 assert 'p' in q['read'] and q['more'] and len(q['body'])>=5
out=root/'记忆与产物/03-知识资料/Cortex系列-ARM面试修订版.pdf'
pdfmetrics.registerFont(TTFont('CN','C:/Windows/Fonts/simhei.ttf'))
W,H=595.28,841.89
c=canvas.Canvas(str(out),pagesize=(W,H))
c.setTitle('Cortex系列 - ARM面试修订版 - 40题逐题详解')
c.setAuthor('MCU与RTOS学习资料')
TOTAL=45
page=0
metrics=[]
def para(text,x,y,width=519,size=13,leading=21,color='#263746'):
 s=ParagraphStyle('p',fontName='CN',fontSize=size,leading=leading,wordWrap='CJK',textColor=HexColor(color))
 p=Paragraph(text,s);_,h=p.wrap(width,2000)
 if y-h<55: raise RuntimeError(f'Page {page}: overflow at {y-h:.1f}')
 p.drawOn(c,x,y-h)
 return y-h
def start(title,sub,key):
 global page
 page+=1
 c.bookmarkPage(key);c.addOutlineEntry(title,key,level=0)
 c.setFillColor(HexColor('#123149'));c.rect(0,H-100,W,100,fill=1,stroke=0)
 c.setFillColor(HexColor('#7DDFC4'));c.setFont('CN',10);c.drawString(38,H-24,'MCU / RTOS  |  ARM 逐题讲解')
 para(html.escape(title),38,H-40,size=17,leading=23,color='#FFFFFF')
 c.setFillColor(HexColor('#D7E8F0'));c.setFont('CN',9.5);c.drawString(38,H-87,sub)
 return H-120
def end(y):
 metrics.append({'page':page,'bottom':round(y,1)})
 c.setStrokeColor(HexColor('#D7E2E8'));c.line(38,40,W-38,40)
 c.setFillColor(HexColor('#526D7E'));c.setFont('CN',9)
 c.drawString(38,25,'指南页码 = 322页中文版PDF物理页  |  2026-09-11 详解版')
 c.drawRightString(W-38,25,f'{page} / {TOTAL}')
 c.showPage()

y=start('读得懂，再记得住','使用说明与六组学习内容对应关系','intro')
intro=[
('本版改了什么','由14页短提纲扩展为40道逐题讲解。每题提供独立页码、概念拆解、原因或流程、例子、误区和带简答的自测；不要求逐字背诵。'),
('页码怎样用','“先读”是最直接的原书位置，“再查”是补背景或深入的位置。均为你提供的322页《Cortex-M3权威指南》的PDF物理页，不是本修订版页码。每道题内的小检查题沿用本题参考页。'),
('没有对应章节怎么办','FreeRTOS API、M0+、M4/M7和具体STM32电源实现并非旧指南完整覆盖的内容。相关题明确区分“指南背景页”和“官方直接入口”，不制造虚假页码。O编号的可点击来源见最后一页。'),
('按你原来的六组学','①基础、寄存器、双栈、启动：Q01～Q11；②存储与访问：Q12～Q16、Q29～Q31；③异常/NVIC/现场：Q17～Q25、Q34；④RTOS衔接：Q06～Q07、Q26～Q28、Q33；⑤低功耗/调试：Q24～Q25、Q32～Q35；⑥汇编/链接查用：Q10～Q11、Q36～Q38。Q39～Q40只补跨核差异。'),
('如何判断学会','先读正文，用自己的话解释机制，再遮住最后一段回答自测。答不出就按“先读”翻书；仍不清楚再看“再查”。A要求会解释和应用，B理解用途与限制，C仅按岗位深挖。'),
('重要边界','本文是原创讲解与纠错，不是原书全文替代，也不是官方认证教材。示例用于理解，不代表已在你的板上实测；不要求学习Linux。原始华清PDF与权威指南均保留。')]
for label,text in intro:
 y=para('<font color="#00695C">'+label+'</font>  '+html.escape(text),38,y)-14
end(y)
for half in range(2):
 y=start(f'题目导航 {half+1}/2','点击题目可跳转；右侧是本修订版页码，不是指南页码',f'index{half}')
 for q in qs[half*20:(half+1)*20]:
  dest=int(q['id'][1:])+3
  line=f'<link href="#{q["id"]}" color="#123149">{q["id"]}  {html.escape(q["title"])}</link>'
  y=para(line,38,y,width=475,size=11.2,leading=17)-10
  c.setFont('CN',10);c.setFillColor(HexColor('#00695C'));c.drawRightString(W-38,y+11,str(dest))
 end(y)
for q in qs:
 y=start(q['id']+'  '+q['title'],q['level']+'  |  一题一页，先理解再复述',q['id'])
 y=para('<font color="#00695C">先读指南</font>  '+html.escape(q['read']),38,y,size=10.8,leading=17)-7
 y=para('<font color="#00695C">没懂再查</font>  '+html.escape(q['more']),38,y,size=10.8,leading=17)-17
 for label,text in q['body']:
  y=para('<font color="#00695C">'+html.escape(label)+'</font>  '+html.escape(text),38,y,size=13,leading=21)-14
 end(y)
y=start('阅读原文时，带着这份纠错清单','对应位置明确区分“华清原PDF”和“权威指南”','errata')
items=[
('华清原PDF p1～2','ARM7/ARM9不能一概归为ARMv6。ARM7TDMI为ARMv4T；Cortex-M3为ARMv7-M，M4/M7为ARMv7E-M。'),
('华清原PDF p3～5、p9','Thread不一定用PSP；PendSV是异常号14；MemManage=4、BusFault=5。复位先读MSP和复位向量，不是直接从0地址执行代码。'),
('华清原PDF p6～7','堆增长方式不能一概而论；SIMD不等于单周期多指令；屏障不是简单强弱排序，参见Q30。'),
('指南 p24、p48','PRIMASK不屏蔽NMI与HardFault；向量入口的Thumb最低位规则不适用于首项初始MSP，初始MSP反而应满足栈对齐。'),
('指南 p52、p54','APSR饱和标志应为Q，不是S；p54的AND对应C按位与&，不是按位或|。看指令表时仍需核对具体指令。'),
('指南 p72～73、p179～182','DMB不能当作全部访问完成屏障，ISB不是最强数据屏障；双栈/MPU示例不等于所有FreeRTOS任务都非特权运行。'),
('指南 p206～207、p316','XN=1禁止取指、XN=0不因XN禁止取指，原文表格/解释有笔误；Fault示例不能占用RTOS已使用的PendSV，也不能盲目信任已损坏的栈。'),
('这不是全书勘误','仅列本轮相关核查发现。旧工具链代码和寄存器配置不可无条件复制到当前工程。教材帮助理解，实际编码还要匹配内核、芯片和工具链。')]
for label,text in items:
 y=para('<font color="#00695C">'+html.escape(label)+'</font>  '+html.escape(text),38,y,size=12.2,leading=19)-12
end(y)
y=start('官方查证入口','O编号对应每题的补充来源；标题可点击','sources')
y=para('中文主参考：'+html.escape(data['guide'])+'。本版逐题标出的p均指该文件物理页。官方网页无固定页码，按所列函数或章节检索；版本不同请重新核对。',38,y,size=11.5,leading=18)-16
for code,label,url in data['sources']:
 y=para(f'<link href="{html.escape(url,quote=True)}" color="#00695C">{code}  {html.escape(label)}</link>',38,y,size=11.2,leading=18)-17
y=para('O2包含O2a/O2b，O7包含O7a/O7b。O4在线main会更新，它只用于核查原理；工程事实以自己的实际端口版本为准。指南没有M0+/M4/M7直接讲解，相关指南页仅是对照基础。',38,y,size=10.5,leading=17)-5
end(y)
assert page==TOTAL,(page,TOTAL)
c.save()
(root/'tmp/mcu-rtos-material-review/arm-detailed-layout.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(f'{out}\n{page} pages; minimum content bottom: {min(x["bottom"] for x in metrics)}')
