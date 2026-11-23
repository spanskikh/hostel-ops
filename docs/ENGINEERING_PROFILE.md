# Engineering Profile — `hostel-ops`

> **Architectural Role:** Neuro-Symbolic Triple-Entry Ledger & Concurrency-Safe Booking Engine (`D1` Maturity Tier)

## 1. Concepts and Theories
- **Database-Level Temporal Exclusion (`btree_gist`):** Enforces non-overlapping room occupancy invariants directly inside PostgreSQL via GiST range exclusion constraints (`EXCLUDE USING gist (room_id WITH =, stay_range WITH &&)`), guaranteeing atomic rejection (`SQLSTATE 23P01` `ExclusionViolation`) under concurrent `TOCTOU` booking races.
- **Triple-Entry Accounting & Zero-Sum Invariants:** Models financial postings (charges, payments, refunds, ledger adjustments) with formal `Z3` zero-sum conservation laws (`sum(debits) == sum(credits)`) and state-machine transition guards.
- **Neuro-Symbolic Operational Guard:** Validates LLM-parsed guest booking/housekeeping intents against `Pydantic v2` schemas, `Z3` interval/balance invariants, and PostgreSQL transactional constraints before commit.
- **Deterministic Concurrency & Property Verification:** Combines multi-worker race tests (`TOCTOU` collision harnesses) with `Hypothesis` stateful ledger fuzzing.

## 2. Frameworks and Libraries
| Layer | Technology | Version / Spec | Role in `hostel-ops` |
| :--- | :--- | :--- | :--- |
| **Transactional RDBMS** | `psycopg[binary]` + PostgreSQL | `>=3.2.0` (`btree_gist`) | Enforces atomic range exclusion (`23P01`) and ACID triple-entry ledger transactions. |
| **Formal Solver** | `z3-solver` | `>=4.13.0` | Proves check-in/check-out temporal bounds, occupancy capacity, and zero-sum ledger balance. |
| **Analytical & Audit Store** | `duckdb` | `>=1.1.0` | Embedded analytical snapshots and offline verification audit trail. |
| **Contracts & Protocol** | `pydantic`, `fastmcp` | `>=2.9.0`, `>=2.0.0` | Domain models (`BookingIntent`, `LedgerEntry`) and `FastMCP` `stdio` operational tools. |
| **QA & Fuzzing** | `pytest`, `pytest-asyncio`, `hypothesis`, `mypy` | Python `>=3.12` | Concurrent `TOCTOU` race tests, property fuzzing, `--strict` static analysis (`13` files). |

## 3. Dev Tools and Environment
- **Local Infrastructure:** Calculate Linux Desktop (KDE, Kernel `6.18+`) on Intel Core i5-9500 (6C/6T, AVX2, `24 GiB` / `16 GiB` RAM) running local PostgreSQL (`btree_gist` enabled) and `DuckDB`.
- **Protocol & Schema Tooling:** `FastMCP` `stdio` test harness, `Mermaid` sequence/ER diagrams in `README.md` and `docs/ARCHITECTURE.md`.
- **CI/CD & Supply Chain:** GitHub Actions executing `ruff`, `mypy --strict`, offline `pytest` verification suites, and `CycloneDX` SBOM generation.

## 4. Processes and Procedures
- **Defense-in-Depth Invariant Enforcement:** Business invariants are verified at three independent boundaries: `Pydantic v2` input parsing -> `Z3` symbolic proof -> PostgreSQL `btree_gist` & check constraints.
- **Zero-PII Hygiene Policy:** Strictly enforces synthetic/anonymized guest fixtures across all tests and documentation via `tests/test_release_hygiene.py`.
- **End-to-End CR Governance:** Full traceability across `RELEASES.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, and `docs/releases/vX.Y.Z-retrospective.md`.

## 5. Test Approach, Tools, Environment & Metrics
- **Verification Pyramid:**
  1. *Concurrency & Race Tests:* Parallel booking contention tests verifying deterministic `23P01` `ExclusionViolation` handling with zero double-bookings.
  2. *Symbolic & Property Tests:* `Z3` zero-sum accounting proofs + `Hypothesis` randomized booking/cancellation sequences.
  3. *MCP `stdio` & Doc Quality Gates:* End-to-end JSON-RPC tool contract validation + automated AST/regex documentation checks.
- **Empirical Baseline Metrics (`v0.6.0` -> `v0.7.0`):**
  - **Double-Booking Escape Rate:** `0.0%` under concurrent `TOCTOU` contention (`100%` deterministic `23P01` rejection).
  - **Accounting Conservation:** `100%` `Z3` zero-sum invariant satisfaction across all tested ledger state transitions.
  - **Offline Fast Suite:** `26 passed`, `0` `mypy --strict` errors across `13` source files.
