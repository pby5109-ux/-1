import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(here);
const modules = process.argv[2];
const cssPath = process.argv[3];
if (!modules || !cssPath) throw Error('Usage: node 生成阅读版.mjs <node_modules> <shared lesson.css>');
const require = createRequire(import.meta.url);
const markedEntry = require.resolve(path.join(modules, 'marked'));
const {marked} = await import(pathToFileURL(markedEntry));
const bank = JSON.parse(fs.readFileSync(path.join(here,'题库源数据.json'),'utf8'));
const qs = bank.questions;
if(qs.length !== 52 || new Set(qs.map(q=>q.id)).size !== 52) throw Error('Invalid question count/ids');
const labels={A:'必会',B:'加强',C:'了解'};
const groups={C01:'一、预处理与关键字',C13:'二、类型、指针与布局',C25:'三、内存与数据搬移',C36:'四、表达式与工程诊断',C43:'五、手写函数',C51:'六、嵌入式综合迁移'};
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const intro=`采用C11。数字题默认8位字节、ILP32（int/long/普通对象指针4字节）、小端；对齐按题目明示。合法性/未定义行为优先于计算。代码片段所需标准头文件、外壳及场景占位函数按题意补齐。题目是学习资料改编，不是企业官方试卷。`;
const guideName='00-使用说明与调研依据.md';
let questionMd=`# C语言专项训练：题目卷\n\n52题｜A必会34｜B加强15｜C了解3\n\n${intro}\n\n[使用说明与调研依据](${guideName}) · [作答后查看解析](02-答案与解析.md) · [手机折叠版](03-手机自测版.html)\n\n首次先做C02、C08、C14。每次3～5道口述/推导题或1道手写题。不要求逐字背诵，不在此记录分数。\n\n`;
let answerMd=`# C语言专项训练：答案与解析\n\n${intro}\n\n答案检查的是关键点，不要求同一句话。先做[题目卷](01-题目卷.md)。依据与原文纠错见[使用说明](${guideName})。\n\n`;
let cards='';
for(const q of qs){
  for(const k of ['id','level','title','source','q','a','logic','trap','ref']) if(!q[k]) throw Error(`${q.id}: missing ${k}`);
  if(groups[q.id]){questionMd+=`## ${groups[q.id]}\n\n`;answerMd+=`## ${groups[q.id]}\n\n`;}
  const head=`### ${q.id}｜${q.level} ${labels[q.level]}｜${q.title}`;
  const meta=`来源：${q.source}`;
  questionMd+=`${head}\n\n${q.q}\n\n${meta}\n\n---\n\n`;
  const ans=`#### 答案与解析\n\n${q.a}\n\n#### 口述思路\n\n${q.logic}\n\n#### 易错提醒\n\n${q.trap}\n\n依据：${q.ref}。对应官方链接见使用说明的“技术核对入口”。`;
  answerMd+=`${head}\n\n${q.q}\n\n${meta}\n\n${ans}\n\n---\n\n`;
  cards+=`<article id="${q.id}" data-level="${q.level}" class="card question"><div class="tag">${q.id} · ${q.level} ${labels[q.level]}</div><h2>${escape(q.title)}</h2><div class="prompt">${marked.parse(q.q)}</div><details class="answer"><summary>我已作答 · 展开答案与口述思路</summary>${marked.parse(ans)}<p class="source">${escape(meta)}</p></details><a class="top" href="#top">返回筛选区</a></article>`;
}
fs.writeFileSync(path.join(root,'01-题目卷.md'),questionMd);
fs.writeFileSync(path.join(root,'02-答案与解析.md'),answerMd);
const guide=fs.readFileSync(path.join(root,guideName),'utf8');
const css=fs.readFileSync(cssPath,'utf8');
const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>C语言52题 · 自我训练</title><style>${css}
main{max-width:860px;padding-top:30px}h1{font-size:2rem}.question h2{margin:8px 0 18px;border:0;padding:0;font-size:1.35rem}.tag{font-weight:700;color:var(--blue)}.question{padding:22px}.prompt p,details p{overflow-wrap:anywhere}pre code{background:none;padding:0;color:inherit}pre{font-size:14px;line-height:1.65;white-space:pre;overflow:auto}summary{cursor:pointer;color:var(--blue);font-weight:650;padding:12px 0}details.answer{border-top:1px solid var(--line);margin-top:18px}details.answer[open]{padding-bottom:10px}details h4{font-size:1rem;color:var(--blue);margin-bottom:6px}.source{font-size:13px;color:var(--muted)}.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center}button,input,select{font:inherit;border:1px solid #a9bbc5;background:white;border-radius:8px;padding:9px 12px;color:var(--ink)}button{cursor:pointer}input{width:100%;max-width:380px}.top{display:inline-block;font-size:13px;margin-top:15px}.muted{color:var(--muted)}[hidden]{display:none!important}table{display:block;overflow-x:auto;font-size:14px}td{min-width:100px}.guide h1{font-size:1.6rem}.guide h2{font-size:1.2rem}.guide{background:#fff}.status{font-weight:600;color:var(--blue)}
@media(max-width:600px){main{padding:24px 12px 50px}h1{font-size:1.65rem}.card{padding:17px 14px}.question h2{font-size:1.2rem}body{font-size:16px}.controls button{flex:1}pre{padding:12px;font-size:13px}button,select{min-height:44px}}
@media print{.controls,.top,#guide-toggle,.status{display:none}.card{break-inside:auto;border:0;border-top:1px solid #aaa;border-radius:0}pre{white-space:pre-wrap;color:black;background:#f6f6f6}details.answer:not([open]){display:none}}
</style></head><body><main id="top"><p class="tag">STM32 / MCU / RTOS · C基础</p><h1>懂原理，再把话说清楚</h1><p class="lead">52道主问题 · 必会34 / 加强15 / 了解3<br>先回答，再展开；答案是检查要点，不是背诵台词。</p><div class="note">首次推荐 C02、C08、C14。每次选3～5道口述题或1道手写题。${escape(intro)}</div><details id="guide-toggle" class="card guide"><summary>使用顺序、招聘调研、原文纠错与来源</summary>${marked.parse(guide)}</details><div class="card"><div class="controls"><label for="level">范围</label><select id="level"><option value="ALL">全部等级</option><option value="A">A 必会</option><option value="B">B 加强</option><option value="C">C 了解</option></select><input id="search" type="search" aria-label="搜索题号或关键词" placeholder="搜索题号或知识点，如 C08、指针"><button id="random">当前范围随机3题</button><button id="reset">恢复全部</button><button id="close">收起所有答案</button></div><p id="status" class="status">显示52题</p><p class="muted">不保存分数或作答记录。可把题号和自己的答案发给老师，按理解与表达继续追问。手机离线打开无需登录。</p></div><section id="questions">${cards}</section></main><script>
const articles=[...document.querySelectorAll('.question')];
const level=document.querySelector('#level'),search=document.querySelector('#search'),status=document.querySelector('#status');
let selected=null;
function eligible(){const key=search.value.trim().toLowerCase();return articles.filter(a=>(level.value==='ALL'||a.dataset.level===level.value)&&(!key||a.id.toLowerCase().includes(key)||a.querySelector('h2').textContent.toLowerCase().includes(key)||a.querySelector('.prompt').textContent.toLowerCase().includes(key)));}
function render(){const allow=new Set(eligible().filter(a=>selected===null||selected.has(a.id)));articles.forEach(a=>{a.hidden=!allow.has(a);if(a.hidden)a.querySelector('details').open=false});status.textContent='显示'+allow.size+'题 / 共52题';}
level.addEventListener('change',()=>{selected=null;render()});search.addEventListener('input',()=>{selected=null;render()});
document.querySelector('#random').addEventListener('click',()=>{const pool=eligible();for(let i=pool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[pool[i],pool[j]]=[pool[j],pool[i]];}selected=new Set(pool.slice(0,3).map(a=>a.id));articles.forEach(a=>a.querySelector('details').open=false);render()});
document.querySelector('#reset').addEventListener('click',()=>{selected=null;level.value='ALL';search.value='';render()});
document.querySelector('#close').addEventListener('click',()=>articles.forEach(a=>a.querySelector('details').open=false));
if(/^#C[0-9]{2}$/.test(location.hash)){const a=document.querySelector(location.hash);if(a)a.scrollIntoView();}
</script></body></html>`;
fs.writeFileSync(path.join(root,'03-手机自测版.html'),html);
const headers='#include <stdint.h>\n#include <stddef.h>\n#include <stdbool.h>\n#include <string.h>\n#include <limits.h>\n';
const selectedIds=['C09','C43','C44','C45','C46','C47','C48','C49','C50'];
let code=headers+'\n/* Automatically extracted from answer blocks; edit JSON source first. */\n';
for(const id of selectedIds){const q=qs.find(q=>q.id===id);const blocks=[...q.a.matchAll(/~~~c\n([\s\S]*?)\n~~~/g)];if(blocks.length!==1)throw Error(id+' code missing');code+='\n/* '+id+' */\n'+blocks[0][1]+'\n';}
fs.writeFileSync(path.join(here,'参考实现.c'),code);
fs.writeFileSync(path.join(here,'结构验证.json'),JSON.stringify({questions:qs.length,levels:qs.reduce((a,q)=>(a[q.level]=(a[q.level]||0)+1,a),{}),ids_unique:true,answers_complete:qs.every(q=>q.a&&q.logic&&q.trap&&q.source),mobile_cards:(html.match(/class="card question"/g)||[]).length,default_open_answers:(html.match(/<details class="answer" open/g)||[]).length,extracted_code_ids:selectedIds},null,2));
console.log('Generated 2 Markdown readers, offline HTML, reference C, and structure validation.');
