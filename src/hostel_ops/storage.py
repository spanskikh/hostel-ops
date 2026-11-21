from __future__ import annotations

import os
from pathlib import Path

import duckdb
import psycopg

from hostel_ops.contracts import CheckInEventProposal, ExistingBooking, RoomCleanState

DEFAULT_DSN = os.getenv(
    "POSTGRES_DSN", "postgresql://dev:dev@host.docker.internal:15432/hostel_ops"
)
DEFAULT_DUCKDB = os.getenv("AUDIT_DB_PATH", "/app/data/hostel_analytics.duckdb")


class HostelClusterStore:
    """Гибридное хранилище: OLTP в PostgreSQL (rhino) + аналитика/аудит в DuckDB (hippo)."""

    def __init__(self, pg_dsn: str = DEFAULT_DSN, duck_path: str | Path = DEFAULT_DUCKDB) -> None:
        self._pg_dsn = pg_dsn
        self._duck_path = str(duck_path)

    def init_schemas(self) -> None:
        with psycopg.connect(self._pg_dsn, autocommit=True) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS beds (
                    bed_id VARCHAR(32) PRIMARY KEY,
                    room_code VARCHAR(16) NOT NULL,
                    clean_state VARCHAR(16) NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id VARCHAR(64) PRIMARY KEY,
                    bed_id VARCHAR(32) NOT NULL REFERENCES beds(bed_id),
                    guest_name VARCHAR(128) NOT NULL,
                    check_in_day INTEGER NOT NULL,
                    check_out_day INTEGER NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS triple_ledger (
                    entry_id SERIAL PRIMARY KEY,
                    event_id VARCHAR(64) NOT NULL,
                    booking_id VARCHAR(64) NOT NULL,
                    account VARCHAR(32) NOT NULL,
                    amount_cents INTEGER NOT NULL,
                    memo VARCHAR(128) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT now()
                );
                """
            )

        duck = duckdb.connect(self._duck_path)
        try:
            duck.execute("SET memory_limit='512MB'; SET threads=2;")
            duck.execute(
                """
                CREATE TABLE IF NOT EXISTS event_audit_log (
                    ts TIMESTAMP DEFAULT current_timestamp,
                    event_id VARCHAR NOT NULL,
                    bed_id VARCHAR NOT NULL,
                    status VARCHAR NOT NULL,
                    volume_cents INTEGER NOT NULL,
                    violations_count INTEGER NOT NULL
                );
                """
            )
        finally:
            duck.close()

    def upsert_bed(self, bed_id: str, room_code: str, clean_state: RoomCleanState) -> None:
        with psycopg.connect(self._pg_dsn, autocommit=True) as conn:
            conn.execute(
                """
                INSERT INTO beds (bed_id, room_code, clean_state)
                VALUES (%s, %s, %s)
                ON CONFLICT (bed_id) DO UPDATE SET
                    room_code = EXCLUDED.room_code,
                    clean_state = EXCLUDED.clean_state;
                """,
                (bed_id, room_code, clean_state),
            )

    def fetch_bed_state_and_bookings(
        self, bed_id: str
    ) -> tuple[RoomCleanState, list[ExistingBooking]]:
        with psycopg.connect(self._pg_dsn) as conn:
            row = conn.execute(
                "SELECT clean_state FROM beds WHERE bed_id = %s;", (bed_id,)
            ).fetchone()
            state: RoomCleanState = row[0] if row else "DIRTY"
            rows = conn.execute(
                """
                SELECT booking_id, bed_id, check_in_day, check_out_day
                FROM bookings WHERE bed_id = %s;
                """,
                (bed_id,),
            ).fetchall()
            bookings = [
                ExistingBooking(
                    booking_id=str(r[0]),
                    bed_id=str(r[1]),
                    check_in_day=int(r[2]),
                    check_out_day=int(r[3]),
                )
                for r in rows
            ]
            return state, bookings

    def commit_verified_checkin(self, event: CheckInEventProposal) -> None:
        """Атомарно фиксирует заезд, проводки тройной записи и переводит койку в DIRTY."""
        with psycopg.connect(self._pg_dsn) as conn:
            with conn.transaction():
                conn.execute(
                    """
                    INSERT INTO bookings (
                        booking_id, bed_id, guest_name, check_in_day, check_out_day
                    )
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (
                        event.event_id,
                        event.bed_id,
                        event.guest_name,
                        event.check_in_day,
                        event.check_out_day,
                    ),
                )
                for leg in event.ledger_legs:
                    conn.execute(
                        """
                        INSERT INTO triple_ledger (
                            event_id, booking_id, account, amount_cents, memo
                        )
                        VALUES (%s, %s, %s, %s, %s);
                        """,
                        (event.event_id, event.event_id, leg.account, leg.amount_cents, leg.memo),
                    )
                conn.execute(
                    "UPDATE beds SET clean_state = 'DIRTY' WHERE bed_id = %s;",
                    (event.bed_id,),
                )

    def log_audit(self, event_id: str, bed_id: str, status: str, volume: int, v_cnt: int) -> None:
        duck = duckdb.connect(self._duck_path)
        try:
            duck.execute(
                "INSERT INTO event_audit_log VALUES (current_timestamp, ?, ?, ?, ?, ?);",
                [event_id, bed_id, status, volume, v_cnt],
            )
        finally:
            duck.close()
