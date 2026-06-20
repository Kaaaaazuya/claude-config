#!/usr/bin/env python3
"""UserPromptSubmit フック: N プロンプトごとにセッションログ更新を促す。"""

import json
import sys
import time
from pathlib import Path

from hooks._common import get_project_root

THRESHOLD = 5
_LOG_TARGET = "logs/session-log.md"
_COUNTER_DIR = Path("/tmp/claude-log-reminder")


def main() -> None:
    data = json.load(sys.stdin)
    sess_id = data.get("session_id", "unknown")

    _COUNTER_DIR.mkdir(exist_ok=True)
    counter_file = _COUNTER_DIR / f"count_{sess_id}"

    count = int(counter_file.read_text()) if counter_file.exists() else 0
    count += 1
    counter_file.write_text(str(count))

    if count % THRESHOLD != 0:
        return

    project_root = get_project_root()
    log_path = project_root / _LOG_TARGET

    if not log_path.exists():
        status = "（ファイル未作成）"
    else:
        age_min = int((time.time() - log_path.stat().st_mtime) / 60)
        status = f"（最終更新: {age_min}分前）"

    print(
        f"⏰ LOG REMINDER ({count}プロンプト経過)\n"
        f"   {_LOG_TARGET} {status}\n"
        f"   作業内容を要約して {_LOG_TARGET} に追記してください。"
    )

    sys.exit(0)


if __name__ == "__main__":
    main()
