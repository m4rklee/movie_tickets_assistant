# v3：票夹问答与观看报表

## 依赖

- MVP 票夹数据已稳定写入 `movie_tickets`
- ticket-api 已提供：
  - `GET /api/tickets` — 列表/筛选
  - `GET /api/reports/summary?year=` — 聚合报表

## 3.1 TicketQA（Chatflow）

### 形态

Dify **Chatflow** + 自定义工具（OpenAPI 或 HTTP Request Tool）。

### 工具定义

| 工具名 | 方法 | 说明 |
|--------|------|------|
| `list_tickets` | GET `/api/tickets` | 参数：`movie_title`, `limit` |
| `get_ticket` | GET `/api/tickets/{id}` | 单条详情 |

OpenAPI 片段见 [workflow/openapi/ticket-api.yaml](../workflow/openapi/ticket-api.yaml)。

### System Prompt

见 [workflow/prompts.md](../workflow/prompts.md) 中「v3 TicketQA」。

### 约束

- 必须先调工具再回答；无记录时明确说明
- 禁止编造片名、日期、价格

## 3.2 TicketReport（Workflow）

### 输入

| 变量 | 类型 | 说明 |
|------|------|------|
| `year` | 数字 | 可选，默认当年 |

### 节点

1. HTTP `GET /api/reports/summary?year={{year}}`
2. LLM：将 JSON 转为 Markdown 报表（表格 + 简短洞察）
3. 结束：输出报表

### 报表结构

1. 概览：观影次数、总支出、不重复片目数
2. 按月：月份 / 场次 / 支出
3. Top 影厅
4. 片单（按日期倒序）

### Prompt 摘录

```
你是观影数据分析师。根据以下 JSON 生成中文 Markdown 报表，不要编造 JSON 中不存在的数据。
数据：{{http_body}}
```

## 验收

- [ ] 问「今年看了几部」→ 调用 summary 或 list 后正确回答
- [ ] 问「花样年华看了吗」→ 检索 movie_title 含关键词
- [ ] Report 输出含总支出与按月表
- [ ] 空库时问答不幻觉

## 本地验证 API

```bash
curl -H "X-API-Key: dev-local-key" "http://localhost:8000/api/reports/summary?year=2026"
```
