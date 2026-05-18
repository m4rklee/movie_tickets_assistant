"""Unit tests without database."""

from datetime import date, time
from decimal import Decimal

from app.services import extract_to_ticket_fields, parse_price, parse_show_date, parse_show_time


def test_parse_show_date():
    assert parse_show_date("2026-03-15") == date(2026, 3, 15)


def test_parse_show_time():
    assert parse_show_time("19:30") == time(19, 30)


def test_parse_price():
    assert parse_price("¥45.0") == Decimal("45.00")


def test_extract_electronic():
    data = {
        "movie_title": "花样年华",
        "show_date": "2026-03-15",
        "show_time": "19:30",
        "cinema_name": "中国电影资料馆",
        "hall_name": "1号厅",
        "payment_status": "已支付",
        "price": 45,
    }
    fields = extract_to_ticket_fields("electronic", data)
    assert fields["movie_title"] == "花样年华"
    assert fields["show_time"] == time(19, 30)
    assert fields["payment_status"] == "已支付"
    assert fields["seat_info"] is None


def test_extract_paper():
    data = {
        "movie_title": "四百击",
        "show_date": "2026-03-08",
        "cinema_address": "中国电影资料馆",
        "hall_name": "1号厅",
        "seat_info": "6排12座",
        "price": 30,
    }
    fields = extract_to_ticket_fields("paper", data)
    assert fields["seat_info"] == "6排12座"
    assert fields["show_time"] is None
    assert fields["payment_status"] is None
