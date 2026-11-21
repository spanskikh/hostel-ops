from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from hostel_ops.contracts import CheckInEventProposal, ExistingBooking, LedgerLeg
from hostel_ops.verifier import verify_checkin_event


def test_blocks_dirty_room_overbooking_and_imbalance() -> None:
    bad_event = CheckInEventProposal(
        event_id="evt_bad",
        guest_name="Test Guest",
        bed_id="B-101-1",
        check_in_day=10,
        check_out_day=14,
        room_status="DIRTY",
        ledger_legs=[
            LedgerLeg(account="CASH_REGISTER", amount_cents=10000, memo="Cash"),
            LedgerLeg(account="ACCOMMODATION_REVENUE", amount_cents=-9500, memo="Short by 5 EUR"),
        ],
    )
    existing = [
        ExistingBooking(booking_id="b_prev", bed_id="B-101-1", check_in_day=12, check_out_day=15)
    ]
    verdict = verify_checkin_event(bad_event, existing)
    assert verdict.status == "UNSAT"
    assert any("imbalance" in v for v in verdict.violations)
    assert any("DIRTY" in v for v in verdict.violations)
    assert any("Overbooking" in v for v in verdict.violations)


@settings(max_examples=80, deadline=None)
@given(
    amount=st.integers(min_value=100, max_value=100_000),
    new_ci=st.integers(min_value=1, max_value=20),
    stay_len=st.integers(min_value=1, max_value=7),
)
def test_property_z3_enforces_disjoint_intervals_and_zero_sum(
    amount: int, new_ci: int, stay_len: int
) -> None:
    new_co = new_ci + stay_len
    existing = [
        ExistingBooking(booking_id="b_locked", bed_id="B-1", check_in_day=10, check_out_day=15)
    ]
    event = CheckInEventProposal(
        event_id="evt_prop",
        guest_name="Guest",
        bed_id="B-1",
        check_in_day=new_ci,
        check_out_day=new_co,
        room_status="CLEAN",
        ledger_legs=[
            LedgerLeg(account="CASH_REGISTER", amount_cents=amount, memo="Debit"),
            LedgerLeg(account="ACCOMMODATION_REVENUE", amount_cents=-amount, memo="Credit"),
        ],
    )
    verdict = verify_checkin_event(event, existing)
    disjoint = (new_co <= 10) or (new_ci >= 15)
    assert (verdict.status == "SAT") is disjoint
