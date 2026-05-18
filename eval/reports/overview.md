# 视觉模型评测总览

- 生成时间：2026-05-18 01:11:23
- 参考 JSON：`movie_ticket_reference.json`
- 计分图片数：19
- 模型输出：`vision_model_eval.jsonl`
- 已排除（不参与计分）：IMG_0017.jpeg

## 排名（核心字段）

核心字段：`movie_name`, `ticket_date`, `start_time`, `price`, `cinema_hall`, `seat_row`, `seat_col`

| 排名 | 模型 | 核心准确率 | 全字段准确率 | 总 Token | 均 Token/次 | 预估费用(¥) | 均费用/次 | 均耗时 | API失败 | 详报 |
|------|------|------------|--------------|----------|-------------|-------------|-----------|--------|---------|------|
| 1 | glm-4.5v | 92.5% | 91.2% | 127,219 | 6,696 | ¥0.6187 | ¥0.0326 | 12.18s | 0 | [glm-4.5v_report.md](glm-4.5v_report.md) |
| 2 | qwen3.6-flash | 91.7% | 91.8% | 89,247 | 4,697 | ¥0.3296 | ¥0.0173 | 14.63s | 0 | [qwen3.6-flash_report.md](qwen3.6-flash_report.md) |
| 3 | qwen3-vl-plus | 91.7% | 91.2% | 54,879 | 2,888 | ¥0.0791 | ¥0.0042 | 6.41s | 0 | [qwen3-vl-plus_report.md](qwen3-vl-plus_report.md) |
| 4 | qwen3-vl-flash | 90.2% | 88.3% | 54,817 | 2,885 | ¥0.0118 | ¥0.0006 | 3.55s | 0 | [qwen3-vl-flash_report.md](qwen3-vl-flash_report.md) |
| 5 | gemini-2.5-flash | 86.5% | 87.1% | 86,071 | 4,530 | ¥0.4625 | ¥0.0243 | 13.36s | 0 | [gemini-2.5-flash_report.md](gemini-2.5-flash_report.md) |
| 6 | gpt-4.1-mini | 78.9% | 74.9% | 30,720 | 1,617 | ¥0.1067 | ¥0.0056 | 6.86s | 0 | [gpt-4.1-mini_report.md](gpt-4.1-mini_report.md) |
| 7 | claude-sonnet-4-5 | 60.2% | 52.6% | 39,398 | 2,074 | ¥1.07 | ¥0.0562 | 16.98s | 0 | [claude-sonnet-4-5_report.md](claude-sonnet-4-5_report.md) |
| 8 | pixtral-large-latest | n/a | n/a | n/a | n/a | n/a | n/a | n/as | 19 | [pixtral-large-latest_report.md](pixtral-large-latest_report.md) |

## Token 与费用汇总

| 模型 | 总输入 Token | 总输出 Token | 总 Token | 均 Token/次 | 预估费用(¥) | 均费用/次 | 总耗时(s) | 均耗时(s) |
|------|-------------|-------------|----------|-------------|-------------|-----------|-----------|-----------|
| glm-4.5v | 119,225 | 7,994 | 127,219 | 6,696 | ¥0.6187 | ¥0.0326 | 231.3 | 12.18 |
| qwen3.6-flash | 52,155 | 37,092 | 89,247 | 4,697 | ¥0.3296 | ¥0.0173 | 278.0 | 14.63 |
| qwen3-vl-plus | 52,193 | 2,686 | 54,879 | 2,888 | ¥0.0791 | ¥0.0042 | 121.8 | 6.41 |
| qwen3-vl-flash | 52,193 | 2,624 | 54,817 | 2,885 | ¥0.0118 | ¥0.0006 | 67.5 | 3.55 |
| gemini-2.5-flash | 68,609 | 17,462 | 86,071 | 4,530 | ¥0.4625 | ¥0.0243 | 253.8 | 13.36 |
| gpt-4.1-mini | 28,614 | 2,106 | 30,720 | 1,617 | ¥0.1067 | ¥0.0056 | 130.4 | 6.86 |
| claude-sonnet-4-5 | 36,898 | 2,500 | 39,398 | 2,074 | ¥1.07 | ¥0.0562 | 322.5 | 16.98 |
| pixtral-large-latest | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
