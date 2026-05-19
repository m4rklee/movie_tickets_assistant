"""
Dify 代码节点：将 /save_movie_tickets 的 JSON 响应转为用户可读回复。
输入：http_body（HTTP 请求节点的 body）
输出：result（字符串，接 Answer 节点）
"""

import json


FIELD_LABELS = [
    ("movie_name", "电影名称"),
    ("ticket_date", "观看日期"),
    ("start_time", "开始时间"),
    ("end_time", "结束时间"),
    ("movie_duration", "影片时长(分钟)"),
    ("price", "票价"),
    ("cinema_name", "影院"),
    ("cinema_address", "影院地址"),
    ("cinema_hall", "影厅"),
    ("seat_row", "座位排"),
    ("seat_col", "座位号"),
]


def _parse_body(http_body) -> dict:
    if isinstance(http_body, dict):
        return http_body
    text = (http_body or "").strip()
    if not text:
        return {}
    return json.loads(text)


def main(http_body: str) -> dict:
    data = _parse_body(http_body)
    reply = data.get("reply_text")
    if reply:
        return {"result": reply}
    return {"result": data.get("message", "入库完成，但未返回字段详情。")}
