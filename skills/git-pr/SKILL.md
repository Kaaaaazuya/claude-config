---
name: git-pr
description: |
  GitHub Pull Request を作成する。「PRを作って」「プルリクエスト作成」「git pr」「/git-pr」「PR出して」「マージリクエスト作って」と言われたら必ずこのスキルを使う。
  現在ブランチの変更をまとめ、タイトル・本文を自動生成して `gh pr create` で PR を作成する。
  実装作業の締めくくりや「変更をレビューに出したい」という文脈でも自律的に発動すること。
---

# git-pr — GitHub PR を作成する

## 手順

### 1. 現在の状態を把握する

以下を並行して実行する:

```bash
git status
git log main..HEAD --oneline   # main が存在しない場合は master や origin/HEAD で代替
git diff main..HEAD --stat
```

未コミットの変更がある場合は、まずコミットするか確認する（`commit` スキルを使う）。

### 2. リモートへ push する

現在のブランチがリモートに存在しない、または upstream が未設定の場合:

```bash
git push -u origin HEAD
```

すでに push 済みなら push は不要。ただし未 push のコミットがあれば push する。

### 3. PR タイトルと本文を組み立てる

**タイトル**: Conventional Commits 形式 — `<type>(<scope>): <日本語summary>`

- `git log` で変更の主旨を把握し、最も適切な type を選ぶ
- 70字以内に収める

**本文テンプレート**:

```markdown
## Summary
- <変更点を箇条書き（3点以内）>

## Test plan
- [ ] <確認すべき動作>
- [ ] <確認すべき動作>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

Summary はコミット群から変更の意図を読み取って書く。Test plan は変更内容から影響範囲を推測して書く。

### 4. PR を作成する

```bash
gh pr create --title "<title>" --body "$(cat <<'EOF'
<body>
EOF
)"
```

### 5. URL をユーザーに伝える

作成完了後、PR の URL をマークダウンリンク形式で返す。

---

## 注意事項

- `--no-verify` でフックを迂回しない。
- force push は行わない。
- draft PR にするかどうかは、ユーザーが「ドラフトで」「draft で」と言った場合のみ `--draft` を付ける。
- base ブランチは通常 `main`。別のブランチを指定された場合は `--base <branch>` を使う。
