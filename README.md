# claude-config

プロジェクト横断で使う Claude Code のスキル・フック・パーミッション設定をまとめたリポジトリ。

## 構成

```
skills/
  commit/SKILL.md        # Conventional Commits 準拠コミット
  allowlist/SKILL.md     # 許可コマンドの抽出・管理
  grill-me/SKILL.md      # 実装前の設計インタビュー
  hook-status/SKILL.md   # フック稼働・ログ蓄積状況の診断
  log-analyzer/SKILL.md  # ログ分析・繰り返しパターン抽出
  retro-codify/SKILL.md  # セッション振り返りと学びの言語化
  skill-builder/SKILL.md # 候補から draft スキルを生成
hooks/
  pre-tool-use.sh        # 破壊的 git コマンドをブロック（PreToolUse）
  notify.sh              # 入力待ち時のデスクトップ通知（Notification）
  ruff-format.sh         # .py 編集直後に Ruff で自動整形（PostToolUse）
  _common.py             # フック共通のパス解決処理
  tool_logger.py         # 全ツール操作を tool-audit.jsonl に記録（PostToolUse）
  log_reminder.py        # N 回ごとにログ更新を促す（UserPromptSubmit）
tests/                   # hooks/ の Python フックに対する pytest テスト
settings.json            # 汎用パーミッション設定テンプレート
.github/workflows/
  claude-review.yml      # 共通PR自動レビュー本体（Reusable Workflow）
  lint.yml               # YAML を yamllint + actionlint で検証する CI
templates/
  claude-review.yml      # 各リポジトリへ置く呼び出しワークフローのテンプレート
.yamllint.yml            # yamllint 設定（Actions 向けに緩め）
pyproject.toml           # uv プロジェクト設定（pytest / ruff / pyyaml）
```

## 使い方

### グローバルに適用（全プロジェクトで有効）

```bash
# ~/.claude/ にコピー（または直接このリポジトリを clone）
cp -r skills/ ~/.claude/skills/
cp -r hooks/ ~/.claude/hooks/
# settings.json は ~/.claude/settings.json と手動マージ（上書き不可）
```

### プロジェクト単位で適用

```bash
cp -r skills/ /path/to/project/.claude/skills/
cp -r hooks/ /path/to/project/.claude/hooks/
chmod +x /path/to/project/.claude/hooks/*.sh
```

`settings.json` は参照用テンプレート。プロジェクトの `.claude/settings.json` に必要なエントリだけコピーして使う。

## スキルの説明

### `/commit`

Conventional Commits 1.0.0 準拠のコミットを対話的に作成する。

- type / scope / subject / body / footer を規約に沿って組み立て
- コミット前にメッセージをユーザーに提示してから実行
- `--no-verify` でのフック迂回を禁止

### `/allowlist`

直近の作業で実行した Bash コマンドのうち副作用のないものを抽出し、`.claude/settings.json` の `permissions.allow` に追記する。ユーザー確認後にのみ書き込む。

### `/hook-status`

フックスクリプトの存在・ログ蓄積状況・settings.json の設定を診断し、Phase 判定（Phase 1 正常稼働 / Phase 2 未実装など）を出力する。

### `/log-analyzer`

`logs/tool-audit.jsonl` を集計し、繰り返しパターン・エラー傾向・スキル化候補を抽出してレポートを生成する。「ログ分析して」「パターン調べて」でも自律発動。

### `/retro`（retro-codify）

セッション終了前に振り返りを行い、設計判断・問題解決・落とし穴など再利用可能な学びを言語化して `logs/retro-candidates.md` に追記する。スキルを自動生成せず候補提示にとどめる。

### `/skill-builder`

`logs/skill-candidates.json`（機械的検出）と `logs/retro-candidates.md`（意味的抽出）を入力に、人間が選んだパターンを draft 状態の `SKILL.md` + `meta.json` として生成する。

## フックの説明

### `notify.sh`（Notification フック）

Claude が入力待ち・確認待ちになったときにデスクトップ通知を出す。長時間タスク中に別作業で待つ用。リポジトリ名をタイトルに自動設定。

**設定例**（`.claude/settings.json`）:
```json
{
  "hooks": {
    "Notification": [{ "hooks": [{ "type": "command", "command": ".claude/hooks/notify.sh", "async": true }] }]
  }
}
```

### `ruff-format.sh`（PostToolUse フック）

Claude が `.py` ファイルを編集するたびに `ruff format` + `ruff check --fix` を自動実行する。`uv` が使えるプロジェクト向け。

**設定例**（`.claude/settings.json`）:
```json
{
  "hooks": {
    "PostToolUse": [{ "matcher": "Edit|Write|MultiEdit", "hooks": [{ "type": "command", "command": ".claude/hooks/ruff-format.sh", "async": true }] }]
  }
}
```

### `tool_logger.py`（PostToolUse フック）

全ツール操作（Bash / Edit / Write / Read）を `logs/tool-audit.jsonl` に追記する。ログ分析・スキル候補抽出の主データソース。

**設定例**（`.claude/settings.json`）:
```json
{
  "hooks": {
    "PostToolUse": [{ "matcher": "Bash|Edit|Write|Read", "hooks": [{ "type": "command", "command": ".claude/hooks/tool_logger.py" }] }]
  }
}
```

### `log_reminder.py`（UserPromptSubmit フック）

プロンプトが N 回（既定: 5 回）送られるごとに、`logs/session-log.md` の更新をセッションコンテキストに注入する。

**設定例**（`.claude/settings.json`）:
```json
{
  "hooks": {
    "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": ".claude/hooks/log_reminder.py" }] }]
  }
}
```

## PR 自動レビューの共通化

[Claude Code GitHub Actions](https://github.com/anthropics/claude-code-action) を使った PR 自動レビューを、Reusable Workflow として 1 か所に集約する。レビュー本体は `.github/workflows/claude-review.yml`（このリポジトリ）に置き、各リポジトリは数行の呼び出しワークフローを置くだけで利用できる。

### 導入手順（利用する各リポジトリ側）

1. `templates/claude-review.yml` を、利用したいリポジトリの `.github/workflows/claude-review.yml` としてコピーする。

   ```yaml
   name: Claude Auto Review
   on:
     pull_request:
       types: [opened, synchronize, reopened]
   jobs:
     review:
       uses: Kaaaaazuya/claude-config/.github/workflows/claude-review.yml@main
       secrets:
         anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
   ```

2. 利用するリポジトリに `ANTHROPIC_API_KEY` を Secret として登録する（Settings → Secrets and variables → Actions）。
3. （任意）`CLAUDE.md` と `docs/review-rules.md` にプロジェクト固有のレビュー基準を書いておくと、レビュー内容に反映される。

### 上書きできる入力

| 入力 | 既定値 | 説明 |
| --- | --- | --- |
| `max_turns` | `12` | エージェントの最大会話ターン数（コスト上限） |
| `timeout_minutes` | `15` | ジョブのタイムアウト（分） |

上書きする場合は呼び出し側に `with:` を追加する。

```yaml
   review:
     uses: Kaaaaazuya/claude-config/.github/workflows/claude-review.yml@main
     with:
       max_turns: 8
     secrets:
       anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

### 注意

- 本体を更新したら全利用リポジトリへ即時反映される（`@main` 参照のため）。安定運用したい場合は `@v1` などのタグ参照に切り替える。
- このリポジトリが Private の場合、Organization の Actions 設定で他リポジトリからの参照を許可する必要がある（Public なら不要）。
