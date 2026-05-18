from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class DraftCreate(BaseModel):
    ticket_type: Literal["electronic", "paper"]
    extract_json: dict[str, Any]
    image_path: str | None = None


class DraftResponse(BaseModel):
    draft_id: int
    ticket_type: str
    extract_json: dict[str, Any]
    image_path: str | None
    expires_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConfirmRequest(BaseModel):
    draft_id: int
    corrected_json: dict[str, Any] | None = None


class ConfirmResponse(BaseModel):
    ticket_id: int
    duplicate_warning: bool
    summary: str


class TicketResponse(BaseModel):
    id: int
    ticket_type: str
    movie_title: str
    show_date: date
    show_time: str | None
    cinema_name: str | None
    cinema_address: str | None
    hall_name: str | None
    seat_info: str | None
    price: float | None
    payment_status: str | None
    image_path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int


class ReportSummary(BaseModel):
    total_tickets: int
    total_spend: float
    unique_movies: int
    by_month: list[dict[str, Any]]
    top_halls: list[dict[str, Any]]
    movie_list: list[dict[str, Any]]
