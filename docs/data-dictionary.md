# 数据字典与 API 契约

## 1. 票种枚举 `ticket_type`

| 值 | 说明 |
|----|------|
| `electronic` | 电子票截图 |
| `paper` | 纸质票拍照 |

## 2. 表 `movie_tickets`

| 字段 | 类型 | 电子票 | 纸质票 | 说明 |
|------|------|--------|--------|------|
| id | BIGINT | ✓ | ✓ | 主键 |
| ticket_type | ENUM | ✓ | ✓ | electronic / paper |
| movie_title | VARCHAR(200) | ✓ | ✓ | 电影名称 |
| show_date | DATE | ✓ | ✓ | YYYY-MM-DD |
| show_time | TIME | ✓ | — | HH:MM:SS |
| cinema_name | VARCHAR(200) | ✓ | 可选 | 影院名称 |
| cinema_address | VARCHAR(500) | 可选 | ✓ | 影院地址 |
| hall_name | VARCHAR(100) | ✓ | ✓ | 影厅 |
| seat_info | VARCHAR(50) | — | ✓ | 座位 |
| price | DECIMAL(10,2) | ✓ | ✓ | 元 |
| payment_status | VARCHAR(50) | ✓ | — | 已支付/待支付等 |
| image_path | VARCHAR(500) | ✓ | ✓ | 相对存储路径 |
| raw_extract_json | JSON | ✓ | ✓ | 识别原始 JSON |
| confirm_status | ENUM | ✓ | ✓ | 默认 confirmed |
| created_at | DATETIME | ✓ | ✓ | |
| updated_at | DATETIME | ✓ | ✓ | |

**去重键**：`(ticket_type, movie_title, show_date, hall_name, seat_info, show_time)`

## 3. 表 `ticket_drafts`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | draft_id |
| ticket_type | ENUM | |
| extract_json | JSON | LLM 输出（含 confidence / missing_fields） |
| image_path | VARCHAR(500) | 可选 |
| expires_at | DATETIME | 默认创建后 7 天 |

## 4. 识别 JSON Schema

### 4.1 电子票 `electronic`

```json
{
  "movie_title": "string",
  "show_date": "YYYY-MM-DD",
  "show_time": "HH:MM",
  "cinema_name": "string",
  "hall_name": "string",
  "payment_status": "string",
  "price": 0.0,
  "confidence": {},
  "missing_fields": []
}
```

### 4.2 纸质票 `paper`

```json
{
  "movie_title": "string",
  "show_date": "YYYY-MM-DD",
  "cinema_address": "string",
  "hall_name": "string",
  "seat_info": "string",
  "price": 0.0,
  "confidence": {},
  "missing_fields": []
}
```

## 5. REST API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/drafts` | 创建草稿 |
| GET | `/api/drafts/{id}` | 获取草稿 |
| POST | `/api/tickets/confirm` | 确认入库 |
| GET | `/api/tickets` | 列表（query: `limit`, `offset`, `movie_title`） |
| GET | `/api/tickets/{id}` | 单条 |
| GET | `/api/reports/summary` | v3：聚合报表 |
| GET | `/health` | 健康检查 |

### POST `/api/drafts`

```json
{
  "ticket_type": "electronic",
  "extract_json": { },
  "image_path": "uploads/xxx.jpg"
}
```

响应：`{ "draft_id": 1, "expires_at": "..." }`

### POST `/api/tickets/confirm`

```json
{
  "draft_id": 1,
  "corrected_json": { }
}
```

`corrected_json` 可选；缺省使用草稿内 `extract_json`。

响应：`{ "ticket_id": 1, "duplicate_warning": false, "summary": "..." }`

### 鉴权

Header：`X-API-Key: <TICKET_API_KEY>`（未配置 KEY 时跳过校验，仅本地开发）
