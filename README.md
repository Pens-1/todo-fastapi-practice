# TODO 練習 API（FastAPI + SQLModel ハンズオン教材）

FastAPI と SQLModel を**手を動かして**学ぶための教材です。
SQLite に TODO を保存する小さな CRUD API を題材に、

1. まず `app/` の**お手本コード**を読んで仕組みを理解し、
2. 次に `EXERCISES.md` の**課題を上から順に解いて**自分で機能を足していく、

という流れで進めます。

## このアプリでできること

`app/` には、お手本として 5 つのエンドポイント（API の入口）が実装されています。

| メソッド | パス            | 内容                          |
| -------- | --------------- | ----------------------------- |
| `POST`   | `/todos`        | TODO を 1 件作成              |
| `GET`    | `/todos`        | TODO を一覧取得              |
| `GET`    | `/todos/{id}`   | 指定 id の TODO を 1 件取得  |
| `PATCH`  | `/todos/{id}`   | 指定 id の TODO を更新（`title` / `done`） |
| `DELETE` | `/todos/{id}`   | 指定 id の TODO を削除       |

TODO 1 件が持つ項目は次の 4 つです。

- `id` … 主キー（DB が自動採番）
- `title` … タスクのタイトル
- `done` … 完了したかどうか（デフォルト `false`）
- `created_at` … 作成日時（自動で入る）

> **メモ:** お手本には「誰のタスクか（`assignee`）」はあえて入れていません。
> それを追加するのが `EXERCISES.md` の最初の課題です。

## 必要環境

- Python 3.12
- [uv](https://docs.astral.sh/uv/)（パッケージ・仮想環境の管理ツール）

uv が未インストールの場合は、公式手順に従って入れてください。

## セットアップ

依存パッケージのインストールと仮想環境の作成を、まとめて行います。

```bash
uv sync
```

## 起動方法

開発用サーバ（`--reload` でコード変更時に自動再起動）を起動します。

```bash
uv run uvicorn app.main:app --reload
```

起動したらブラウザで以下を開いてください。

```
http://127.0.0.1:8000/docs
```

**Swagger UI** が表示され、各エンドポイントを画面上からそのまま試せます。
（初回起動時、データベース `todo.db` が無ければ自動的に作られます。）

## 動作確認（curl 例）

別のターミナルを開き、サーバを起動したまま以下を順に試してください。

### 1. 作成（POST）

```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "牛乳を買う"}'
```

### 2. 一覧取得（GET）

```bash
curl http://127.0.0.1:8000/todos
```

### 3. 1 件取得（GET）

```bash
curl http://127.0.0.1:8000/todos/1
```

### 4. 更新（PATCH） — 完了にする

```bash
curl -X PATCH http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

> `PATCH` は「送った項目だけ」更新します。`done` だけ送れば `done` だけ書き換わります。

### 5. 削除（DELETE）

```bash
curl -X DELETE http://127.0.0.1:8000/todos/1
```

削除に成功すると、本文なしの `204 No Content` が返ります。

## テスト

pytest でテストを実行します。

```bash
uv run pytest
```

## ディレクトリ構成

```
todo-fastapi-practice/
├── app/                # お手本コード（まずここを読む）
│   ├── __init__.py
│   ├── main.py         # FastAPI 本体・エンドポイント定義
│   ├── database.py     # DB 接続・セッション・テーブル作成
│   ├── models.py       # DB テーブルの形（Todo モデル）
│   └── schemas.py      # API 入出力の形（スキーマ）
├── tests/              # pytest のテスト
│   └── test_todos.py
├── EXERCISES.md        # 自分で解く課題集
├── pyproject.toml      # 依存・設定
└── README.md           # このファイル
```

## 学習の進め方

上から順に進めるのがおすすめです。

1. **`app/` のコードを読む**
   `models.py` → `schemas.py` → `database.py` → `main.py` の順に読むと、
   「テーブルの形 → 入出力の形 → DB 接続 → エンドポイント」と理解しやすいです。
   各ファイルには日本語のコメントが付いています。

2. **`tests/` を読む**
   テストを読むと「この API はどう呼ばれ、何を返すのが正しいのか」が具体的に分かります。
   `uv run pytest` で実際に動かして、全部通ることを確認しましょう。

3. **`EXERCISES.md` の課題を順に解く**
   お手本を真似しながら、自分で機能を足していきます。
   最初の課題は「**誰のタスクか（`assignee`）を DB に追加する**」です。
   `models.py` / `schemas.py` / `main.py` のどこをどう直せばいいか、お手本を手がかりに考えてみてください。
