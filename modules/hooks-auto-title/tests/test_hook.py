"""Unit tests for hooks-auto-title."""

import json
from unittest.mock import MagicMock, patch

import pytest

from amplifier_module_hooks_auto_title import AutoTitleHook, mount


# ---------------------------------------------------------------------------
# mount() registration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mount_registers_on_prompt_complete():
    coordinator = MagicMock()
    coordinator.hooks = MagicMock()
    coordinator.hooks.register = MagicMock()

    await mount(coordinator)

    coordinator.hooks.register.assert_called_once()
    args, kwargs = coordinator.hooks.register.call_args
    assert args[0] == "prompt:complete"
    assert kwargs["priority"] == 200
    assert kwargs["name"] == "auto-title"


@pytest.mark.asyncio
async def test_mount_returns_metadata_dict():
    coordinator = MagicMock()
    coordinator.hooks = MagicMock()
    coordinator.hooks.register = MagicMock()

    metadata = await mount(coordinator)

    assert metadata is not None
    assert metadata["name"] == "hooks-auto-title"
    assert "version" in metadata


# ---------------------------------------------------------------------------
# _get_session_dir — tier 1: coordinator.session_dir
# ---------------------------------------------------------------------------


def test_get_session_dir_uses_coordinator_attr(tmp_path):
    coordinator = MagicMock()
    coordinator.session_dir = str(tmp_path)

    hook = AutoTitleHook(coordinator)
    result = hook._get_session_dir("any-session-id")

    assert result == tmp_path


# ---------------------------------------------------------------------------
# on_prompt_complete — happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sets_title_when_name_is_new(tmp_path):
    coordinator = MagicMock()
    coordinator.session_dir = str(tmp_path)

    (tmp_path / "metadata.json").write_text(
        json.dumps(
            {
                "name": "Debug: Auth Flow",
                "name_generated_at": "2024-01-01T00:00:00+00:00",
            }
        )
    )

    hook = AutoTitleHook(coordinator)

    with patch.object(hook, "_print_title") as mock_print:
        await hook.on_prompt_complete("prompt:complete", {"session_id": "abc123"})
        mock_print.assert_called_once_with("Debug: Auth Flow")


@pytest.mark.asyncio
async def test_tracks_last_name_after_setting(tmp_path):
    coordinator = MagicMock()
    coordinator.session_dir = str(tmp_path)

    (tmp_path / "metadata.json").write_text(json.dumps({"name": "Build: Dashboard"}))

    hook = AutoTitleHook(coordinator)
    with patch.object(hook, "_print_title"):
        await hook.on_prompt_complete("prompt:complete", {"session_id": "abc123"})

    assert hook._last_name == "Build: Dashboard"


# ---------------------------------------------------------------------------
# on_prompt_complete — no duplicate updates
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skips_when_name_unchanged(tmp_path):
    coordinator = MagicMock()
    coordinator.session_dir = str(tmp_path)

    (tmp_path / "metadata.json").write_text(json.dumps({"name": "Debug: Auth Flow"}))

    hook = AutoTitleHook(coordinator)
    hook._last_name = "Debug: Auth Flow"  # already shown

    with patch.object(hook, "_print_title") as mock_print:
        await hook.on_prompt_complete("prompt:complete", {"session_id": "abc123"})
        mock_print.assert_not_called()


@pytest.mark.asyncio
async def test_updates_when_name_changes(tmp_path):
    coordinator = MagicMock()
    coordinator.session_dir = str(tmp_path)

    (tmp_path / "metadata.json").write_text(json.dumps({"name": "Refactor: API Layer"}))

    hook = AutoTitleHook(coordinator)
    hook._last_name = "Debug: Auth Flow"  # old name

    with patch.object(hook, "_print_title") as mock_print:
        await hook.on_prompt_complete("prompt:complete", {"session_id": "abc123"})
        mock_print.assert_called_once_with("Refactor: API Layer")


# ---------------------------------------------------------------------------
# on_prompt_complete — graceful degradation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skips_when_no_session_id():
    coordinator = MagicMock()
    hook = AutoTitleHook(coordinator)

    with patch.object(hook, "_print_title") as mock_print:
        await hook.on_prompt_complete("prompt:complete", {})
        mock_print.assert_not_called()


@pytest.mark.asyncio
async def test_skips_when_session_dir_not_found():
    # Use a plain object so hasattr("session_dir") is False
    class FakeCoordinator:
        pass

    hook = AutoTitleHook(FakeCoordinator())

    with patch.object(hook, "_print_title") as mock_print:
        await hook.on_prompt_complete(
            "prompt:complete", {"session_id": "nonexistent-session-id-xyz"}
        )
        mock_print.assert_not_called()


@pytest.mark.asyncio
async def test_skips_when_metadata_missing(tmp_path):
    coordinator = MagicMock()
    coordinator.session_dir = str(tmp_path)
    # metadata.json intentionally not created

    hook = AutoTitleHook(coordinator)

    with patch.object(hook, "_print_title") as mock_print:
        await hook.on_prompt_complete("prompt:complete", {"session_id": "abc123"})
        mock_print.assert_not_called()


@pytest.mark.asyncio
async def test_skips_when_name_not_yet_in_metadata(tmp_path):
    coordinator = MagicMock()
    coordinator.session_dir = str(tmp_path)

    # Session exists but naming hasn't run yet (turn < initial_trigger_turn)
    (tmp_path / "metadata.json").write_text(json.dumps({"turn_count": 1}))

    hook = AutoTitleHook(coordinator)

    with patch.object(hook, "_print_title") as mock_print:
        await hook.on_prompt_complete("prompt:complete", {"session_id": "abc123"})
        mock_print.assert_not_called()


@pytest.mark.asyncio
async def test_skips_on_corrupt_metadata(tmp_path):
    coordinator = MagicMock()
    coordinator.session_dir = str(tmp_path)

    (tmp_path / "metadata.json").write_text("not valid json {{{")

    hook = AutoTitleHook(coordinator)

    with patch.object(hook, "_print_title") as mock_print:
        await hook.on_prompt_complete("prompt:complete", {"session_id": "abc123"})
        mock_print.assert_not_called()


# ---------------------------------------------------------------------------
# _print_title — ANSI escape format
# ---------------------------------------------------------------------------


def test_print_title_writes_ansi_osc0(tmp_path, monkeypatch):
    """The escape sequence must be OSC0: \\033]0;<title>\\007"""
    coordinator = MagicMock()
    hook = AutoTitleHook(coordinator)

    written = []

    class FakeTTY:
        def write(self, s):
            written.append(s)

        def flush(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setenv("CLAUDE_TITLE_PREFIX", "")
    with patch("builtins.open", return_value=FakeTTY()):
        hook._print_title("Debug: Auth Flow")

    assert len(written) == 1
    seq = written[0]
    assert seq.startswith("\033]0;")
    assert seq.endswith("\007")
    assert "Debug: Auth Flow" in seq


def test_print_title_includes_prefix(monkeypatch):
    coordinator = MagicMock()
    hook = AutoTitleHook(coordinator)

    written = []

    class FakeTTY:
        def write(self, s):
            written.append(s)

        def flush(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setenv("CLAUDE_TITLE_PREFIX", "★")
    with patch("builtins.open", return_value=FakeTTY()):
        hook._print_title("Build: Dashboard")

    assert "★" in written[0]
    assert "Build: Dashboard" in written[0]
