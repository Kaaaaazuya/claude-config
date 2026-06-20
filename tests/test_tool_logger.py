import json
from io import StringIO
from pathlib import Path
from unittest.mock import patch


def _run_logger(payload: dict, project_root: Path) -> None:
    """tool_logger をインプロセスで実行するヘルパー。"""
    import importlib

    import hooks.tool_logger as mod

    importlib.reload(mod)  # モジュールキャッシュをリセット

    with (
        patch("sys.stdin", StringIO(json.dumps(payload))),
        patch("hooks.tool_logger.get_project_root", return_value=project_root),
        patch("sys.exit"),
    ):
        mod.main()


def test_appends_entry_to_jsonl(tmp_path):
    payload = {
        "session_id": "sess-1",
        "tool_name": "Bash",
        "tool_input": {"command": "ls"},
        "tool_response": {"exit_code": 0},
    }
    _run_logger(payload, tmp_path)

    lines = (tmp_path / "logs" / "tool-audit.jsonl").read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["tool"] == "Bash"
    assert entry["session_id"] == "sess-1"
    assert entry["success"] is True


def test_multiple_runs_accumulate(tmp_path):
    payload = {
        "session_id": "sess-1",
        "tool_name": "Edit",
        "tool_input": {"file_path": "/tmp/x"},
        "tool_response": {"exit_code": 0},
    }
    _run_logger(payload, tmp_path)
    _run_logger(payload, tmp_path)

    lines = (tmp_path / "logs" / "tool-audit.jsonl").read_text().splitlines()
    assert len(lines) == 2


def test_nonzero_exit_sets_success_false(tmp_path):
    payload = {
        "session_id": "sess-2",
        "tool_name": "Bash",
        "tool_input": {"command": "false"},
        "tool_response": {"exit_code": 1},
    }
    _run_logger(payload, tmp_path)

    entry = json.loads((tmp_path / "logs" / "tool-audit.jsonl").read_text())
    assert entry["success"] is False


def test_stderr_on_nonzero_exit(tmp_path, capsys):
    payload = {
        "session_id": "sess-3",
        "tool_name": "Bash",
        "tool_input": {"command": "false"},
        "tool_response": {"exit_code": 2},
    }
    _run_logger(payload, tmp_path)
    captured = capsys.readouterr()
    assert "Bash" in captured.err
    assert "exit 2" in captured.err


def test_missing_exit_code_treats_as_success(tmp_path):
    payload = {
        "session_id": "sess-4",
        "tool_name": "Read",
        "tool_input": {"file_path": "/tmp/f"},
        "tool_response": {},
    }
    _run_logger(payload, tmp_path)

    entry = json.loads((tmp_path / "logs" / "tool-audit.jsonl").read_text())
    assert entry["success"] is True
