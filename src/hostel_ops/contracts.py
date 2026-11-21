from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

RoomCleanState = Literal["CLEAN", "DIRTY", "MAINTENANCE"]
AccountType = Literal["CASH_REGISTER", "BANK_TRANSFER", "GUEST_RECEIVABLE", "ACCOMMODATION_REVENUE"]


class LedgerLeg(BaseModel):
    """Проводка тройной записи (сумма всех legs в событии обязана быть равна 0 в центах)."""

    account: AccountType
    amount_cents: int
    memo: str = Field(min_length=1, max_length=128)


class ExistingBooking(BaseModel):
    """Активное бронирование из PostgreSQL (дни представлены как целочисленный ordinal)."""

    booking_id: str
    bed_id: str
    check_in_day: int
    check_out_day: int


class CheckInEventProposal(BaseModel):
    """Структурированное событие заезда и оплаты, извлечённое из заметки администратора."""

    event_id: str = Field(min_length=1, max_length=64)
    guest_name: str = Field(min_length=1, max_length=128)
    bed_id: str = Field(min_length=1, max_length=32)
    check_in_day: int = Field(ge=1)
    check_out_day: int = Field(ge=2)
    room_status: RoomCleanState
    ledger_legs: list[LedgerLeg] = Field(min_length=2, max_length=8)


class HostelAuditVerdict(BaseModel):
    """Вердикт Z3 по инвариантам бухгалтерии, овербукинга и состояния уборки."""

    status: Literal["SAT", "UNSAT"]
    event_id: str
    total_volume_cents: int
    violations: list[str] = Field(default_factory=list)
