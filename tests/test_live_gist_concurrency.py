from __future__ import annotations

import asyncio
import os
import threading
import uuid
from pathlib import Path

import psycopg
import pytest

from hostel_ops.contracts import CheckInEventProposal, LedgerLeg
from hostel_ops.storage import HostelClusterStore

LIVE_PG_DSN = os.getenv(
    "HOSTEL_PG_DSN",
    "postgresql://dev:devpass@127.0.0.1:15432/hostel_ops",
)


def _make_proposal(
    event_id: str, bed_id: str, check_in: int, check_out: int
) -> CheckInEventProposal:
    return CheckInEventProposal(
        event_id=event_id,
        guest_name=f"Guest-{event_id}",
        bed_id=bed_id,
        check_in_day=check_in,
        check_out_day=check_out,
        room_status="CLEAN",
        ledger_legs=[
            LedgerLeg(account="CASH_REGISTER", amount_cents=5000, memo="Deposit"),
            LedgerLeg(account="ACCOMMODATION_REVENUE", amount_cents=-5000, memo="Stay"),
        ],
    )


@pytest.mark.integration
async def test_concurrent_overlapping_bookings_enforced_by_rhino_gist(tmp_path: Path) -> None:
    store = HostelClusterStore(pg_dsn=LIVE_PG_DSN, duck_path=tmp_path / "race.duckdb")
    store.init_schemas()

    suffix = uuid.uuid4().hex[:8]
    bed_id = f"B-RACE-{suffix}"
    ev_a = f"EV-A-{suffix}"
    ev_b = f"EV-B-{suffix}"

    store.upsert_bed(bed_id=bed_id, room_code="R-101", clean_state="CLEAN")
    barrier = threading.Barrier(2)

    def _race_commit(event: CheckInEventProposal) -> str:
        barrier.wait(timeout=5.0)
        store.commit_verified_checkin(event)
        return event.event_id

    try:
        results = await asyncio.gather(
            asyncio.to_thread(_race_commit, _make_proposal(ev_a, bed_id, 10, 14)),
            asyncio.to_thread(_race_commit, _make_proposal(ev_b, bed_id, 12, 16)),
            return_exceptions=True,
        )

        successes = [r for r in results if isinstance(r, str)]
        excl_errors = [r for r in results if isinstance(r, psycopg.errors.ExclusionViolation)]

        assert len(successes) == 1, f"Expected exactly 1 winner, got: {results}"
        assert len(excl_errors) == 1, f"Expected 1 ExclusionViolation, got: {results}"

        winner = successes[0]
        state, bookings = store.fetch_bed_state_and_bookings(bed_id)
        assert state == "DIRTY"
        assert len(bookings) == 1
        assert bookings[0].booking_id == winner

        with psycopg.connect(LIVE_PG_DSN) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM triple_ledger WHERE event_id IN (%s, %s);",
                (ev_a, ev_b),
            ).fetchone()
            assert row is not None and int(row[0]) == 2
    finally:
        with psycopg.connect(LIVE_PG_DSN, autocommit=True) as conn:
            conn.execute("DELETE FROM triple_ledger WHERE event_id IN (%s, %s);", (ev_a, ev_b))
            conn.execute("DELETE FROM bookings WHERE bed_id = %s;", (bed_id,))
            conn.execute("DELETE FROM beds WHERE bed_id = %s;", (bed_id,))
