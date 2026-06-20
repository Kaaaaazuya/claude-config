#!/usr/bin/env python3
"""PostToolUse フック: 全ツール操作を logs/tool-audit.jsonl に追記する。"""

import json
import sys
from datetime import datetime, timezone

from hooks._common import get_log_dir, get_project_root


def main() -> None:
    data = json.load(sys.stdin)
    project_root = get_project_root()
    log_dir = get_log_dir(project_root)

    tool_resp = data.get("tool_response") or {}
    exit_code = tool_resp.get("exit_code")
    success = exit_code == 0 if exit_code is not None else True

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": data.get("session_id"),
        "tool": data.get("tool_name"),
        "input": data.get("tool_input"),
        "exit_code": exit_code,
        "duration_ms": tool_resp.get("durationMs") or tool_resp.get("duration_ms"),
        "success": success,
    }

    with open(log_dir / "tool-audit.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    if not success:
        print(
            f"⚠️ ツール '{data.get('tool_name')}' が exit {exit_code} で終了しました。",
            file=sys.stderr,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
