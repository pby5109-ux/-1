# approved-content.json 契约

> 当前嵌入式生成使用schema v2，见[current-workflow.md](current-workflow.md)及`current-content.json`。下方schema v1仅保留供旧包重建，不要求新稿恢复8条项目、两条校园或自评。

## 当前v2检查与旧生成的区别（2026-10-11）

`build_current_resume.py --check`接受现行v2快照：审批可用`approved_by/approved_on/approval_note`（或历史`source`），校园可用`mode=long/short/none`，long含`name/role/period/bullets`，short使用`text`或`short_text`。可变条目以`source_refs`引用`profile/project`事实ID或`sources`中带status的来源对象；来源字符串元数据不是证据ID，禁止/未解决/设计方案与限定词仍检查。

`approved=true`与上述字段只记录声明，检查不会证明真实批准或工程事实。带`snapshot_kind=dynamic_template_snapshot`的素材不能进入9月17日固定生成器；`sync_status=partial_pending_protected_wording_sync`说明与当前PDF仍有正文差异，需按最新PDF与批准差量处理。成功检查不表示已完成正文同步、当前版式兼容或一页验收。

2026-10-24：`--check`还会只读核对`sources`中带路径的来源对象，SHA256缺失/错误、文件缺失/不可读或内容变化均提示；`--check --require-current-sources`在这些问题或正文待同步时返回2，否则返回0。此选项不能用于生成/导入基准。`snapshot_review.observed_templates`和`pending_claims`只保存文件观察与待核对问题，不作为正文条目的证据ID、批准或实测结论。维护元数据不提高正文修订号或重签旧批准；真实同步后才按准确批准差量更新正文版本与来源。

## 历史schema v1

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
