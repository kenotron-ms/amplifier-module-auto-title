# amplifier-bundle-terminal-title

An [Amplifier](https://github.com/microsoft/amplifier) behavior bundle that automatically updates the terminal window/tab title to reflect what the AI agent is working on.

Adapted from [claude-code-terminal-title](https://github.com/bluzername/claude-code-terminal-title) by bluzername.

---

## What It Does

When you're running multiple terminal sessions, it's easy to lose track of which one is doing what. This bundle teaches the Amplifier agent to set descriptive, human-readable titles:

```
my-project | Build: Dashboard UI
my-project | Debug: Auth Flow
my-project | Test: Payment Module
```

The agent sets the title at the start of each session and updates it when switching to a substantially different task.

---

## Quick Start (App Bundle — Recommended)

Install globally so terminal titling works in **every** Amplifier session, no per-project config needed:

```bash
amplifier bundle add git+https://github.com/kenotron-ms/amplifier-module-auto-title@main --app
```

That's it. Restart Amplifier and titles start appearing automatically.

> **What `--app` does:** Registers the bundle as a global app bundle that auto-composes with every session, stored in `~/.amplifier/`. No need to touch any project's `bundle.md`.

---

## Project-Level Install

If you only want terminal titling in a specific project, add it to your `.amplifier/bundle.md`:

```yaml
includes:
  - bundle: git+https://github.com/kenotron-ms/amplifier-module-auto-title@main
```

### Just the Behavior (for existing bundles)

If you already have your own bundle and just want to add the behavior:

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/kenotron-ms/amplifier-module-auto-title@main#subdirectory=behaviors/terminal-title.yaml
```

---

## What's Included

| File | Purpose |
|------|---------|
| `bundle.md` | Root bundle (foundation + this behavior) |
| `behaviors/terminal-title.yaml` | The composable behavior — includes skill and context |
| `skills/terminal-title.md` | Skill: teaches the agent when/how to set titles |
| `context/terminal-title-awareness.md` | Brief awareness prompt injected at session start |
| `scripts/set_title.sh` | Optional: standalone shell script for projects that prefer it |

---

## How It Works

The bundle is **skill-driven**: the agent uses the `load_skill` tool to learn the title-setting conventions and applies them using `bash`. No custom Python hook module is needed.

**Flow:**
1. Session starts → awareness context prompts the agent to load the skill
2. Agent loads `terminal-title` skill → learns format rules and the bash command
3. Agent runs `printf '\033]0;%s | %s\007'` inline to set the title
4. Agent updates the title again when switching to a new high-level task

**ANSI compatibility:** Works with macOS Terminal, iTerm2, Alacritty, xterm, rxvt, tmux, screen, and most modern terminal emulators.

---

## Customization

### Custom prefix via environment variable

```bash
export CLAUDE_TITLE_PREFIX="🤖"
# Produces: "🤖 my-project | Build: Dashboard UI"
```

### Optional shell script

Copy `scripts/set_title.sh` to your project root and call it instead of the inline command:

```bash
bash scripts/set_title.sh "Build: Dashboard UI"
```

The script handles sanitization, the directory prefix, and `CLAUDE_TITLE_PREFIX` automatically.

---

## Title Format

```
[current-dir] | [Action]: [Specific Focus]
```

| Situation | Title |
|-----------|-------|
| Building a feature | `Build: Dashboard UI` |
| Debugging an issue | `Debug: Auth Flow` |
| Writing tests | `Test: Payment Module` |
| Refactoring code | `Refactor: API Layer` |
| Database work | `DB: Users Migration` |
| Infrastructure | `Infra: Docker Setup` |

---

## Credits

- Original skill and scripts by [bluzername](https://github.com/bluzername/claude-code-terminal-title)
- Adapted for the Amplifier ecosystem

## License

MIT
