# approved-content.json 契约

> 当前嵌入式生成使用schema v2，见[current-workflow.md](current-workflow.md)及`current-content.json`。下方schema v1仅保留供旧包重建，不要求新稿恢复8条项目、两条校园或自评。

生成脚本接受UTF-8 JSON。所有字符串必须是最终可排版文字，不允许占位符。

```json
{
  "schema_version": 1,
  "preview_id": "company-role-YYYYMMDD-v1",
  "approved": true,
  "template": "embedded",
  "company": "公司名称",
  "role": "岗位名称",
  "date": "YYYYMMDD",
  "header": {
    "target": "嵌入式软件工程师",
    "tags": "STM32｜FreeRTOS｜外设驱动｜软硬件联调"
  },
  "skills": [
    {"label": "开发调试", "text": "...", "evidence_ids": ["skill.toolchain"]},
    {"label": "RTOS外设", "text": "...", "evidence_ids": ["skill.rtos"]},
    {"label": "编程及技能", "text": "...", "evidence_ids": ["skill.c"]}
  ],
  "projects": [
    {
      "id": "instrument",
      "name": "项目名",
      "role": "角色",
      "period": "2026.03—2026.06",
      "bullets": [
        {"label": "系统架构", "text": "...", "evidence_ids": ["instrument.architecture"]}
      ]
    }
  ],
  "enterprise": {
    "name": "烟台东方威思顿电气有限公司",
    "role": "智能电表软硬件测试实习生",
    "period": "2025.10—2025.11",
    "bullets": [
      {"label": "产品认知", "text": "...", "evidence_ids": ["experience.meter_training"]},
      {"label": "开发板实践", "text": "...", "evidence_ids": ["experience.meter_board"]}
    ]
  },
  "campus": {
    "name": "山东建筑大学校学生会科创部",
    "role": "部长",
    "period": "2023.09—2025.06",
    "bullets": [
      {"label": "科创组织", "text": "...", "evidence_ids": ["campus.organization"]},
      {"label": "现场保障", "text": "...", "evidence_ids": ["campus.event_recovery"]}
    ]
  },
  "competitions": [
    {"label": "蓝桥杯", "text": "...", "evidence_ids": ["award.lanqiao"]},
    {"label": "电子设计", "text": "...", "evidence_ids": ["car_contest.contribution"]},
    {"label": "项目实践", "text": "...", "evidence_ids": ["car_lab.contribution"]},
    {"label": "校级荣誉", "text": "...", "evidence_ids": ["award.school"]}
  ],
  "self_evaluation": {
    "label": "个人优势",
    "text": "...",
    "evidence_ids": ["profile.strengths"]
  }
}
```

硬性结构：

- `approved`必须为`true`；
- `template`只能是`embedded`或`general`；
- `skills`恰好3条；
- `projects`恰好3个，全部项目描述合计恰好8条；
- 企业实践2条、校园经历2条、竞赛/荣誉4条、自我评价1条；
- 每一条可变文字都必须至少带一个存在且允许用于简历的`evidence_id`；
- `preview_id`必须与用户明确批准的预览一致。

生成器不负责替作者判断真实性，只接受已通过验证脚本的内容。

可选`approval_record`记录`preview_id`、用户批准原句、批准时间及预览文件SHA256，便于跨会话追溯；这不是自动授权凭证。现有schema_version=1批准稿继续兼容。JD、差距和预览风险保存在外部Markdown，不能混入最终能力正文。新增限定证据的同条正文须包含其`required_qualifier_terms`之一；政策未知或状态为未解决/禁止的证据拒绝生成。
