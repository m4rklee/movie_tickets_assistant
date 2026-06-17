# Movie Ticket Assistant

> An AI-powered movie ticket wallet for recognizing, storing, querying, and analyzing China Film Archive tickets.

中国电影资料馆智能票据助手是一个面向影迷的票据管理工具。项目通过多模态识别、结构化入库、自然语言查询和报表生成，将电子票、纸质票中分散的观影信息沉淀为可检索、可分析的个人观影数据库。

## Highlights

- **Ticket recognition workflow**: 使用 Dify Workflow/多模态能力识别电子票和纸质票字段。
- **Structured ticket database**: 后端校验票据字段并写入 MySQL。
- **Natural-language SQL query**: 基于 SQL 查询工具的智能体支持自然语言检索观影记录。
- **AI report generation**: 基于观影历史生成统计分析、图表和观影总结。
- **Feishu/Langbot extension**: 可选接入飞书机器人，实现票据助手对话入口。
- **Evaluation docs**: `eval/` 中保留字段识别和模型评测相关材料。

## Demo

票据识别：

<img src="docs/pics/ticket_recognition.png" width="720" alt="票据识别：上传图片后结构化入库" />

票据样例：

| 电子票截图 | 纸质票 |
|---|---|
| <img src="docs/pics/digital_ticket.jpeg" width="360" alt="电子票样例" /> | <img src="docs/pics/paper_ticket.jpeg" width="360" alt="纸质票样例" /> |

自然语言查询：

<img src="docs/pics/sql_movie_search.png" width="720" alt="数据查询：自然语言转 SQL 查询票夹" />

AI 报表：

<img src="docs/pics/ai_report.png" width="720" alt="报表生成：对话与查询过程" />

<img src="docs/pics/ai_report_chart.png" width="720" alt="报表生成：Agent 查询数据并输出图表" />

## Architecture

```text
Ticket image
    |
    v
Dify Workflow / multimodal extraction
    |
    v
ticket-api / FastAPI
    |
    +--> field validation
    +--> MySQL persistence
    +--> natural-language SQL query
    +--> AI report generation
    |
    v
Web / Feishu / Langbot interface
```

## Features

| Module | Description |
|---|---|
| **票据识别** | 上传电子票或纸质票图片，抽取电影名、日期、时间、影院、影厅、座位、票价等字段。 |
| **字段校验** | 后端校验日期、价格、座位、支付状态等格式，减少脏数据。 |
| **票夹数据库** | 将观影记录持久化到 MySQL，形成个人电影资料馆票夹。 |
| **自然语言查询** | 用自然语言查询票价、时长、影院、观影频率等问题，并生成 SQL。 |
| **AI 报表** | 输出观影统计、偏好分析和可视化报表。 |
| **飞书扩展** | 通过 Langbot 配置接入飞书会话入口。 |

## Tech Stack

- **Workflow**: Dify Workflow for multimodal ticket extraction
- **Backend**: FastAPI, Python
- **Database**: MySQL
- **Agent Query**: Natural-language-to-SQL workflow
- **Integration**: Optional Langbot / Feishu
- **Deployment**: Docker Compose

## Quick Start

```bash
git clone https://github.com/m4rklee/movie_tickets_assistant.git
cd movie_tickets_assistant
```

启动数据库和服务：

```bash
docker compose up -d
```

`ticket-api/.env.example` 提供后端环境变量模板。首次使用前请根据本地 MySQL、Dify Workflow 和模型服务配置 `.env`。

## Usage

导入数据库结构：

```bash
mysql -u root -p < sql/schema.sql
```

票据识别 workflow 可参考：

```text
digital_movie_ticket.yml
workflow/
```

详细产品、字段和迭代说明见：

```text
docs/PRD.md
docs/data-dictionary.md
docs/v3-qa-reports.md
```

## Project Structure

```text
ticket-api/              # FastAPI ticket service
workflow/                # Dify workflow and prompts
langbot/                 # Feishu/Langbot example config
docs/                    # PRD, workflow design, screenshots, data dictionary
eval/                    # Evaluation scripts and baseline metrics
sql/                     # Database schema and migrations
my_backend/              # Earlier backend prototype
```

## Notes

- 票据识别结果依赖图片质量、模型能力和字段校验策略。
- 项目用于个人票据管理和作品展示，不涉及真实购票或影院系统接口。
- 上传真实票据时应注意遮盖订单号、二维码、手机号等敏感信息。

## Roadmap

- Add a public web demo.
- Improve field-level confidence scoring.
- Add dashboard pages for long-term viewing statistics.
- Expand evaluation dataset for paper tickets and low-quality images.
