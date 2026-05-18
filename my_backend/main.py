import json
import re
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from sqlalchemy import create_engine, text as sql_text

app = FastAPI()

DATABASE_URL = "mysql+pymysql://root:xiaopang123,.@127.0.0.1:3306/my_movie_tickets?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

def parse_tickets_from_request_data(data: Any) -> list[dict[str, Any]]:

    """

    兼容三种情况：

    1. Dify 直接传数组：

       [

         {"movie_name": "..."},

         {"movie_name": "..."}

       ]

    2. Dify 直接传单个对象：

       {

         "movie_name": "..."

       }

    3. Dify 传 {"text": "```json ... ```"}：

       {

         "text": "```json\n[...]\n```"

       }

    4. Dify 传 {"text": "[...]"}：

       {

         "text": "[{\"movie_name\": \"...\"}]"

       }

    """

    # 情况1：Dify 已经直接传来了 list

    if isinstance(data, list):

        tickets = data

    # 情况2：Dify 直接传来了单个 ticket 对象

    elif isinstance(data, dict) and "movie_name" in data:

        tickets = [data]

    # 情况3：Dify 传来了 {"text": "..."}

    elif isinstance(data, dict) and "text" in data:

        raw_text = data["text"]

        if not isinstance(raw_text, str):

            raise ValueError("text 字段必须是字符串")

        content = raw_text.strip()

        # 提取 ```json ... ``` 中间的内容

        match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.S)

        if match:

            json_text = match.group(1).strip()

        else:

            json_text = content

        try:

            tickets = json.loads(json_text)

            if isinstance(tickets, dict) and "movie_name" in tickets:

                tickets = [tickets]

        except json.JSONDecodeError as e:

            raise ValueError(f"text 字段中的 JSON 解析失败: {str(e)}")

    else:

        raise ValueError("请求体格式错误：期望 JSON 数组、单个电影票对象，或包含 text 字段的对象")

    if not isinstance(tickets, list):

        raise ValueError("解析结果不是列表，期望格式是 [{...}, {...}]")

    for index, item in enumerate(tickets):

        if not isinstance(item, dict):

            raise ValueError(f"第 {index + 1} 条数据不是对象")

    return tickets


def normalize_int(value: Any) -> int | None:
    if value is None or value == "":
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float) and value.is_integer():
        return int(value)

    text = str(value).strip()
    if text.isdigit():
        return int(text)

    match = re.search(r"\d+", text)
    if match:
        return int(match.group(0))

    chinese_digits = {
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
        "十": 10,
    }
    for char, number in chinese_digits.items():
        if char in text:
            return number

    return None

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Dify MySQL backend is running"
    }

@app.post("/save_movie_tickets")

async def save_movie_tickets(request: Request):
    body = await request.body()

    body_text = body.decode("utf-8", errors="ignore")

    print("====== RAW BODY START ======")
    print(body_text)
    try:
        data = json.loads(body_text)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail="请求体不是合法 JSON: {str(e)}")

    try:
        tickets = parse_tickets_from_request_data(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    insert_sql = sql_text("""
        INSERT INTO movie_tickets
        (
            movie_name,
            ticket_date,
            start_time,
            end_time,
            movie_duration,
            price,
            cinema_name,
            cinema_address,
            cinema_hall,
            seat_row,
            seat_col,
            raw_text
        )
        VALUES
        (
            :movie_name,
            :ticket_date,
            :start_time,
            :end_time,
            :movie_duration,
            :price,
            :cinema_name,
            :cinema_address,
            :cinema_hall,
            :seat_row,
            :seat_col,
            :raw_text
        )
    """)
    try:
        with engine.begin() as conn:
            for ticket in tickets:
                conn.execute(insert_sql, {
                    "movie_name": ticket.get("movie_name"),
                    "ticket_date": ticket.get("ticket_date"),
                    "start_time": ticket.get("start_time"),
                    "end_time": ticket.get("end_time"),
                    "movie_duration": ticket.get("movie_duration"),
                    "price": ticket.get("price"),
                    "cinema_name": ticket.get("cinema_name"),
                    "cinema_address": ticket.get("cinema_address"),
                    "cinema_hall": ticket.get("cinema_hall"),
                    "seat_row": normalize_int(ticket.get("seat_row")),
                    "seat_col": normalize_int(ticket.get("seat_col")),
                    "raw_text": json.dumps(data, ensure_ascii=False),
                })
    except Exception as e:
        print("====== DATABASE ERROR START ======")
        print(repr(e))
        print("====== DATABASE ERROR END ======")

        raise HTTPException(
            status_code=500,
            detail=f"数据库写入失败: {repr(e)}"
        )
    return {
        "success": True,
        "saved_count": len(tickets),
        "message": f"成功保存 {len(tickets)} 条电影票信息"
    }

@app.post("/debug")

async def debug_request(request: Request):

    body = await request.body()

    headers = dict(request.headers)

    return {

        "headers": headers,

        "body_raw": body.decode("utf-8", errors="ignore")

    }        
