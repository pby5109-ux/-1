#!/usr/bin/env python3
"""保留实习经历栏，仅更新 09-20 正文并按指定字号重排，用于测试最大可用字号。"""
import copy, hashlib, sys, zipfile
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn

BASE = Path(r"D:\APP\project_practice\codex-project\简历\简历修改版本\模板简历（随时跟新）\彭博裕-嵌入式软件工程师-含实习无校园.docx")
EXPECTED = "C42B86ED97E858E116FCD5524ACFDADA49CE5E7E97C41AEB7F2B3747178346F2"
TEXT_OVERRIDES = {
    "项目简介#1": "集成示波器、数字万用表、可调直流电源和信号发生器，支持波形实时显示及频率、幅度测量，频率测量误差1 Hz，电压与电阻测量误差1%；支持直流电压稳定输出；信号发生器输出正弦、方波等，频率档位覆盖50 Hz～50 kHz。",
    "并发优化": "针对采集与显示共享缓冲区的读写冲突，设计双缓冲与状态机协同机制，管理波形数据的读写权限和切换时机，保证单帧绘制期间数据一致，避免新旧帧混用，并允许新帧准备与当前帧绘制并行。",
    "测量与调试": "基于内部参考电压估算VDDA，结合GPIO档位识别、分压与偏置补偿完成多量程换算，提升测量准确性；优化采样率与波表长度配置、定时参数计算及更新时序，修正低频输出偏差，实现频率切换及时生效。",
    "系统开发": "分层封装传感器驱动与采集逻辑，设计RTC周期采集与按键唤醒双事件机制，分别维护采样与显示期限，避免临时查看打乱上报节拍；支持无网关条件下现场查看数据，并通过有效性检查标识采集异常，保障不同情况下数据的有效观测。",
    "功耗优化": "结合Stop模式、代码系统优化、外设供电门控与休眠控制，抑制GPIO漏电并隔离断电外设信号，将整板待机电流控制在µA级。",
    "协议开发": "设计CRC校验、序号匹配及ACK超时有限重试机制，实现上报确认与传输异常处理；开发PC网关处理半包、粘包及坏帧，按节点与序号去重且对重传仍回ACK，完成数据解析及带时间的故障日志记录，支持采集异常追溯。",
    "光照适配": "基于Otsu算法自动估计灰度阈值，通过按键触发重估、帧间保持阈值，实现不同光环境下的阈值校准；对无灰度对比的画面跳过识别并重试，避免无效画面参与阈值估计。",
    "AI工具": "熟练使用Codex、Claude Code、DeepSeek Harness、ZCode搭建工作流并实现快速产品设计与开发。",
}

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1<<20), b''): h.update(c)
    return h.hexdigest().upper()

def replace_runs(paragraph, segments):
    old=list(paragraph.runs)
    styles=[copy.deepcopy(r._r.rPr) if r._r.rPr is not None else None for r in old]
    for r in old: paragraph._p.remove(r._r)
    for text, idx in segments:
        run=paragraph.add_run(text)
        st=styles[min(idx,len(styles)-1)]
        if st is not None: run._r.insert(0, copy.deepcopy(st))

def main():
    out=Path(sys.argv[1]); scale=int(sys.argv[2])          # 0=原字号, 1=+1级, 2=+2级
    line=sys.argv[3] if len(sys.argv)>3 else "230"
    head=sys.argv[4] if len(sys.argv)>4 else "60"
    if out.exists(): print('ERROR: 输出已存在'); return 2
    assert sha(BASE)==EXPECTED, '基准哈希不符'
    doc=Document(BASE)
    # 正文覆盖
    seen={}; applied=0
    for p in doc.paragraphs:
        t=p.text
        if '：' not in t: continue
        bullet=t.lstrip().startswith('•')
        body=t.lstrip().lstrip('•').strip()
        label=body.split('：',1)[0].strip()
        seen[label]=seen.get(label,0)+1
        key=label if label not in ('项目简介','项目职责') else '%s#%d'%(label,seen[label])
        if key not in TEXT_OVERRIDES: continue
        replace_runs(p, [(('• %s：'%label) if bullet else ('%s：'%label),0), (TEXT_OVERRIDES[key],1)])
        applied+=1
    # 字号
    base_map={'16':'17','18':'18','19':'20','20':'21'} if scale==1 else {'16':'18','18':'19','19':'20','20':'21'}
    if scale==0: base_map={}
    n=0
    for run in doc.element.body.iter(qn('w:r')):
        rPr=run.find(qn('w:rPr'))
        if rPr is None: continue
        for tag in ('w:sz','w:szCs'):
            e=rPr.find(qn(tag))
            if e is not None and e.get(qn('w:val')) in base_map:
                e.set(qn('w:val'), base_map[e.get(qn('w:val'))]); n+=1
    # 行距与段前
    m=k=0
    heads={'教育背景','竞赛与荣誉','项目经历','实习经历','专业技能'}
    for p in doc.paragraphs:
        pPr=p._p.find(qn('w:pPr'))
        if pPr is None: continue
        sp=pPr.find(qn('w:spacing'))
        if sp is None: continue
        if sp.get(qn('w:line')): sp.set(qn('w:line'), line); m+=1
        if p.text.strip() in heads and sp.get(qn('w:before')) not in (None,'0'):
            sp.set(qn('w:before'), head); k+=1
    staged=out.with_name(out.stem+'.staged.docx'); doc.save(staged)
    with zipfile.ZipFile(BASE) as z, zipfile.ZipFile(staged) as e:
        doc_xml=e.read('word/document.xml')
    with zipfile.ZipFile(BASE) as z, zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as o:
        for item in z.infolist():
            o.writestr(item, doc_xml if item.filename=='word/document.xml' else z.read(item.filename))
    staged.unlink()
    print('scale=%d 字号=%d处 行距=%s(%d处) 段前=%s(%d处) 正文覆盖=%d处' % (scale,n,line,m,head,k,applied))
    return 0

raise SystemExit(main())
