from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hostel_ops.storage import HostelClusterStore


def test_init_schemas_enforces_btree_gist_exclusion_constraint() -> None:
    executed_sql: list[str] = []
    mock_conn = MagicMock()
    mock_conn.execute.side_effect = lambda sql, *args: executed_sql.append(str(sql))

    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_conn
    mock_ctx.__exit__.return_value = False

    with (
        patch("hostel_ops.storage.psycopg.connect", return_value=mock_ctx),
        patch("hostel_ops.storage.duckdb.connect"),
    ):
        store = HostelClusterStore(pg_dsn="postgresql://stub", duck_path=":memory:")
        store.init_schemas()

    joined = "\n".join(executed_sql)
    assert "CREATE EXTENSION IF NOT EXISTS btree_gist" in joined
    assert "EXCLUDE USING gist" in joined
    assert "int4range(check_in_day, check_out_day, '[)')" in joined


def test_housekeeping_cleaning_rejects_maintenance_and_cleans_dirty() -> None:
    mock_conn = MagicMock()
    mock_tx = MagicMock()
    mock_tx.__enter__.return_value = None
    mock_tx.__exit__.return_value = False
    mock_conn.transaction.return_value = mock_tx

    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_conn
    mock_ctx.__exit__.return_value = False

    store = HostelClusterStore(pg_dsn="postgresql://stub", duck_path=":memory:")

    with patch("hostel_ops.storage.psycopg.connect", return_value=mock_ctx):
        mock_conn.execute.return_value.fetchone.return_value = ("MAINTENANCE",)
        with pytest.raises(ValueError, match="MAINTENANCE"):
            store.complete_housekeeping_cleaning("B-101-1")

        mock_conn.execute.return_value.fetchone.return_value = ("DIRTY",)
        assert store.complete_housekeeping_cleaning("B-101-1") == "CLEAN"
