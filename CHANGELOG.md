# Changelog

All notable changes and formal Change Requests (CRs) for `hostel-ops` are documented in this file.

## [0.8.0] - 2026-11-23 — CR-022 & CR-023: Cross-Cluster Z3 Contract, SBOM Gate & Rubric Sign-Off
### Objective & Risk Mitigated
- **Closed Residual Risk:** Enforced cross-cluster Z3 RAM budget invariants (`hippo` 24 GiB / `rhino` 16 GiB), 12-tool FastMCP namespace disjointness, deterministic `CycloneDX` SBOM reproducibility, and grammar-constrained live Ollama documentation rubric evaluation (`>= 4/5`).
- **Traceability:** Change Requests `CR-022` and `CR-023` (`BUG-003` / `CAPA-006`) merged via `--no-ff`; release `v0.8.0`.

### Added & Changed
- `pyproject.toml` & `.github/workflows/ci.yml` (`CR-022`): Bump version to `0.8.0`, add `cyclonedx-bom>=7.2.0`, and verify two-run `CycloneDX` SBOM determinism and path hygiene in CI.
- `tests/test_sbom_and_contracts.py` (`CR-022`): Cross-cluster Z3 SAT/UNSAT budget solver, 12-tool FastMCP namespace disjointness check, and `CycloneDX` SBOM reproducibility gate.
- `tests/test_docs_quality.py` (`CR-023` / `BUG-003` / `CAPA-006`): Upgraded `_judge_doc_with_ollama` to JSON Schema grammar-constrained decoding (`DocRubricScore.model_json_schema()`, `temperature=0.0`, `timeout=180.0`).

### Verification Evidence
- `ruff check src tests` & `mypy src tests --strict`: `0` issues across all source and test modules.
- `pytest -m "not integration"`: `30 passed` (including `CR-022` Z3 cluster and `CycloneDX` SBOM gates).
- `pytest -v -m integration`: `2 passed` against live `hippo` Ollama (`qwen2.5-coder:7b`) and `rhino` PostgreSQL.

## [0.7.0] - 2026-11-23 — CR-017..CR-021: Engineering Profiles, SSoT Governance & Auditor Fix
### Objective & Risk Mitigated
- **Closed Residual Risk:** Eliminated cross-repository inconsistency in how theoretical foundations, library versions, workstation environment, SDLC/QA processes, and empirical benchmark metrics are presented to technical reviewers; enforced structural compliance via automated AST/regex quality gates.
- **Traceability:** Change Request `CR-017` implemented across `hostel-ops` (`docs/ENGINEERING_PROFILE.md`, `README.md`, `tests/test_docs_quality.py`, `RELEASES.md`).

### Added
- `docs/ENGINEERING_PROFILE.md`: Standardized 5-section engineering dossier (`1. Concepts and Theories`, `2. Frameworks and Libraries`, `3. Dev Tools and Environment`, `4. Processes and Procedures`, `5. Test Approach, Tools, Environment & Metrics`).
- `README.md`: Added direct navigation link to `docs/ENGINEERING_PROFILE.md`.
- `tests/test_docs_quality.py`: Added mandatory file, 5-heading structural assertions, signal density checks, and `2` new seeded defect counterexamples (`missing_engineering_profile`, `missing_profile_section`).

- `DEVPROCESS.md` & `tests/test_docs_quality.py` (`CR-019` / `CAPA-003`): Enforced `<= 1.5 KiB` PTY paste cap and `logs/` summary cap.

- `README.md` & SSoT Migration (`CR-020` / `CAPA-004`): Consolidated shared governance docs (`DEVPROCESS.md`, `RELEASES.md`, `docs/DEFECTS_AND_CAPA.md`, `docs/releases/*`) into `spanskikh/spanskikh` and linked canonical URLs.
- `tests/test_docs_quality.py` (`CR-021` / `BUG-002` / `CAPA-005`): Fixed Markdown auditor to scan all tracked `*.md` files recursively for Cyrillic/placeholders and enforce `CLUSTER_DOC_DUPLICATE`.

### Verification Evidence
- `ruff check .` & `mypy --strict`: `0` issues across all source and test modules.
- `pytest -m "not integration"`: All unit, contract, hygiene, and documentation quality tests green (`+2` new counterexample cases).

