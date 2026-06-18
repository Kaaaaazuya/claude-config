# claude-config

プロジェクト横断で使う Claude Code のスキル・フック・パーミッション設定をまとめたリポジトリ。

## 構成

```
skills/
  commit/SKILL.md     # Conventional Commits 準拠コミット
  allowlist/SKILL.md  # 許可コマンドの抽出・管理
hooks/
  notify.sh           # 入力待ち時のデスクトップ通知（macOS / Linux）
  ruff-format.sh      # .py 編集直後に Ruff で自動整形（uv プロジェクト用）
settings.json         # 汎用パーミッション設定テンプレート
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
