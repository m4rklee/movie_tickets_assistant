# Dify 工作流搭建指南

## 前置

1. Dify ≥ 1.6 已安装并配置视觉模型（GPT-4o / Qwen-VL 等）
2. `docker compose up -d` 启动 ticket-api（`http://localhost:8000`）
3. Dify 在 Docker 内时，API 基址使用 `http://host.docker.internal:8000`

## 应用环境变量

| 变量 | 值 |
|------|-----|
| `TICKET_API_BASE` | `http://host.docker.internal:8000` |
| `TICKET_API_KEY` | `dev-local-key`（与 docker-compose 一致） |

## Workflow A：ParseTicket

1. 新建 **Workflow** 应用，名称 `ParseTicket`
2. **开始节点** 变量：
   - `ticket_type`：下拉选项 `electronic` / `paper`
   - `ticket_image`：文件类型「图片」
3. **IF/ELSE**：条件 `ticket_type` equals `electronic` → 电子票 LLM 分支；否则纸质票分支
4. **LLM 节点**（各分支一个）：
   - 开启 Vision，图片变量 `ticket_image`
   - System Prompt 见 [prompts.md](./prompts.md)
   - temperature `0.2`
5. **代码节点** `validate_extract`：粘贴 [code/validate_extract.py](./code/validate_extract.py)
   - 输入：`llm_text` ← LLM text，`ticket_type` ← 开始节点
   - 若 `valid` 为 false，可接「重试 LLM」分支（最多 1 次，参考 MatchCV v2）
6. **HTTP Request** `POST {{TICKET_API_BASE}}/api/drafts`
   - Headers：`X-API-Key: {{TICKET_API_KEY}}`
   - Body JSON：

```json
{
  "ticket_type": "{{#start.ticket_type#}}",
  "extract_json": {{#validate.extract_json#}},
  "image_path": null
}
```

7. **代码节点** `format_parse_reply`：粘贴 [code/format_parse_reply.py](./code/format_parse_reply.py)
8. **结束节点**：输出 `markdown`

导出 DSL 至 `workflow/exports/parse-ticket.yml`（配置 Key 后从 Dify 导出）。

### 从 Langbot 调用 ParseTicket 的图片格式

Langbot 从飞书收到图片后，需要先拿到图片二进制或公网 URL，再按 Dify 文件输入格式传给工作流。若先上传到 Dify `/v1/files/upload`，运行工作流时使用：

```json
{
  "inputs": {
    "ticket_type": "electronic",
    "ticket_image": [
      {
        "type": "image",
        "transfer_method": "local_file",
        "upload_file_id": "<DIFY_FILE_ID>"
      }
    ]
  },
  "response_mode": "blocking",
  "user": "feishu-<open_id>"
}
```

若日志中看到后端收到 `{"error":"No image provided."}`，优先检查 Langbot 传给 Dify 的 `ticket_image` 是否是上述文件列表，而不是飞书 `image_key` 或普通字符串。

## Workflow B：ConfirmTicket

1. 新建 Workflow `ConfirmTicket`
2. **开始节点**：
   - `draft_id`：数字
   - `corrected_json`：段落文本，**非必填**
3. **代码节点** `merge_confirm`：粘贴 [code/merge_confirm.py](./code/merge_confirm.py)
4. **HTTP Request** `POST {{TICKET_API_BASE}}/api/tickets/confirm`
   - Body：`{{#merge_confirm.body_json#}}`（或结构化 Body 引用 `body` 对象）
   - Headers：同上
5. **结束节点** 模板：

```
已入票夹 #{{ticket_id}}
{{summary}}
{{#if duplicate_warning}}⚠️ 检测到可能重复记录{{/if}}
```

导出至 `workflow/exports/confirm-ticket.yml`。

## 联调检查清单

- [ ] `GET http://localhost:8000/health` 返回 ok
- [ ] ParseTicket 上传测试图 → 返回 draft_id
- [ ] ConfirmTicket 传入 draft_id → 返回 ticket_id
- [ ] `GET http://localhost:8000/api/tickets` 可见记录

## HTTP 节点示例（Confirm）

- URL：`{{#env.TICKET_API_BASE#}}/api/tickets/confirm`
- Method：POST
- Header：`X-API-Key` = `{{#env.TICKET_API_KEY#}}`
- Body type：JSON
