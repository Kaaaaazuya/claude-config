import os
from pathlib import Path


def get_project_root() -> Path:
    """
    CLAUDE_PROJECT_DIR 環境変数を優先し、なければ cwd を返す。
    フック実行時のプロジェクトルート解決に使う。
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    return Path.cwd()


def get_log_dir(project_root: Path) -> Path:
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