## [0.6.0] - 2026-11-22 — CR-014, CR-015 & CR-016: Pre-Public Hygiene Gate, Portfolio Sync & Public CI / CycloneDX Activation
### Objective & Risk Mitigated
- **Closed Residual Risk:** Enforced automated pre-public secret/PII hygiene checks, synchronized `README.md` and `docs/ARCHITECTURE.md` with live `btree_gist` TOCTOU concurrency (`23P01`) and property verification metrics, and activated GitHub Actions CI + `CycloneDX` SBOM generation.
- **Traceability:** Branches `feat/cr-014-release-hygiene-gate` (`f469b84`), `feat/cr-015-portfolio-landing-sync` (`d64daa3`), and `CR-016` CI promotion merged via `--no-ff`; releases `v0.6.0`.

### Added
- `tests/test_release_hygiene.py`: Pre-public tracked-file secret/PII scanner and CI readiness assertions.
- `docs/ci/ci.yml` -> `.github/workflows/ci.yml` & `scripts/publish_to_github.sh`: Automated CI verification and `CycloneDX` SBOM artifact generation.
- `README.md` & `docs/ARCHITECTURE.md`: Added empirical concurrency and property verification benchmark table.

### Verification Evidence
- `./scripts/run_logged.sh cr015_ruff`: `All checks passed!`
- `./scripts/run_logged.sh cr015_mypy`: `Success: no issues found in 13 source files`
- `./scripts/run_logged.sh cr015_pytest`: `26 passed, 2 deselected`

## [0.6.0] - 2026-11-22 — CR-014, CR-015 & CR-016: Pre-Public Hygiene Gate, Portfolio Sync & Public CI / CycloneDX Activation
### Objective & Risk Mitigated
- **Closed Residual Risk:** Enforced automated pre-public secret/PII hygiene checks, synchronized `README.md` and `docs/ARCHITECTURE.md` with live `btree_gist` TOCTOU concurrency (`23P01`) and property verification metrics, and activated GitHub Actions CI + `CycloneDX` SBOM generation.
- **Traceability:** Branches `feat/cr-014-release-hygiene-gate` (`f469b84`), `feat/cr-015-portfolio-landing-sync` (`d64daa3`), and `CR-016` CI promotion merged via `--no-ff`; releases `v0.6.0`.

### Added
- `tests/test_release_hygiene.py`: Pre-public tracked-file secret/PII scanner and CI readiness assertions.
- `docs/ci/ci.yml` -> `.github/workflows/ci.yml` & `scripts/publish_to_github.sh`: Automated CI verification and `CycloneDX` SBOM artifact generation.
- `README.md` & `docs/ARCHITECTURE.md`: Added empirical concurrency and property verification benchmark table.

### Verification Evidence
- `./scripts/run_logged.sh cr015_ruff`: `All checks passed!`
- `./scripts/run_logged.sh cr015_mypy`: `Success: no issues found in 13 source files`
- `./scripts/run_logged.sh cr015_pytest`: `26 passed, 2 deselected`

## [0.6.0] - 2026-11-22 — CR-014, CR-015 & CR-016: Pre-Public Hygiene Gate, Portfolio Sync & Public CI / CycloneDX Activation
### Objective & Risk Mitigated
- **Closed Residual Risk:** Enforced automated pre-public secret/PII hygiene checks, synchronized `README.md` and `docs/ARCHITECTURE.md` with live `btree_gist` TOCTOU concurrency (`23P01`) and property verification metrics, and activated GitHub Actions CI + `CycloneDX` SBOM generation.
- **Traceability:** Branches `feat/cr-014-release-hygiene-gate` (`f469b84`), `feat/cr-015-portfolio-landing-sync` (`d64daa3`), and `CR-016` CI promotion merged via `--no-ff`; releases `v0.6.0`.

### Added
- `tests/test_release_hygiene.py`: Pre-public tracked-file secret/PII scanner and CI readiness assertions.
- `docs/ci/ci.yml` -> `.github/workflows/ci.yml` & `scripts/publish_to_github.sh`: Automated CI verification and `CycloneDX` SBOM artifact generation.
- `README.md` & `docs/ARCHITECTURE.md`: Added empirical concurrency and property verification benchmark table.

### Verification Evidence
- `./scripts/run_logged.sh cr015_ruff`: `All checks passed!`
- `./scripts/run_logged.sh cr015_mypy`: `Success: no issues found in 13 source files`
- `./scripts/run_logged.sh cr015_pytest`: `26 passed, 2 deselected`

