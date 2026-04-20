---
phase: 03
slug: async-autocomplete-scale-performance
status: approved
shadcn_initialized: false
preset: not-applicable
created: 2026-04-20
---

# Phase 03 — UI Design Contract

> Visual and interaction contract for async autocomplete behavior in default Django Admin.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | none (Django admin native templates) |
| Icon library | none required |
| Font | Django admin default stack |

---

## Spacing Scale

Declared values (must be multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | icon/input inline spacing |
| sm | 8px | input chip/option spacing |
| md | 16px | control vertical rhythm |
| lg | 24px | control group separation |
| xl | 32px | page section gap |
| 2xl | 48px | major section separation |
| 3xl | 64px | not used in this phase |

Exceptions: none

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 14px | 400 | 1.5 |
| Label | 13px | 600 | 1.4 |
| Heading | 16px | 600 | 1.3 |
| Display | 20px | 600 | 1.2 |

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | inherit admin default | Background/surfaces |
| Secondary (30%) | inherit admin default | Inputs/lists |
| Accent (10%) | inherit admin link/accent color | Focus ring + active option only |
| Destructive | inherit admin destructive color | Clear/remove actions only |

Accent reserved for: focused input border, highlighted option row, active fetch spinner indicator

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | Apply filters |
| Empty state heading | No matching options |
| Empty state body | Try a different search term or broaden your filter input. |
| Error state | Unable to load options. Check your query and try again. |
| Destructive confirmation | Reset filters: Clear all active filters? |

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| Django admin native templates/static | autocomplete control partial + progressive JS module | not required |

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-04-20
