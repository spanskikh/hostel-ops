from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from hostel_ops.cegis import process_checkin_note
from hostel_ops.contracts import CheckInEventProposal
from hostel_ops.storage import HostelClusterStore
from hostel_ops.verifier import verify_checkin_event

mcp = FastMCP("hostel-ops-ledger")


@mcp.tool()
def audit_hostel_checkin(event_json: dict[str, Any]) -> dict[str, Any]:
    """Проверяет событие заезда и проводки тройной записи через Z3 + состояние БД на rhino."""
    event = CheckInEventProposal.model_validate(event_json)
    store = HostelClusterStore()
    store.init_schemas()
    _, bookings = store.fetch_bed_state_and_bookings(event.bed_id)
    verdict = verify_checkin_event(event, bookings)
    vol = verdict.total_volume_cents
    store.log_audit(event.event_id, event.bed_id, verdict.status, vol, len(verdict.violations))
    return verdict.model_dump()


@mcp.tool()
async def ingest_operator_checkin_note(note: str, bed_id: str) -> dict[str, Any]:
    """Парсит заметку администратора, верифицирует в Z3 и фиксирует в PostgreSQL на rhino."""
    store = HostelClusterStore()
    store.init_schemas()
    state, bookings = store.fetch_bed_state_and_bookings(bed_id)
    res = await process_checkin_note(note, bed_id, state, bookings)
    if res.converged and res.event and res.verdict:
        store.commit_verified_checkin(res.event)
        vol = res.verdict.total_volume_cents
        store.log_audit(res.event.event_id, bed_id, "SAT", vol, 0)
    return {
        "converged": res.converged,
        "iterations": res.iterations,
        "verdict": res.verdict.model_dump() if res.verdict else None,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
