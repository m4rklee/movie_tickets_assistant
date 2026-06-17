# 中国电影资料馆票据管理助手

> 一个面向影迷的票据管理工具

中国电影资料馆智能票据助手是一个面向影迷的票据管理工具。项目通过多模态识别、结构化入库、自然语言查询和报表生成，将电子票、纸质票中分散的观影信息沉淀为可检索、可分析的个人观影数据库。

## 项目功能

- **票据管理工作流**: 使用 Dify 搭建工作流，包含票据识别、票据信息入库、数据库信息查询、图表生成等。
- **结构化票据存储**: 后端校验票据字段并写入 MySQL。
- **票据信息查询**: 基于 SQL 查询工具的智能体支持自然语言检索观影记录。
- **历史图表生成**: 基于观影历史生成统计分析、图表和观影总结。
- **接入飞书机器人**: 基于Langbot框架实现飞书机器人接入。

## 项目演示

### 票据识别：

<img src="docs/pics/ticket_recognition.png" width="720" alt="票据识别：上传图片后结构化入库" />

### 票据样例：

| 电子票截图 | 纸质票 |
|---|---|
| <img src="docs/pics/digital_ticket.jpeg" width="360" alt="电子票样例" /> | <img src="docs/pics/paper_ticket.jpeg" width="360" alt="纸质票样例" /> |

### 自然语言查询：

<img src="docs/pics/sql_movie_search.png" width="720" alt="数据查询：自然语言转 SQL 查询票夹" />

### AI 报表：

<img src="docs/pics/ai_report.png" width="720" alt="报表生成：对话与查询过程" />

<img src="docs/pics/ai_report_chart.png" width="720" alt="报表生成：Agent 查询数据并输出图表" />

## 项目流程

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

## 技术栈

- **工作流**: Dify
- **后端**: FastAPI, Python
- **数据库**: MySQL
- **部署**: Docker

## 快速启动

```bash
git clone https://github.com/m4rklee/movie_tickets_assistant.git
cd movie_tickets_assistant
```

启动数据库和服务：

```bash
docker compose up -d
```

`ticket-api/.env.example` 提供后端环境变量模板。首次使用前请根据本地 MySQL、Dify Workflow 和模型服务配置 `.env`。

## 项目结构

```text
ticket-api/              # 后端
workflow/                # Dify工作流
langbot/                 # Langbot框架，接入飞书机器人
```
