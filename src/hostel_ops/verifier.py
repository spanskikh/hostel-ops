from __future__ import annotations

import z3

from hostel_ops.contracts import (
    CheckInEventProposal,
    ExistingBooking,
    HostelAuditVerdict,
)


def verify_checkin_event(
    event: CheckInEventProposal,
    existing_bookings: list[ExistingBooking],
) -> HostelAuditVerdict:
    """Проверяет тройную запись, интервалы проживания и статус уборки через Z3."""
    solver = z3.Solver()

    leg_vars = [z3.Int(f"leg_{i}") for i in range(len(event.ledger_legs))]
    for var, leg in zip(leg_vars, event.ledger_legs, strict=True):
        solver.add(var == leg.amount_cents)
    solver.add(z3.Sum(leg_vars) == 0)

    positive_volume = sum(max(0, leg.amount_cents) for leg in event.ledger_legs)
    vol_var = z3.Int("positive_volume")
    solver.add(vol_var == positive_volume, vol_var > 0)

    is_clean = z3.Bool("room_is_clean")
    solver.add(is_clean == z3.BoolVal(event.room_status == "CLEAN"), is_clean)

    ci, co = z3.Ints("ci co")
    solver.add(ci == event.check_in_day, co == event.check_out_day, ci < co)

    same_bed_bookings = [b for b in existing_bookings if b.bed_id == event.bed_id]
    for idx, b in enumerate(same_bed_bookings):
        b_ci, b_co = z3.Ints(f"b_ci_{idx} b_co_{idx}")
        solver.add(b_ci == b.check_in_day, b_co == b.check_out_day)
        solver.add(z3.Or(co <= b_ci, ci >= b_co))

    if solver.check() == z3.sat:
        return HostelAuditVerdict(
            status="SAT",
            event_id=event.event_id,
            total_volume_cents=positive_volume,
        )

    violations: list[str] = []
    balance = sum(leg.amount_cents for leg in event.ledger_legs)
    if balance != 0:
        violations.append(f"Triple-entry imbalance: sum(amount_cents)={balance} != 0")
    if positive_volume <= 0:
        violations.append("Zero-volume ledger entry is forbidden")
    if event.room_status != "CLEAN":
        violations.append(f"Housekeeping violation: bed '{event.bed_id}' is {event.room_status}")
    if event.check_in_day >= event.check_out_day:
        violations.append(
            f"Invalid interval: in={event.check_in_day} >= out={event.check_out_day}"
        )
    for b in same_bed_bookings:
        if not (event.check_out_day <= b.check_in_day or event.check_in_day >= b.check_out_day):
            violations.append(
                f"Overbooking conflict on '{event.bed_id}' with '{b.booking_id}' "
                f"[{b.check_in_day}, {b.check_out_day})"
            )

    return HostelAuditVerdict(
        status="UNSAT",
        event_id=event.event_id,
        total_volume_cents=positive_volume,
        violations=violations,
    )
