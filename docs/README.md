# BIRAJ AI Documentation

This directory is the single source of truth for BIRAJ AI's technical plans and verified project status.

## Documents

- [Architecture](ARCHITECTURE.md) — system boundaries, layers, and current/target design.
- [Development Plan](DEVELOPMENT-PLAN.md) — ordered build phases and completion gates.
- [Decision Log](DECISIONS.md) — confirmed decisions and unresolved choices.
- [Testing Strategy](TESTING.md) — test levels, quality gates, and verification status.
- [Module Register](modules/README.md) — module ownership, status, and documentation rules.
- [Branch Register](BRANCHES.md) — branch names, purposes, pull requests, and branch lifecycle rules.

## Documentation rules

1. Update the relevant document in the same change that alters code or a technical decision.
2. Mark proposals as **Proposed** and unresolved choices as **Pending**. Never present them as approved.
3. Use only these status labels: **Implemented**, **In progress**, **Planned**, or **Pending decision**.
4. Keep detailed module specifications in one module document; link to them rather than copying the same content elsewhere.
5. GitHub Issues track work items. They do not replace architecture or decision documentation.
6. The root README is the entry point; this folder owns the detailed technical record.
7. Do not add product/service scope, pricing, subscriptions, or marketing plans during the core-platform phase.
