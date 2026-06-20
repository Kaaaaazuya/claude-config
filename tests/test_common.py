def test_get_project_root_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    from hooks._common import get_project_root

    assert get_project_root() == tmp_path


def test_get_project_root_fallback_to_cwd(monkeypatch, tmp_path):
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    from hooks._common import get_project_root

    assert get_project_root() == tmp_path


def test_get_log_dir_creates_directory(tmp_path):
    from hooks._common import get_log_dir

    log_dir = get_log_dir(tmp_path)
    assert log_dir == tmp_path / "logs"
    assert log_dir.is_dir()


def test_get_log_dir_idempotent(tmp_path):
    from hooks._common import get_log_dir

    get_log_dir(tmp_path)
    get_log_dir(tmp_path)  # 2回呼んでもエラーにならない
    assert (tmp_path / "logs").is_dir()