## [0.6.0] - 2026-11-22 — CR-014, CR-015 & CR-016: Pre-Public Hygiene Gate, Portfolio Sync & Public CI / CycloneDX Activation
### Objective & Risk Mitigated
- **Closed Residual Risk:** Enforced automated pre-public secret/PII hygiene checks, synchronized `README.md` and `docs/ARCHITECTURE.md` with live `btree_gist` TOCTOU concurrency (`23P01`) and property verification metrics, and activated GitHub Actions CI + `CycloneDX` SBOM generation.
- **Traceability:** Branches `feat/cr-014-release-hygiene-gate` (`f469b84`), `feat/cr-015-portfolio-landing-sync` (`d64daa3`), and `CR-016` CI promotion merged via `--no-ff`; releases `v0.6.0`.

### Added
- `tests/test_release_hygiene.py`: Pre-public tracked-file secret/PII scanner and CI readiness assertions.
- `docs/ci/ci.yml` -> `.github/workflows/ci.yml` & `scripts/publish_to_github.sh`: Automated CI verification and `CycloneDX` SBOM artifact generation.
- `README.md` & `docs/ARCHITECTURE.md`: Added empirical concurrency and property verification benchmark table.

### Verification Evidence
- `./scripts/run_logged.sh cr015_ruff`: `All checks passed!`
- `./scripts/run_logged.sh cr015_mypy`: `Success: no issues found in 13 source files`
- `./scripts/run_logged.sh cr015_pytest`: `26 passed, 2 deselected`

## [0.5.0] - 2026-11-22 — CR-010 & CR-013: FastMCP `stdio` Contract Harness & Normative SDLC Governance
### Objective & Risk Mitigated
- **Closed Residual Risk:** Guaranteed that all agent-facing `FastMCP` `stdio` tools (`audit_hostel_checkin`, `ingest_operator_checkin_note`, `mark_bed_cleaned`) enforce strict Pydantic v2 input schemas and Z3 triple-entry accounting, anti-overbooking, and housekeeping invariants without bypassing validation gates.
- **Traceability:** Branch `feat/cr-010-mcp-stdio-contracts` merged via `--no-ff`; releases `v0.5.0`.

### Added
- `tests/test_mcp_contracts.py`: Real `mcp.client.stdio` JSON-RPC discovery (`list_tools()`), input JSON schema verification, `SAT` check-in approval, `UNSAT` rejection of overbooking/dirty-room/unbalanced ledger entries, and Pydantic `ValidationError` rejection on malformed accounts.
- `DEVPROCESS.md` & `docs/DEFECTS_AND_CAPA.md` (`CAPA-002`): Codified normative SDLC gates, zero-orphan CR traceability, and English-only Git governance.

### Verification Evidence
- `./scripts/run_logged.sh cr010_ruff` (`logs/20261122-152741_cr010_ruff.log`): `All checks passed!`
- `./scripts/run_logged.sh cr010_mypy` (`logs/20261122-152741_cr010_mypy.log`): `Success: no issues found in 12 source files`
- `./scripts/run_logged.sh cr010_pytest` (`logs/20261122-152742_cr010_pytest.log`): `18 passed, 2 deselected`

## [0.4.0] - 2026-11-22 — CR-009: Dev-Process Auditability, Execution Logging & Release Retrospectives
### Objective & Risk Mitigated
- **Closed Residual Risk:** Eliminated loss of iterative engineering history, unlogged local execution runs, and missing post-release retrospectives across `hostel-ops` by introducing deterministic `.stdout`/`.stderr`/`.log` capture, versioned `docs/dev-log/` artifacts, and mandatory release retrospectives enforced by automated mutation tests.
- **Traceability:** Branch `feat/cr-009-dev-process-auditability` merged via `--no-ff`; releases `v0.4.0`.

### Added
- `scripts/run_logged.sh` & `tests/test_run_logged.py`: POSIX execution wrapper capturing ISO-8601 start/end timestamps, duration, exit codes, and split `.stdout`, `.stderr`, and `.log` artifacts in gitignored `logs/`.
- `docs/dev-log/`: Versioned raw patch/script artifact history (`20261122-130500_cr-009_install-run-logged.sh`, `20261122-130800_cr-009_enforce-release-retrospectives.py`).
- `docs/releases/v0.3.0-retrospective.md` & `tests/test_docs_quality.py`: Post-release retrospective capturing Lessons Learned, Rejected Ideas, Unlucky Probe-Runs, and Release Chat Digest, enforced by an 8th seeded mutation counterexample (`missing_retrospective_section`).

