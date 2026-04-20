# Phase 1: Declarative Filter API Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-20
**Phase:** 01-declarative-filter-api-foundation
**Areas discussed:** API Declaration Style, Validation Contract, Extensibility Boundary
**Mode:** auto

---

## API Declaration Style

| Option | Description | Selected |
|--------|-------------|----------|
| Class + fluent parity | Support both declaration styles and normalize internally | ✓ |
| Class-only for MVP | Keep one declaration style until later | |
| Fluent-only for MVP | Optimize for concise builder API first | |

**Auto choice:** Class + fluent parity (recommended default in auto mode)
**Notes:** Aligns with API-02 and preserves ergonomic flexibility while keeping one internal model.

---

## Validation Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Fail-fast config validation | Validate definitions early with actionable errors | ✓ |
| Lazy runtime validation | Defer validation to first filter use | |
| Mixed strategy | Fail-fast for critical issues, defer non-critical warnings | |

**Auto choice:** Fail-fast config validation (recommended default in auto mode)
**Notes:** Reduces ambiguity for downstream planning and catches API misuse earlier.

---

## Extensibility Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Practical hook set | Limit to query + widget behavior hooks in phase 1 | ✓ |
| Broad plugin system now | Build generalized plugin architecture immediately | |
| Minimal no-hooks MVP | Delay extensibility to later phases | |

**Auto choice:** Practical hook set (recommended default in auto mode)
**Notes:** Matches project out-of-scope constraints against premature plugin abstraction.

---

## OpenCode's Discretion

- Internal module boundaries and helper naming.
- Exact error message text and formatting details.

## Deferred Ideas

- Advanced query-language semantics beyond API foundation scope.
- Rich UI/UX behaviors that belong in later roadmap phases.
