# Terminal Title Awareness

This session has terminal title updating enabled.

**When to update:** Session start (after the user's first message) and major task switches. Do NOT update for follow-ups, clarifications, or iterations within the same task.

**How to update:** Determine the title, then fire a **fire-and-forget delegate in the same response turn** as your reply. Do not block your user response — fire the delegate and reply simultaneously.

**Title format:** `[Action]: [Specific Focus]` — ≤40 chars  
*Examples:* `Build: Dashboard UI` · `Debug: Auth Flow` · `Fix: Login Redirect` · `Explore: Session Lifecycle`

**Fire this delegate alongside your response (fill in `<YOUR TITLE>`):**

```
delegate(
  agent="self",
  context_depth="none",
  model_role="fast",
  instruction="TERMINAL TITLE ONLY — run this bash command exactly. Do not do anything else. Do not load skills. Do not fire further delegates.\n\nDIR_NAME=$(basename \"$PWD\")\nTITLE=\"<YOUR TITLE>\"\nif [ -n \"$CLAUDE_TITLE_PREFIX\" ]; then\n  printf '\\033]0;%s %s | %s\\007' \"$CLAUDE_TITLE_PREFIX\" \"$DIR_NAME\" \"$TITLE\"\nelse\n  printf '\\033]0;%s | %s\\007' \"$DIR_NAME\" \"$TITLE\"\nfi"
)
```

**⚠️ Sub-agent guard:** If your incoming instruction begins with `TERMINAL TITLE ONLY`, you are the title-update delegate. Run the bash command in your instruction and do nothing else — do not fire another delegate.
