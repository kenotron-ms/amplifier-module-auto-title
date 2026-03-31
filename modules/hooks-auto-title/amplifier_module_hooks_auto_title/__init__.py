"""Amplifier hook module: hooks-auto-title

Listens on prompt:complete (priority 200, after hooks-session-naming at 100),
reads the session name from metadata.json, and prints an ANSI OSC0 escape
sequence to update the terminal window/tab title.

No LLM call required — reuses the name computed by hooks-session-naming.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AutoTitleHook:
    """Sets the terminal title from the session name whenever it changes."""

    def __init__(self, coordinator: Any) -> None:
        self.coordinator = coordinator
        self._last_name: str | None = None

    def _get_session_dir(self, session_id: str) -> Path | None:
        """Locate the session directory.

        Mirrors the three-tier lookup used by hooks-session-naming so we find
        the same metadata.json regardless of Amplifier version or install path.
        """
        # Tier 1: coordinator exposes it directly (preferred — always current)
        if hasattr(self.coordinator, "session_dir"):
            return Path(self.coordinator.session_dir)

        # Tier 2: modern layout — ~/.amplifier/projects/<hash>/sessions/<id>
        projects_dir = Path.home() / ".amplifier" / "projects"
        if projects_dir.exists():
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    candidate = project_dir / "sessions" / session_id
                    if candidate.exists():
                        return candidate

        # Tier 3: legacy layout — ~/.amplifier/sessions/<id>
        legacy = Path.home() / ".amplifier" / "sessions" / session_id
        if legacy.exists():
            return legacy

        return None

    def _print_title(self, name: str) -> None:
        """Write ANSI OSC0 escape directly to the controlling terminal."""
        dir_name = Path.cwd().name
        prefix = os.environ.get("CLAUDE_TITLE_PREFIX", "")

        if prefix:
            title = f"{prefix} {dir_name} | {name}"
        else:
            title = f"{dir_name} | {name}"

        # Write to /dev/tty so the escape reaches the terminal even when
        # stdout/stderr are piped (common when Amplifier hooks run).
        try:
            with open("/dev/tty", "w") as tty:
                tty.write(f"\033]0;{title}\007")
                tty.flush()
        except OSError:
            # Fallback: write to stdout (works in most non-piped environments)
            print(f"\033]0;{title}\007", end="", flush=True)

    async def on_prompt_complete(self, event: str, data: dict) -> None:
        """Handle prompt:complete — runs after hooks-session-naming writes metadata.

        Reads the session name from metadata.json and updates the terminal title
        when the name is new or has changed.
        """
        session_id = data.get("session_id")
        if not session_id:
            return

        session_dir = self._get_session_dir(session_id)
        if not session_dir:
            logger.debug("auto-title: session dir not found for %s", session_id[:8])
            return

        metadata_path = session_dir / "metadata.json"
        if not metadata_path.exists():
            return

        try:
            metadata = json.loads(metadata_path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            logger.debug("auto-title: could not read metadata: %s", exc)
            return

        name = metadata.get("name")
        if not name:
            return  # session not yet named — nothing to show

        if name == self._last_name:
            return  # name unchanged — skip redundant update

        self._last_name = name
        self._print_title(name)
        logger.debug("auto-title: set terminal title to %r", name)


async def mount(
    coordinator: Any, config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Register the auto-title hook on prompt:complete.

    Runs at priority 200 — after hooks-session-naming (priority 100) — so the
    session name is already written to metadata.json when we read it.
    """
    hook = AutoTitleHook(coordinator)

    coordinator.hooks.register(
        "prompt:complete",
        hook.on_prompt_complete,
        priority=200,
        name="auto-title",
    )

    logger.info("hooks-auto-title: registered on prompt:complete (priority 200)")

    return {
        "name": "hooks-auto-title",
        "version": "1.0.0",
        "description": "Sets terminal window title from session name on prompt:complete",
    }
