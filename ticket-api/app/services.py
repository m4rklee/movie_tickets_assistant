from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models import MovieTicket, TicketDraft


def parse_show_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    s = str(value).strip()[:10]
    return date.fromisoformat(s)


def parse_show_time(value: Any) -> time | None:
    if value is None:
        return None
    if isinstance(value, time):
        return value
    m = re.match(r"(\d{1,2}):(\d{2})", str(value).strip())
    if not m:
        return None
    return time(int(m.group(1)), int(m.group(2)))


def parse_price(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value)).quantize(Decimal("0.01"))
    s = re.sub(r"[^\d.]", "", str(value))
    if not s:
        return None
    return Decimal(s).quantize(Decimal("0.01"))


def create_draft(db: Session, ticket_type: str, extract_json: dict, image_path: str | None) -> TicketDraft:
    expires = datetime.utcnow() + timedelta(days=settings.draft_ttl_days)
    draft = TicketDraft(
        ticket_type=ticket_type,
        extract_json=extract_json,
        image_path=image_path,
        expires_at=expires,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


def get_draft(db: Session, draft_id: int) -> TicketDraft | None:
    return db.get(TicketDraft, draft_id)


def extract_to_ticket_fields(ticket_type: str, data: dict[str, Any]) -> dict[str, Any]:
    movie_title = (data.get("movie_title") or "").strip()
    if not movie_title:
        raise ValueError("movie_title is required")

    fields: dict[str, Any] = {
        "ticket_type": ticket_type,
        "movie_title": movie_title,
        "show_date": parse_show_date(data["show_date"]),
        "hall_name": data.get("hall_name"),
        "price": parse_price(data.get("price")),
        "raw_extract_json": data,
    }

    if ticket_type == "electronic":
        fields["show_time"] = parse_show_time(data.get("show_time"))
        fields["cinema_name"] = data.get("cinema_name")
        fields["payment_status"] = data.get("payment_status")
        fields["cinema_address"] = data.get("cinema_address")
        fields["seat_info"] = None
    else:
        fields["show_time"] = None
        fields["cinema_address"] = data.get("cinema_address")
        fields["cinema_name"] = data.get("cinema_name")
        fields["seat_info"] = data.get("seat_info")
        fields["payment_status"] = None

    return fields


def find_duplicate(db: Session, fields: dict[str, Any]) -> MovieTicket | None:
    stmt = select(MovieTicket).where(
        MovieTicket.ticket_type == fields["ticket_type"],
        MovieTicket.movie_title == fields["movie_title"],
        MovieTicket.show_date == fields["show_date"],
        MovieTicket.hall_name == fields.get("hall_name"),
        MovieTicket.seat_info == fields.get("seat_info"),
        MovieTicket.show_time == fields.get("show_time"),
    )
    return db.execute(stmt).scalar_one_or_none()


def confirm_ticket(
    db: Session, draft_id: int, corrected_json: dict | None, image_path: str | None = None
) -> tuple[MovieTicket, bool]:
    draft = get_draft(db, draft_id)
    if not draft:
        raise LookupError(f"draft {draft_id} not found")

    payload = corrected_json if corrected_json else draft.extract_json
    fields = extract_to_ticket_fields(draft.ticket_type, payload)
    duplicate = find_duplicate(db, fields)
    duplicate_warning = duplicate is not None

    ticket = MovieTicket(
        **fields,
        image_path=image_path or draft.image_path,
        confirm_status="confirmed",
    )
    db.add(ticket)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if duplicate:
            return duplicate, True
        raise
    db.refresh(ticket)
    return ticket, duplicate_warning


def list_tickets(
    db: Session, limit: int = 50, offset: int = 0, movie_title: str | None = None
) -> tuple[list[MovieTicket], int]:
    stmt = select(MovieTicket)
    count_stmt = select(func.count()).select_from(MovieTicket)
    if movie_title:
        pattern = f"%{movie_title}%"
        stmt = stmt.where(MovieTicket.movie_title.like(pattern))
        count_stmt = count_stmt.where(MovieTicket.movie_title.like(pattern))
    stmt = stmt.order_by(MovieTicket.show_date.desc(), MovieTicket.id.desc()).limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())
    total = db.execute(count_stmt).scalar_one()
    return items, total


def build_summary(db: Session, year: int | None = None) -> dict[str, Any]:
    stmt = select(MovieTicket)
    if year:
        stmt = stmt.where(func.year(MovieTicket.show_date) == year)
    tickets = list(db.execute(stmt).scalars().all())

    total_spend = sum(float(t.price or 0) for t in tickets)
    movies = {t.movie_title for t in tickets}

    by_month: dict[str, dict[str, Any]] = {}
    hall_counts: dict[str, int] = {}
    for t in tickets:
        key = t.show_date.strftime("%Y-%m")
        bucket = by_month.setdefault(key, {"month": key, "count": 0, "spend": 0.0})
        bucket["count"] += 1
        bucket["spend"] += float(t.price or 0)
        if t.hall_name:
            hall_counts[t.hall_name] = hall_counts.get(t.hall_name, 0) + 1

    top_halls = sorted(
        [{"hall_name": k, "count": v} for k, v in hall_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:5]

    movie_list = sorted(
        [
            {
                "movie_title": t.movie_title,
                "show_date": t.show_date.isoformat(),
                "hall_name": t.hall_name,
                "price": float(t.price) if t.price else None,
            }
            for t in tickets
        ],
        key=lambda x: x["show_date"],
        reverse=True,
    )

    return {
        "total_tickets": len(tickets),
        "total_spend": round(total_spend, 2),
        "unique_movies": len(movies),
        "by_month": sorted(by_month.values(), key=lambda x: x["month"], reverse=True),
        "top_halls": top_halls,
        "movie_list": movie_list,
    }


def ticket_to_response(t: MovieTicket) -> dict[str, Any]:
    return {
        "id": t.id,
        "ticket_type": t.ticket_type,
        "movie_title": t.movie_title,
        "show_date": t.show_date,
        "show_time": t.show_time.strftime("%H:%M") if t.show_time else None,
        "cinema_name": t.cinema_name,
        "cinema_address": t.cinema_address,
        "hall_name": t.hall_name,
        "seat_info": t.seat_info,
        "price": float(t.price) if t.price is not None else None,
        "payment_status": t.payment_status,
        "image_path": t.image_path,
        "created_at": t.created_at,
    }


def format_summary(ticket: MovieTicket) -> str:
    parts = [
        f"《{ticket.movie_title}》",
        ticket.show_date.isoformat(),
    ]
    if ticket.show_time:
        parts.append(ticket.show_time.strftime("%H:%M"))
    if ticket.hall_name:
        parts.append(ticket.hall_name)
    if ticket.seat_info:
        parts.append(ticket.seat_info)
    if ticket.price is not None:
        parts.append(f"¥{ticket.price}")
    return " · ".join(parts)
