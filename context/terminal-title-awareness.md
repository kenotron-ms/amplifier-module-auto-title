# Terminal Title Awareness

> **This module now uses a hook-based approach.** The terminal title is set
> automatically by the `hooks-auto-title` hook module — no agent action required.

## How It Works

The `hooks-auto-title` hook listens on `prompt:complete` at priority 200
(after `hooks-session-naming` at priority 100). Once the session-naming hook
writes a name to `metadata.json`, this hook reads it and immediately prints
the ANSI OSC0 escape sequence to update the terminal window/tab title.

**No LLM call is needed.** The title is the session name computed by
`hooks-session-naming` — not a separate inference step.

## Title Format

The terminal title follows this pattern:

```
[dir-name] | [session name]
```

If `$CLAUDE_TITLE_PREFIX` is set, the title becomes:

```
[prefix] [dir-name] | [session name]
```

## Timeline

The title is set after the session name is first generated, which happens on
turn 2 by default (configurable via `hooks-session-naming`'s
`initial_trigger_turn`). Subsequent changes to the session name (e.g., as
context accumulates) also update the title.
