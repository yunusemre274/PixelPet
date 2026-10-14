# Token Reduction Protocol

This document defines how coding agents should manage context consumption. It is NOT a claim that agents have infinite persistent memory. Different sessions may have different context windows. These are practical rules to minimize waste.

---

## A. Read-Once Within a Working Session

If the agent has already read a document during the current session and the document has not changed, do NOT re-read the entire document. Rely on conversation/session context.

## B. Relevant-Document Routing

Do NOT read all documentation before every task.

**Example — Changing sprite frame timing:**

Read:
- `GEMINI.md` (auto-loaded)
- Relevant source files
- `docs/ASSET_PIPELINE.md`
- `docs/PET_BEHAVIOR.md` if animation states are affected

Do NOT read:
- `ROADMAP.md`
- `PRODUCT.md`
- `DECISIONS.md`
- Unrelated macOS research

Unless the task genuinely requires them.

## C. Fresh-Session Bootstrap

A new session should load:

1. `GEMINI.md` (routing table)
2. `PROJECT_STATE.md` (compressed current state)
3. The document(s) directly related to the requested task

Then inspect relevant source files. Only expand context if needed.

## D. Project State Compression

`PROJECT_STATE.md` exists so agents don't reconstruct project history from scratch. It contains:

- Current milestone
- Latest completed work
- Architecture state
- Known blockers
- Next recommended task
- Recently changed files

Keep it under ~100 lines. It is NOT a changelog.

## E. Do Not Repeatedly Scan

Once the agent knows the repository structure, do NOT recursively scan the entire repository before every small task. Inspect only relevant directories/files.

## F. Changed-File Invalidation

If a documentation file changed after it was previously read in the session, the cached mental model is stale. Re-read the changed document.

## G. Session Continuation

When the platform supports resuming the same session, prefer continuation for closely related work rather than starting a fresh context.

## H. Source of Truth Hierarchy

When information conflicts, precedence is (highest first):

```
1. Current explicit user instruction
2. AGENTS.md / GEMINI.md rules
3. DECISIONS.md
4. ARCHITECTURE.md
5. PRODUCT.md
6. ROADMAP.md
7. PROJECT_STATE.md
8. Code comments / assumptions
```

User instructions always have highest priority unless unsafe or technically impossible.

## I. Context Budget Modes

### SMALL — Simple Isolated Change

Load:
- `GEMINI.md` (router)
- Relevant source files
- One relevant domain doc

Examples: fix a typo, adjust a constant, rename a method.

### MEDIUM — Feature Implementation

Load:
- `GEMINI.md` (router)
- `PROJECT_STATE.md`
- Relevant architecture section from `ARCHITECTURE.md`
- Relevant domain docs
- Relevant source files

Examples: add a new pet state, implement click handling, add asset loading.

### LARGE — Architecture / Refactor / Milestone Work

Load:
- `ARCHITECTURE.md`
- `DECISIONS.md`
- Relevant `ROADMAP.md` section
- `PROJECT_STATE.md`
- Necessary domain docs
- All affected source areas

Examples: restructure module boundaries, implement a new subsystem, complete a milestone.

**Default to SMALL. Escalate only when needed.**

## J. Anti-Patterns

❌ Reading every `.md` file before a one-line fix  
❌ Scanning the entire repository tree before every task  
❌ Re-reading unchanged documents multiple times per session  
❌ Loading `ROADMAP.md` to fix a rendering bug  
❌ Loading `PRODUCT.md` to adjust a timer constant  
❌ Using LARGE mode for a SMALL task  