### Verification Evidence
- `./scripts/run_logged.sh cr009_final_gate`: `ruff check src tests` (`All checks passed!`), `mypy src tests --strict` (`Success: no issues found`), `pytest -v -m "not integration"` (`14 passed, 2 deselected`).

## [0.3.0] - 2026-11-22 — CR-008: Documentation Quality Gates, Mutation Counterexamples & Live Rubric Evaluation
### Objective & Risk Mitigated
- **Closed Residual Risk:** Eliminated documentation drift, broken relative links, unclosed Mermaid diagrams, unresolved placeholders, and hollow marketing claims across `hostel-ops` through deterministic structural/style/market-value checks, 7 seeded negative mutation counterexamples, and live `Ollama` rubric grading.
- **Traceability:** Branch `feat/cr-008-docs-quality-tests` merged via `--no-ff`; releases `v0.3.0`.

### Added
- `docs/ARCHITECTURE.md`: Added Level-2 domain architecture with Mermaid topology, ADRs, and trade-off/risk control matrix.
- `tests/test_docs_quality.py`: `DocQualityAuditor` (`Pydantic v2`), 7 parametrized negative mutation counterexamples (`MISSING_REQUIRED_FILE`, `LANGUAGE_DRIFT_CYRILLIC`, `MISSING_REQUIRED_SECTION`, `PLACEHOLDER_LEAK`, `BROKEN_MERMAID_BLOCK`, `BROKEN_RELATIVE_LINK`, `LOW_MARKET_SIGNAL_OR_HYPE`), and `@pytest.mark.integration` live `Ollama` rubric test (`num_ctx=2048`, `num_predict=160`, `timeout=180.0` tuned for CPU inference on `hippo`).
- `pyproject.toml`: Standardized version `0.3.0`, `[project.optional-dependencies] dev`, `pythonpath = ["src"]`, and `@pytest.mark.integration` marker.

### Verification Evidence
- `ruff check src tests`: `All checks passed!`
- `mypy src tests --strict`: `Success: no issues found`
- `pytest -v -m "not integration"`: `12 passed, 2 deselected` (including all 7 seeded mutation counterexamples)
- `pytest -v -m "integration"`: `2 passed, 12 deselected` (live `Ollama` rubric >= 4/5 on real docs and <= 2/5 on weak counterexample)

## [0.3.0-cr007] - 2026-11-22 — CR-007: Live PostgreSQL GiST Concurrency Race Test & DDL Migration
### Objective & Risk Mitigated
- **Closed Residual Risk:** Caught and eliminated a live schema drift defect on `rhino` where pre-existing `v0.1.0` `bookings` tables bypassed `CREATE TABLE IF NOT EXISTS` without `bookings_no_overlap_excl`; proved under concurrent `asyncio` barrier execution that simultaneous overlapping bookings (`[10, 14)` vs `[12, 16)`) yield exactly 1 commit and 1 `ExclusionViolation` (`23P01`).
- **Traceability:** Branch `feat/cr-007-live-gist-concurrency` merged via `--no-ff`.

### Defect & Root Cause Analysis (`BUG-001`)
- **Defect (`BUG-001`):** Concurrent live race test caught two overlapping bookings (`[10, 14)` and `[12, 16)`) succeeding simultaneously on `rhino` despite `CR-004`.
- **Root Cause:** `CREATE TABLE IF NOT EXISTS bookings (...)` is a silent no-op on tables provisioned in `v0.1.0`, leaving live `bookings` without `bookings_no_overlap_excl` while unit tests only inspected SQL string literals.
- **Lessons Learned & Process Improvement (`CAPA-001`):** Never rely on `CREATE TABLE IF NOT EXISTS` to evolve constraints or indexes on stateful cluster databases; enforce explicit idempotent `pg_constraint` / `IF NOT EXISTS` DDL guards and require live `@pytest.mark.integration` verification against stateful `rhino` instances before closing DB changes.

### Added & Fixed
- `src/hostel_ops/storage.py`: Added idempotent `DO $$ ... ALTER TABLE bookings ADD CONSTRAINT bookings_no_overlap_excl ... $$` migration in `init_schemas()` (`BUG-001` fix).
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
