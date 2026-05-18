"""
Dify 代码节点：生成 ParseTicket 给用户确认的 Markdown。
输入：extract_json, draft_id
"""

import json


def main(extract_json: dict, draft_id: int) -> dict:
    rows = []
    for k, v in extract_json.items():
        if k in ("confidence", "missing_fields"):
            continue
        rows.append(f"| {k} | {v} |")

    missing = extract_json.get("missing_fields") or []
    md = "## 识别结果（请核对）\n\n| 字段 | 值 |\n|------|-----|\n"
    md += "\n".join(rows)
    md += f"\n\n- **draft_id**：{draft_id}\n"
    md += f"- **缺失字段**：{', '.join(missing) if missing else '无'}\n\n"
    md += "确认后请运行 **ConfirmTicket**，传入 `draft_id`；若有修正请填写 `corrected_json`。\n"
    return {"markdown": md, "draft_id": draft_id, "extract_json_str": json.dumps(extract_json, ensure_ascii=False)}
