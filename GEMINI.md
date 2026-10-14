# DockPet — Agent Context Router

DockPet is a native macOS application where a pixel-art virtual pet lives around the macOS Dock. It uses a transparent AppKit window positioned relative to the Dock, with modular rendering, behavior, and asset systems. No private APIs. No web runtimes.

## Immutable Rules

- Native macOS only (Swift/AppKit). No Electron, Tauri, or web views.
- No private Apple APIs without explicit project owner approval.
- Do not regenerate user-created pixel art.
- Do not implement features beyond the current milestone scope.
- Prefer small, incremental, testable changes.

## Documentation Routing

| Need | Read |
|------|------|
| Agent rules | [AGENTS.md](AGENTS.md) |
| Product behavior / MVP | [PRODUCT.md](PRODUCT.md) |
| Architecture / modules | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Current implementation status | [PROJECT_STATE.md](PROJECT_STATE.md) |
| Next milestone / roadmap | [ROADMAP.md](ROADMAP.md) |
| Architectural decisions | [DECISIONS.md](DECISIONS.md) |
| Sprite / asset conventions | [docs/ASSET_PIPELINE.md](docs/ASSET_PIPELINE.md) |
| Pet states / animations | [docs/PET_BEHAVIOR.md](docs/PET_BEHAVIOR.md) |
| macOS / Dock research | [docs/MACOS_RESEARCH.md](docs/MACOS_RESEARCH.md) |
| Testing approach | [docs/TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md) |
| Context efficiency | [TOKEN_REDUCE.md](TOKEN_REDUCE.md) |
| Agent skills | [SKILLS.md](SKILLS.md) |

## Current State

→ See [PROJECT_STATE.md](PROJECT_STATE.md) for compressed current state.

## Context Protocol

1. **Start** with this file (auto-loaded).
2. **Read** `PROJECT_STATE.md` for current status.
3. **Read** only the document(s) relevant to your task.
4. **Inspect** affected source files.
5. **Expand** context only if genuinely needed.

Do NOT read all documentation before every task. See [TOKEN_REDUCE.md](TOKEN_REDUCE.md) for context budget rules.

## Task Context Modes

| Mode | When | Load |
|------|------|------|
| SMALL | Simple isolated change | This file + relevant source + one domain doc |
| MEDIUM | Feature implementation | + `PROJECT_STATE` + architecture section + domain docs |
| LARGE | Architecture/milestone work | + `ARCHITECTURE` + `DECISIONS` + `ROADMAP` section + affected source areas |

Default to SMALL. Escalate only when needed.

## Post-Task Checklist

- [ ] Tests pass
- [ ] Architecture boundaries respected
- [ ] `PROJECT_STATE.md` updated (if meaningful change)
- [ ] `DECISIONS.md` updated (if new decision)
- [ ] `ROADMAP.md` updated (if milestone status changed)
- [ ] No unrelated code modified
