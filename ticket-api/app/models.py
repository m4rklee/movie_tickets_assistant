from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import JSON, Date, DateTime, Enum, Numeric, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TicketDraft(Base):
    __tablename__ = "ticket_drafts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_type: Mapped[str] = mapped_column(Enum("electronic", "paper", name="draft_ticket_type"))
    extract_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    image_path: Mapped[str | None] = mapped_column(String(500))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class MovieTicket(Base):
    __tablename__ = "movie_tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_type: Mapped[str] = mapped_column(Enum("electronic", "paper", name="ticket_type_enum"))
    movie_title: Mapped[str] = mapped_column(String(200))
    show_date: Mapped[date] = mapped_column(Date)
    show_time: Mapped[time | None] = mapped_column(Time)
    cinema_name: Mapped[str | None] = mapped_column(String(200))
    cinema_address: Mapped[str | None] = mapped_column(String(500))
    hall_name: Mapped[str | None] = mapped_column(String(100))
    seat_info: Mapped[str | None] = mapped_column(String(50))
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    payment_status: Mapped[str | None] = mapped_column(String(50))
    image_path: Mapped[str | None] = mapped_column(String(500))
    raw_extract_json: Mapped[dict | None] = mapped_column(JSON)
    confirm_status: Mapped[str] = mapped_column(
        Enum("pending", "confirmed", name="confirm_status_enum"), default="confirmed"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
