import importlib
import json
from io import StringIO
from pathlib import Path
from unittest.mock import patch


def _run_reminder(
    session_id: str, project_root: Path, threshold: int = 3, counter_dir: Path | None = None
) -> str:
    """log_reminder をインプロセスで実行し、stdout を返す。"""
    import hooks.log_reminder as mod

    importlib.reload(mod)

    if counter_dir is None:
        counter_dir = project_root / ".counters"

    payload = {"session_id": session_id}
    captured_out = StringIO()
    with (
        patch("sys.stdin", StringIO(json.dumps(payload))),
        patch("hooks.log_reminder.get_project_root", return_value=project_root),
        patch("hooks.log_reminder.THRESHOLD", threshold),
        patch("hooks.log_reminder._COUNTER_DIR", counter_dir),
        patch("sys.stdout", captured_out),
        patch("sys.exit"),
    ):
        mod.main()
    return captured_out.getvalue()


def test_no_output_below_threshold(tmp_path):
    out = _run_reminder("s1", tmp_path, threshold=3)
    assert out == ""


def test_output_at_threshold(tmp_path):
    _run_reminder("s1", tmp_path, threshold=3)
    _run_reminder("s1", tmp_path, threshold=3)
    out = _run_reminder("s1", tmp_path, threshold=3)
    assert "LOG REMINDER" in out
    assert "3" in out  # プロンプト経過数


def test_no_output_just_after_threshold(tmp_path):
    for _ in range(3):
        _run_reminder("s1", tmp_path, threshold=3)
    out = _run_reminder("s1", tmp_path, threshold=3)  # 4回目
    assert out == ""


def test_counter_is_session_scoped(tmp_path):
    """セッションが違えばカウンタが独立している。"""
    for _ in range(3):
        _run_reminder("s1", tmp_path, threshold=3)
    # s2 はまだ1回目なので出力されない
    out = _run_reminder("s2", tmp_path, threshold=3)
    assert out == ""


def test_shows_log_file_missing_status(tmp_path):
    for _ in range(2):
        _run_reminder("s1", tmp_path, threshold=3)
    out = _run_reminder("s1", tmp_path, threshold=3)
    assert "未作成" in out


def test_shows_last_modified_time(tmp_path):
    log_file = tmp_path / "logs" / "session-log.md"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("# log")

    for _ in range(2):
        _run_reminder("s1", tmp_path, threshold=3)
    out = _run_reminder("s1", tmp_path, threshold=3)
    assert "分前" in out
