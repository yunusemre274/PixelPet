# Agent Operating Rules

## Core Behavior

Agents MUST:

- Inspect existing architecture before modifying code
- Never rewrite unrelated code
- Never silently change architectural decisions
- Never introduce dependencies without explaining why
- Prefer small incremental changes
- Preserve backward compatibility where reasonable
- Run appropriate tests after implementation
- Update documentation when architecture changes
- Update `PROJECT_STATE.md` after meaningful work
- Update `DECISIONS.md` when a significant architectural decision is made
- Update `ROADMAP.md` only when roadmap state actually changes

Agents MUST NOT:

- Refactor the entire project while implementing a small feature
- Invent undocumented APIs
- Use private macOS APIs without explicit project owner approval
- Duplicate existing systems
- Create unnecessary abstraction layers
- Create giant files when the responsibility can be separated cleanly
- Silently replace technologies
- Regenerate user-created pixel art
- Modify unrelated assets
- Read all documentation files before every task

## Context Discipline

> Before implementing something, determine which documentation files are actually relevant. Read only those files unless broader context is genuinely necessary.

Use `GEMINI.md` as the routing layer. Use `PROJECT_STATE.md` as compressed state. Load domain documentation only when relevant to the current task.

See [TOKEN_REDUCE.md](TOKEN_REDUCE.md) for the full context protocol.

## Documentation Updates

Update documentation when:
- Architecture changes
- A new decision is made or an existing one changes
- A milestone status changes
- The project state meaningfully changes

Do NOT force documentation updates for:
- Formatting-only edits
- Trivial internal refactors that don't change interfaces
- Work-in-progress that hasn't reached a stable point

## Source of Truth Hierarchy

When information conflicts, precedence is (highest first):

1. Current explicit user instruction
2. `AGENTS.md` / `GEMINI.md` rules
3. `DECISIONS.md`
4. `ARCHITECTURE.md`
5. `PRODUCT.md`
6. `ROADMAP.md`
7. `PROJECT_STATE.md`
8. Code comments / assumptions

User instructions always have highest priority unless unsafe or technically impossible.

## Workflow

```text
1. Understand request
2. Identify task scope
3. Select context mode: SMALL / MEDIUM / LARGE
4. Read only relevant docs
5. Inspect affected code
6. Check architecture boundaries
7. Implement smallest correct change
8. Test
9. Update relevant documentation
10. Update PROJECT_STATE.md if meaningful
11. Report exactly what changed
```
