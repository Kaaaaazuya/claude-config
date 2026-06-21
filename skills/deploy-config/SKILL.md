---
name: deploy-config
description: >-
  ~/local/claude-config リポジトリの skills・agents・CLAUDE.md を ~/.claude/ にデプロイする。
  「/deploy-config」「設定を反映して」「スキルを有効化して」「各リポジトリに反映して」と言われたら起動する。
---

# deploy-config

`~/local/claude-config` リポジトリの内容を `~/.claude/` にコピーし、全プロジェクトで有効化する。

## 実行手順

1. **差分を確認する**

   リポジトリと `~/.claude/` の状態を比べて何が変わるかを提示する。

   ```bash
   diff -rq ~/local/claude-config/skills/ ~/.claude/skills/ 2>/dev/null
   diff -rq ~/local/claude-config/agents/ ~/.claude/agents/ 2>/dev/null
   ```

2. **ユーザーに確認してからデプロイする**

   差分を提示し、問題なければ以下を実行する。

   ```bash
   cp -r ~/local/claude-config/skills/*/  ~/.claude/skills/
   cp -r ~/local/claude-config/agents/    ~/.claude/agents/
   ```

   CLAUDE.md はシムリンクで管理されているため上書きしない。
   シムリンクが切れている場合のみ再作成を提案する。

   ```bash
   # シムリンク確認
   ls -la ~/.claude/CLAUDE.md
   ```

3. **PR を作成する**

   `main` ブランチに未プッシュのコミットがあれば、feature ブランチを切って PR を作成する。

   ```bash
   # 未プッシュコミットの確認
   git -C ~/local/claude-config log origin/main..HEAD --oneline
   ```

   未プッシュコミットがある場合:

   a. `feature/deploy-YYYYMMDD` ブランチを作成してコミットを移す
   b. `gh pr create` で PR を作成する。タイトル・本文は変更内容から生成する
   c. PR の URL をユーザーに提示する
   d. **マージはしない**。レビュー・マージはユーザーが行う

   未プッシュコミットがない場合はスキップする。

4. **デプロイ結果を報告する**

   ```
   ## deploy-config 完了

   デプロイ済みスキル: X 個
   デプロイ済みエージェント: X 個
   スキップ: CLAUDE.md（シムリンク管理）
   PR: <URL>（またはスキップ）
   ```

## 注意

- `~/.claude/skills/` にリポジトリにない独自スキル（`git-commit`, `pii-check`, `sync-docs` など）が
  ある場合は上書きしない。`cp -r` はディレクトリ単位でコピーするため既存の独自スキルは保持される
- hooks は設定依存が大きいため自動デプロイしない。必要な場合はユーザーに手順を案内する
- `settings.json` は上書きしない（各プロジェクトの設定を壊さないため）
