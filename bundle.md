---
bundle:
  name: terminal-title
  version: 2.0.0
  description: >
    Automatically updates the terminal window/tab title to reflect the current
    session name. Hooks into prompt:complete (after hooks-session-naming) to
    reuse the generated session name — no extra LLM call required.

includes:
  - bundle: terminal-title:behaviors/terminal-title
---
