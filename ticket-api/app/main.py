from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.schemas import (
    ConfirmRequest,
    ConfirmResponse,
    DraftCreate,
    DraftResponse,
    ReportSummary,
    TicketListResponse,
    TicketResponse,
)
from app.services import (
    build_summary,
    confirm_ticket,
    create_draft,
    format_summary,
    get_draft,
    list_tickets,
    ticket_to_response,
)

app = FastAPI(title="FilmArchive Ticket API", version="0.1.0")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


def verify_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    if not settings.ticket_api_key:
        return
    if x_api_key != settings.ticket_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/drafts", response_model=DraftResponse, dependencies=[Depends(verify_api_key)])
def post_draft(body: DraftCreate, db: Session = Depends(get_db)) -> Any:
    draft = create_draft(db, body.ticket_type, body.extract_json, body.image_path)
    return DraftResponse(
        draft_id=draft.id,
        ticket_type=draft.ticket_type,
        extract_json=draft.extract_json,
        image_path=draft.image_path,
        expires_at=draft.expires_at,
        created_at=draft.created_at,
    )


@app.get("/api/drafts/{draft_id}", response_model=DraftResponse, dependencies=[Depends(verify_api_key)])
def get_draft_endpoint(draft_id: int, db: Session = Depends(get_db)) -> Any:
    draft = get_draft(db, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return DraftResponse(
        draft_id=draft.id,
        ticket_type=draft.ticket_type,
        extract_json=draft.extract_json,
        image_path=draft.image_path,
        expires_at=draft.expires_at,
        created_at=draft.created_at,
    )


@app.post("/api/tickets/confirm", response_model=ConfirmResponse, dependencies=[Depends(verify_api_key)])
def post_confirm(body: ConfirmRequest, db: Session = Depends(get_db)) -> ConfirmResponse:
    try:
        ticket, duplicate_warning = confirm_ticket(db, body.draft_id, body.corrected_json)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return ConfirmResponse(
        ticket_id=ticket.id,
        duplicate_warning=duplicate_warning,
        summary=format_summary(ticket),
    )


@app.get("/api/tickets", response_model=TicketListResponse, dependencies=[Depends(verify_api_key)])
def get_tickets(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    movie_title: str | None = None,
    db: Session = Depends(get_db),
) -> TicketListResponse:
    items, total = list_tickets(db, limit=limit, offset=offset, movie_title=movie_title)
    return TicketListResponse(
        items=[TicketResponse(**ticket_to_response(t)) for t in items],
        total=total,
    )


@app.get("/api/tickets/{ticket_id}", response_model=TicketResponse, dependencies=[Depends(verify_api_key)])
def get_ticket(ticket_id: int, db: Session = Depends(get_db)) -> TicketResponse:
    from app.models import MovieTicket

    ticket = db.get(MovieTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse(**ticket_to_response(ticket))


@app.get("/api/reports/summary", response_model=ReportSummary, dependencies=[Depends(verify_api_key)])
def get_report_summary(
    year: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> ReportSummary:
    data = build_summary(db, year=year)
    return ReportSummary(**data)
