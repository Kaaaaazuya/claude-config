---
name: skill-builder
description: |
  スキル生成エンジン（meta-skill）。logs/skill-candidates.json（機械的検出）と
  logs/retro-candidates.md（意味的抽出）を入力に、人間が承認したパターンを
  draft 状態の SKILL.md として生成する。/skill-builder または /skill-build で呼び出す。
---

# skill-builder スキル

## 入力（2 系統）

1. `logs/skill-candidates.json` — pattern_detector による機械的なコマンド頻度
2. `logs/retro-candidates.md` — retro-codify による意味的な学びの抽出

## 実行手順

1. 上記 2 ファイルを Read で読み込み、候補を統合してユーザーに提示する
2. **ユーザーにスキル化するものを選択させる**（自動では選ばない）
3. 選択されたパターンについて以下を決定する:
   - スキル名（kebab-case）
   - description（いつ自律発動するかを自然言語で）
   - 実行手順（再現可能なステップ形式）
   - 出力フォーマット

4. `.claude/skills/{name}/SKILL.md` を Write で生成する

5. **同時に `.claude/skills/{name}/meta.json` を生成する:**

```json
{
  "name": "{name}",
  "status": "draft",
  "created_at": "{ISO8601}",
  "source": "pattern_detector | retro-codify | manual",
  "use_count": 0,
  "success_count": 0,
  "last_used_at": null,
  "promoted_at": null
}
```

6. CLAUDE.md の「利用可能なスキル」テーブルに **(draft) タグ付きで** 追記提案する

7. **claude-config リポジトリに PR を作成する:**

   ```
   CLAUDE_CONFIG_REPO=~/local/claude-config
   ```

   以下の手順で実行する:

   a. `$CLAUDE_CONFIG_REPO` に移動し、`main` ブランチが最新であることを確認する
   b. `feature/skill-{name}` ブランチを作成してチェックアウト
   c. 生成した `SKILL.md`（と `meta.json`）を `$CLAUDE_CONFIG_REPO/skills/{name}/` にコピー
   d. コミット（メッセージ例: `feat(skills): {name}スキルを追加`）
   e. `gh pr create` で PR を作成する。タイトル・本文はスキルの description と手順概要から生成する
   f. PR の URL をユーザーに提示する
   g. **マージはしない**。レビュー・マージはユーザーが行う

   > claude-config リポジトリが見つからない場合はスキップしてその旨を伝える。

## 品質チェック（生成前に確認）

- description は「いつ発動するか」が明確か
- 手順は誰が読んでも再現できるか（「直感的に」等の曖昧語がないか）
- `.claude/skills/` 以下の既存スキルと重複していないか
- 問題解決・再現性・新規性の 3 要件を満たすか

## 注意

draft 状態のスキルは「試用中」を意味する。
昇格（draft → active）は人間が評価データを元に判断し、承認したときだけ行う。
スキルを自動で active にしない。
