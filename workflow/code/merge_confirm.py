"""
Dify 代码节点：合并 Confirm 请求的 corrected_json。
输入：draft_id (number), corrected_json (str, 可选)
输出：body (object) 供 HTTP POST /api/tickets/confirm
"""

import json


def main(draft_id: int, corrected_json: str = "") -> dict:
    body = {"draft_id": int(draft_id)}
    text = (corrected_json or "").strip()
    if text:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if len(lines) > 2 else lines)
        body["corrected_json"] = json.loads(text)
    return {"body": body, "body_json": json.dumps(body, ensure_ascii=False)}
