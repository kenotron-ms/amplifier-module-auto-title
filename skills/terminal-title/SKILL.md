---
name: terminal-title
description: >
  Sets the terminal window/tab title to reflect the current high-level task.
  Use at the start of every session after the first user message, and when
  switching to a distinctly new high-level task. Helps developers manage
  multiple terminal windows at a glance.
version: 1.0.0
---

# Terminal Title

## When to Use

**Always trigger at:**
- Start of every new session, immediately after the user's first message
- When switching to a substantially different high-level task

**Task switches that warrant a title update:**
- Frontend → backend work
- Debugging → new feature development
- One module/component → a completely different one
- Different domain areas (e.g., auth → payments → infrastructure)

**Do NOT update for:**
- Follow-up questions about the same task
- Small refinements to current work
- Debugging the same feature just built
- Clarifications or quick questions
- Iterating on the same component
- Mid-task progress checks

## How to Set the Title

Title updates use a **fire-and-forget delegate** — fire it in the same response turn as your reply, not before. The delegate runs in parallel and the user gets their response immediately.

See `terminal-title:context/terminal-title-awareness.md` for the exact delegate call to use (it includes the bash snippet pre-embedded in the instruction).

**The bash command the delegate runs:**

```bash
DIR_NAME=$(basename "$PWD")
TITLE="Your Title Here"
if [ -n "$CLAUDE_TITLE_PREFIX" ]; then
  printf '\033]0;%s %s | %s\007' "$CLAUDE_TITLE_PREFIX" "$DIR_NAME" "$TITLE"
else
  printf '\033]0;%s | %s\007' "$DIR_NAME" "$TITLE"
fi
```

The `CLAUDE_TITLE_PREFIX` environment variable allows users to add a custom prefix (e.g., an emoji or team name). The snippet handles it automatically.

## Title Format

**Pattern:** `[Action]: [Specific Focus]`

| Situation | Title |
|-----------|-------|
| Building a feature | `Build: Dashboard UI` |
| Debugging an issue | `Debug: Auth Flow` |
| Writing tests | `Test: Payment Module` |
| Refactoring | `Refactor: API Layer` |
| Database work | `DB: Users Migration` |
| Infrastructure / config | `Infra: Docker Setup` |
| Code review | `Review: PR #142` |
| General exploration | `Explore: Codebase` |

**Displayed in terminal as:**
```
my-project | Build: Dashboard UI
my-project | Debug: Auth Flow
```

## Rules

- Keep the title ≤ 40 characters
- Use present-tense action words: "Build", "Debug", "Refactor", "Test"
- Include specific focus: what module, file, or feature
- No need to include the project name — the script prefixes it automatically

## Common Mistakes

| Bad | Good |
|-----|------|
| `Implementing user authentication system with JWT tokens and refresh logic` | `Build: JWT Auth` |
| `Working` | `Refactor: Auth Layer` |
| `my-project: Fix bug` | `Fix: Login Redirect` |
| `I am working on the dashboard` | `Build: Dashboard UI` |

## Example Workflow

```
User: "Help me debug the authentication flow in the API"
→ printf '\033]0;%s | %s\007' "$(basename "$PWD")" "Debug: Auth API Flow"

User: "Now create a React component for the user profile page"
→ printf '\033]0;%s | %s\007' "$(basename "$PWD")" "Build: User Profile UI"

User: "Write tests for the payment processing module"
→ printf '\033]0;%s | %s\007' "$(basename "$PWD")" "Test: Payment Module"
```

## Optional: Bundled Script

A full-featured shell script is available at `terminal-title:scripts/set_title.sh`
for users who prefer to copy it into their project. The inline approach above
is preferred — no installation required.
