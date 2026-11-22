# Target: tests/test_mcp_contracts.py
from __future__ import annotations

import json
import os
import sys
import textwrap
from pathlib import Path
from typing import Any

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import CallToolResult, TextContent

REPO_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_TOOLS: dict[str, set[str]] = {
    "audit_hostel_checkin": {"event_json"},
    "ingest_operator_checkin_note": {"note", "bed_id"},
    "mark_bed_cleaned": {"bed_id"},
}

HARNESS_ENTRYPOINT = textwrap.dedent(
    """
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, patch
    from hostel_ops import server
    from hostel_ops.contracts import (
        CheckInEventProposal,
        ExistingBooking,
        HostelAuditVerdict,
        LedgerLeg,
        RoomCleanState,
    )

    class _StubHostelStore:
        def __init__(self) -> None:
            self.audits: list[tuple[str, str, str, int, int]] = []
            self.committed: list[CheckInEventProposal] = []

        def init_schemas(self) -> None:
            return None

        def fetch_bed_state_and_bookings(
            self,
            bed_id: str,
        ) -> tuple[RoomCleanState, list[ExistingBooking]]:
            existing = [
                ExistingBooking(
                    booking_id="bk_existing_101",
                    bed_id=bed_id,
                    check_in_day=10,
                    check_out_day=15,
                )
            ]
            return ("CLEAN", existing)

        def log_audit(
            self,
            event_id: str,
            bed_id: str,
            status: str,
            total_volume_cents: int,
            violation_count: int,
        ) -> None:
            self.audits.append((event_id, bed_id, status, total_volume_cents, violation_count))

        def commit_verified_checkin(self, event: CheckInEventProposal) -> None:
            self.committed.append(event)

        def complete_housekeeping_cleaning(self, bed_id: str) -> str:
            return "CLEAN"

    async def _fake_checkin_cegis(
        note: str,
        bed_id: str,
        state: RoomCleanState,
        bookings: list[ExistingBooking],
    ) -> SimpleNamespace:
        event = CheckInEventProposal(
            event_id="evt_note_201",
            guest_name="Max Mustermann",
            bed_id=bed_id,
            check_in_day=16,
            check_out_day=19,
            room_status="CLEAN",
            ledger_legs=[
                LedgerLeg(account="CASH_REGISTER", amount_cents=15000, memo="Cash check-in"),
                LedgerLeg(
                    account="ACCOMMODATION_REVENUE",
                    amount_cents=-15000,
                    memo="Room revenue",
                ),
            ],
        )
        verdict = HostelAuditVerdict(
            status="SAT",
            event_id=event.event_id,
            total_volume_cents=15000,
            violations=[],
        )
        return SimpleNamespace(converged=True, iterations=1, event=event, verdict=verdict)

    mock_cegis = AsyncMock(side_effect=_fake_checkin_cegis)
    with (
        patch.object(server, "HostelClusterStore", _StubHostelStore),
        patch.object(server, "process_checkin_note", new=mock_cegis),
    ):
        server.mcp.run(transport="stdio")
    """
).strip()


def _extract_payload(result: CallToolResult) -> dict[str, Any]:
    assert not result.is_error, f"Unexpected MCP tool error: {result.content}"
    if isinstance(result.structured_content, dict):
        return result.structured_content
    first = result.content[0]
    assert isinstance(first, TextContent)
    parsed = json.loads(first.text)
    assert isinstance(parsed, dict)
    return parsed


def _server_params() -> StdioServerParameters:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return StdioServerParameters(
        command=sys.executable,
        args=["-c", HARNESS_ENTRYPOINT],
        env=env,
    )


@pytest.mark.asyncio
async def test_stdio_tool_discovery_and_schemas() -> None:
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()

    tools_by_name = {tool.name: tool for tool in listed.tools}
    assert set(tools_by_name) == set(EXPECTED_TOOLS)

    for name, expected_required in EXPECTED_TOOLS.items():
        schema = tools_by_name[name].input_schema
        assert schema.get("type") == "object"
        required = set(schema.get("required", []))
        assert expected_required.issubset(required)


@pytest.mark.asyncio
async def test_stdio_z3_sat_and_unsat_checkin_audits() -> None:
    sat_event = {
        "event_id": "evt_sat_101",
        "guest_name": "Anna Schmidt",
        "bed_id": "BED-A1",
        "check_in_day": 15,
        "check_out_day": 18,
        "room_status": "CLEAN",
        "ledger_legs": [
            {"account": "CASH_REGISTER", "amount_cents": 12000, "memo": "Cash payment"},
            {"account": "ACCOMMODATION_REVENUE", "amount_cents": -12000, "memo": "3 nights stay"},
        ],
    }

    unsat_overbooking_and_unbalanced_event = {
        "event_id": "evt_unsat_102",
        "guest_name": "Klaus Weber",
        "bed_id": "BED-A1",
        "check_in_day": 12,
        "check_out_day": 16,
        "room_status": "DIRTY",
        "ledger_legs": [
            {"account": "CASH_REGISTER", "amount_cents": 12000, "memo": "Cash payment"},
            {"account": "ACCOMMODATION_REVENUE", "amount_cents": -9000, "memo": "Unbalanced leg"},
        ],
    }

    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            sat_res = await session.call_tool("audit_hostel_checkin", {"event_json": sat_event})
            sat_data = _extract_payload(sat_res)
            assert sat_data["status"] == "SAT"
            assert sat_data["total_volume_cents"] == 12000
            assert sat_data["violations"] == []

            unsat_res = await session.call_tool(
                "audit_hostel_checkin",
                {"event_json": unsat_overbooking_and_unbalanced_event},
            )
            unsat_data = _extract_payload(unsat_res)
            assert unsat_data["status"] == "UNSAT"
            assert len(unsat_data["violations"]) >= 1

            ingest_res = await session.call_tool(
                "ingest_operator_checkin_note",
                {
                    "note": "Max Mustermann checked in BED-A1 days 16..19 paid 150 EUR cash",
                    "bed_id": "BED-A1",
                },
            )
            ingest_data = _extract_payload(ingest_res)
            assert ingest_data["converged"] is True
            assert ingest_data["verdict"]["status"] == "SAT"

            clean_res = await session.call_tool("mark_bed_cleaned", {"bed_id": "BED-A1"})
            clean_data = _extract_payload(clean_res)
            assert clean_data == {"bed_id": "BED-A1", "clean_state": "CLEAN"}


@pytest.mark.asyncio
async def test_stdio_pydantic_validation_rejection() -> None:
    malformed_event = {
        "event_id": "evt_bad_account",
        "guest_name": "Invalid Guest",
        "bed_id": "BED-A1",
        "check_in_day": 20,
        "check_out_day": 22,
        "room_status": "CLEAN",
        "ledger_legs": [
            {"account": "CRYPTO_WALLET", "amount_cents": 5000, "memo": "Unsupported account"},
            {"account": "ACCOMMODATION_REVENUE", "amount_cents": -5000, "memo": "Revenue"},
        ],
    }

    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            bad_account = await session.call_tool(
                "audit_hostel_checkin",
                {"event_json": malformed_event},
            )
            assert bad_account.is_error is True

            missing_arg = await session.call_tool("audit_hostel_checkin", {})
            assert missing_arg.is_error is True
