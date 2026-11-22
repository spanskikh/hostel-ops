# Changelog

All notable changes and formal Change Requests (CRs) for `hostel-ops` are documented in this file.

## [0.3.0-cr007] - 2026-11-22 — CR-007: Live PostgreSQL GiST Concurrency Race Test & DDL Migration
### Objective & Risk Mitigated
- **Closed Residual Risk:** Caught and eliminated a live schema drift defect on `rhino` where pre-existing `v0.1.0` `bookings` tables bypassed `CREATE TABLE IF NOT EXISTS` without `bookings_no_overlap_excl`; proved under concurrent `asyncio` barrier execution that simultaneous overlapping bookings (`[10, 14)` vs `[12, 16)`) yield exactly 1 commit and 1 `ExclusionViolation` (`23P01`).
- **Traceability:** Branch `feat/cr-007-live-gist-concurrency` merged via `--no-ff`.

### Added & Fixed
- `src/hostel_ops/storage.py`: Added idempotent `DO $$ ... ALTER TABLE bookings ADD CONSTRAINT bookings_no_overlap_excl ... $$` migration in `init_schemas()` for pre-existing tables.
- `pyproject.toml`: Bumped version to `0.3.0`, added `[project.optional-dependencies] dev`, `pythonpath = ["src"]`, and `@pytest.mark.integration` marker.
- `tests/test_live_gist_concurrency.py`: Barrier-synchronized concurrent race test verifying DB-level GiST exclusion and `triple_ledger` atomicity.

### Verification Evidence
- `ruff check src tests`: `All checks passed!`
- `mypy src tests --strict`: `Success: no issues found in 9 source files`
- `pytest -v -m "not integration"`: `4 passed, 1 deselected`
- `pytest -v -m "integration"`: `1 passed, 4 deselected` (against live `rhino` PostgreSQL via OpenRC tunnel)

## [0.3.0-cr006] - 2026-11-22 — CR-006: Offline GitHub Actions CI & CycloneDX SBOM Blueprints
### Objective & Risk Mitigated
- **Closed Residual Risk:** Standardized pre-release verification (`ruff`, `mypy --strict`, `pytest -m "not integration"`) and supply-chain `CycloneDX` SBOM generation across `hostel-ops` without triggering premature CI runs while the repository remains private.
- **Traceability:** Branch `feat/cr-006-ci-blueprints` merged via `--no-ff`.

### Added
- `docs/ci/ci.yml`: Staged GitHub Actions workflow (`uv`, `ruff`, `mypy --strict`, `pytest`, `cyclonedx-py` SBOM artifact upload).
- `scripts/publish_to_github.sh`: Deterministic pre-flight and promotion script (`git mv docs/ci/ci.yml .github/workflows/ci.yml` + `gh repo edit --visibility public`).

### Verification Evidence
- `docs/ci/ci.yml` YAML indentation validated and staged cleanly; `.github/workflows/` kept absent until public release.

## [0.2.0] - 2026-11-21 — CR-004: DB-Level GiST Anti-Overbooking & Housekeeping Cycle
### Objective & Risk Mitigated
* **Closed Residual Risk:** Eliminated TOCTOU race conditions between Z3 verification and PostgreSQL persistence via database-engine exclusion constraints, and closed the bed housekeeping lifecycle (`DIRTY -> CLEAN`).
* **Traceability:** Branch `feat/cr-004-db-gist-anti-overbooking` merged via `--no-ff` (`e690d30`).

### Added
* `src/hostel_ops/storage.py`: Enabled `btree_gist` extension, added `EXCLUDE USING gist (bed_id WITH =, int4range(check_in_day, check_out_day, '[)') WITH &&)` on `bookings`, and implemented `complete_housekeeping_cleaning()` (`DIRTY -> CLEAN` with `MAINTENANCE` guard).
* `src/hostel_ops/server.py`: `mark_bed_cleaned` FastMCP tool.
* `tests/test_db_gist_and_housekeeping.py`: Unit tests verifying DDL exclusion constraints and housekeeping state transitions.

### Verification Evidence
* `ruff check src tests`: `All checks passed!`
* `mypy src tests` (`--strict`): `0` issues across `8` source files.
* `pytest -v`: `4 passed` (`80` `Hypothesis` property examples).

## [0.1.0] - 2026-11-21 — Triple-Entry Ledger & Booking Engine Baseline
* Initial Z3 zero-sum triple-entry accounting verifier, anti-overbooking interval solver, and atomic PostgreSQL + `DuckDB` persistence.
