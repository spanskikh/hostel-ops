from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import ValidationError

from hostel_ops.contracts import (
    CheckInEventProposal,
    ExistingBooking,
    HostelAuditVerdict,
    RoomCleanState,
)
from hostel_ops.storage import HostelClusterStore
from hostel_ops.verifier import verify_checkin_event

DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
DEFAULT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5-coder:7b")


@dataclass(frozen=True)
class HostelCegisResult:
    converged: bool
    iterations: int
    verdict: HostelAuditVerdict | None
    event: CheckInEventProposal | None


async def _parse_operator_note(
    client: httpx.AsyncClient,
    ollama_url: str,
    model: str,
    note: str,
    bed_id: str,
    room_status: RoomCleanState,
    feedback: list[str],
    seed: int = 42,
) -> CheckInEventProposal:
    system_prompt = (
        "You are a hostel accounting compiler. Convert the operator note into JSON "
        "CheckInEventProposal. Use exact bed_id and room_status provided. "
        "Triple-entry invariant: sum of ledger_legs[*].amount_cents MUST equal 0 "
        "(e.g. CASH_REGISTER +12000 and ACCOMMODATION_REVENUE -12000)."
    )
    user_prompt = (
        f"Operator note: {note}\n"
        f"Verified bed_id: {bed_id}\n"
        f"Verified room_status: {room_status}\n"
    )
    if feedback:
        joined = "\n".join(f"- Iter {i + 1}: {msg}" for i, msg in enumerate(feedback))
        user_prompt += f"\nZ3 Counterexamples to fix:\n{joined}\n"

    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "format": CheckInEventProposal.model_json_schema(),
        "options": {"temperature": 0.0, "seed": seed, "num_ctx": 4096},
    }
    resp = await client.post(f"{ollama_url}/api/chat", json=payload, timeout=120.0)
    resp.raise_for_status()
    return CheckInEventProposal.model_validate_json(resp.json()["message"]["content"])


async def process_checkin_note(
    note: str,
    bed_id: str,
    room_status: RoomCleanState,
    existing_bookings: list[ExistingBooking],
    max_iters: int = 3,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    model: str = DEFAULT_MODEL,
    transport: httpx.AsyncBaseTransport | None = None,
) -> HostelCegisResult:
    feedback: list[str] = []
    last_verdict: HostelAuditVerdict | None = None
    last_event: CheckInEventProposal | None = None

    async with httpx.AsyncClient(transport=transport) as client:
        for step in range(max_iters):
            try:
                event = await _parse_operator_note(
                    client=client,
                    ollama_url=ollama_url,
                    model=model,
                    note=note,
                    bed_id=bed_id,
                    room_status=room_status,
                    feedback=feedback,
                    seed=42 + step,
                )
            except (ValidationError, json.JSONDecodeError, KeyError) as exc:
                feedback.append(f"Schema error: {exc}")
                continue

            last_event = event
            verdict = verify_checkin_event(event, existing_bookings)
            last_verdict = verdict

            if verdict.status == "SAT":
                return HostelCegisResult(
                    converged=True,
                    iterations=step + 1,
                    verdict=verdict,
                    event=event,
                )
            feedback.append("; ".join(verdict.violations))

    return HostelCegisResult(
        converged=False,
        iterations=max_iters,
        verdict=last_verdict,
        event=last_event,
    )


async def _smoke_demo() -> None:
    store = HostelClusterStore()
    store.init_schemas()
    store.upsert_bed("B-101-1", "R101", "CLEAN")

    state, bookings = store.fetch_bed_state_and_bookings("B-101-1")
    note = (
        "Event evt_2026_11_22: Check-in 'Markus Weber' to bed B-101-1 days 326..329. "
        "Paid 135.00 EUR (13500 cents) via CASH_REGISTER."
    )
    res = await process_checkin_note(note, "B-101-1", state, bookings, max_iters=3)
    print(f"CEGIS Converged: {res.converged} in {res.iterations} iter(s)")
    if res.converged and res.event and res.verdict:
        store.commit_verified_checkin(res.event)
        vol = res.verdict.total_volume_cents
        store.log_audit(res.event.event_id, res.event.bed_id, "SAT", vol, 0)
        new_state, _ = store.fetch_bed_state_and_bookings("B-101-1")
        print(f"  Committed to rhino PostgreSQL! Bed state transitioned: {state} -> {new_state}")


if __name__ == "__main__":
    asyncio.run(_smoke_demo())
