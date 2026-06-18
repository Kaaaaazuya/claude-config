---
name: commit
description: Conventional Commits 1.0.0 準拠のコミットメッセージを作成してコミットする。ユーザーが「コミットして」「commit して」と言ったときや、コミットメッセージを書く必要があるときに使う。
---

# commit — Conventional Commits 準拠でコミットする

コミットメッセージを **Conventional Commits 1.0.0** で統一する。

## フォーマット

```
<type>(<scope>): <subject>

<body>            # 任意。なぜ/何を。1行空けて書く

<footer>          # 任意。Refs / BREAKING CHANGE / Co-Authored-By
```

例:
```
feat(auth): JWT によるセッション管理を実装

有効期限を環境変数で設定できるようにし、リフレッシュトークンも発行する。
既存の cookie セッションとの互換性は維持しない（BREAKING CHANGE）。

BREAKING CHANGE: cookie セッションを廃止。クライアントの再実装が必要。
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

## type（必須・1つだけ選ぶ）

| type | 用途 |
|---|---|
| `feat` | 機能追加 |
| `fix` | バグ修正 |
| `docs` | ドキュメントのみの変更 |
| `style` | 動作に影響しない整形（空白・フォーマット） |
| `refactor` | 挙動を変えないコード改善 |
| `perf` | パフォーマンス改善 |
| `test` | テストの追加・修正 |
| `build` | ビルド・依存関係 |
| `ci` | CI 設定 |
| `chore` | その他雑務（初期化・設定ファイル等） |
| `revert` | コミットの取り消し |

変更が複数 type にまたがる場合は、主たる変更の type を1つ選ぶ（混ぜない。分けられるならコミットを分割する）。

## scope（任意）

プロジェクトのレイヤー・モジュール名を自由に使う（例: `api` / `ui` / `db` / `auth` / `infra`）。
該当する層がなければ省略してよい。

## subject（必須）

- 日本語でよい。**命令形・簡潔に**（「〜を実装」「〜を修正」）。
- **約50字以内**。末尾に句点「。」を付けない。
- 「何をしたか」が一目で分かること。

## body（任意）

- subject の後に**1行空けて**書く。**なぜ / 何を**変えたかを説明（how より why）。
- 1行は概ね72字で折り返す。

## footer（任意だが規約あり）

- **破壊的変更**: `BREAKING CHANGE: <説明>`（または type の後ろに `!`、例 `feat!:`）。
- **Co-Authored-By（必須）**: Claude が作るコミットの末尾に必ず付ける:
  ```
  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  ```

## 手順

1. `git status` と `git diff --staged`（未ステージなら `git diff`）で変更内容を把握する。
2. ステージされていなければ、コミット対象を確認の上 `git add` する。
3. 上記ルールで type / scope / subject / body / footer を組み立てる。
4. **コミット前に最終メッセージをユーザーに提示**してから `git commit` する。
5. pre-commit フックが失敗したら、原因を解消してから再コミットする。**フックを `--no-verify` で迂回しない。**

## 禁止事項

- 規約を無視した自由形式メッセージ。
- `--no-verify` でのフック迂回。
- 1コミットに無関係な変更を混ぜること。
