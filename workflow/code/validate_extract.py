"""
Dify 代码节点：解析并校验 Vision LLM 输出的 JSON。
输入变量：llm_text (str), ticket_type (str)
输出变量：extract_json (object), valid (bool), error_message (str)
"""

import json
import re


def main(llm_text: str, ticket_type: str) -> dict:
    text = (llm_text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return {"extract_json": {}, "valid": False, "error_message": f"JSON 解析失败: {e}"}

    required = {
        "electronic": ["movie_title", "show_date", "show_time", "cinema_name", "hall_name", "payment_status", "price"],
        "paper": ["movie_title", "show_date", "cinema_address", "hall_name", "seat_info", "price"],
    }
    keys = required.get(ticket_type, [])
    missing = [k for k in keys if data.get(k) is None and k not in (data.get("missing_fields") or [])]

    if not data.get("movie_title"):
        return {"extract_json": data, "valid": False, "error_message": "movie_title 不能为空"}

    if "confidence" not in data:
        data["confidence"] = {}
    if "missing_fields" not in data:
        data["missing_fields"] = missing

    return {"extract_json": data, "valid": True, "error_message": ""}
