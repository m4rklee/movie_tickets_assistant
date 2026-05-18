# 迭代日志

## v1 — 2026-05-16（脚手架 + 评测基线）

### 交付

- PRD / JTBD / 数据字典 / 工作流设计
- ticket-api（drafts、confirm、list、report）
- docker-compose（MySQL + API）
- Dify ParseTicket / ConfirmTicket 搭建文档、Prompt、代码节点
- eval 10 case 模板 + scorecard 脚本
- v2 Langbot 飞书、v3 问答报表设计文档

### 评测首轮（模拟 perfect parse）

在替换真实票样前，使用与 `expected.json` 一致的模拟 parse 输出跑分：

| 指标 | 结果 |
|------|------|
| 核心字段 10/10 | 100% |
| 电子专属 5/5 | 100% |
| 纸质座位 5/5 | 100% |
| 幻觉 | 0 |

> 真实 Dify Vision 实测需在本地配置模型后填写 scorecard 实测列。

### 下一步

1. 将脱敏 `ticket.jpg` 放入各 case 目录
2. Dify 导出 `parse-ticket.yml` / `confirm-ticket.yml`
3. 实测后更新本表与 [baseline-metrics.md](../eval/baseline-metrics.md)

### v2 计划

Langbot + 飞书卡片确认（见 [v2-langbot-feishu.md](./v2-langbot-feishu.md)）

### v3 计划

TicketQA Chatflow + TicketReport Workflow（见 [v3-qa-reports.md](./v3-qa-reports.md)）
