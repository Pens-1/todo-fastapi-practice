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
http://127.0.0.1:8000/         お手本フロント（TODO アプリの画面）
http://127.0.0.1:8000/docs     Swagger UI（各 API を画面から試せる）
```

- `/` を開くと、素の HTML/CSS/JS だけで作った**お手本フロント**が表示されます。
  実体は `app/static/index.html` にあり、`fetch` で `/todos` API を叩いて
  作成・一覧・完了トグル・削除を行います（依存ライブラリ・CDN なし）。
- `/docs` には **Swagger UI** が表示され、各エンドポイントを画面上からそのまま試せます。

（初回起動時、データベース `todo.db` が無ければ自動的に作られます。）

> **メモ:** このフロントはあくまで「お手本」です。`assignee` 入力欄の追加など
> フロント側の機能拡張は、`EXERCISES.md` のバックエンド課題を解き終えてから
> 自分で挑戦してみてください。

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
│   ├── main.py         # FastAPI 本体の組み立て（lifespan・/ でフロント配信・ルーター登録）
│   ├── database.py     # DB 接続・セッション・テーブル作成
│   ├── models.py       # DB テーブルの形（Todo モデル）
│   ├── schemas.py      # API 入出力の形（スキーマ）
│   ├── crud.py         # DB 操作そのもの（読み書き関数を集約）
│   ├── routers/        # エンドポイント（HTTP の入口）
│   │   ├── __init__.py
│   │   └── todos.py    # /todos 系のルーター（薄い層・404 判定はここ）
│   └── static/
│       └── index.html  # お手本フロント（素の HTML/CSS/JS）
├── tests/              # pytest のテスト
│   └── test_todos.py
├── EXERCISES.md        # 自分で解く課題集
├── pyproject.toml      # 依存・設定
└── README.md           # このファイル
```

## 学習の進め方

上から順に進めるのがおすすめです。

1. **`app/` のコードを読む**
   `models.py` → `schemas.py` → `database.py` → `crud.py` → `routers/todos.py` → `main.py`
   の順に読むと、「テーブルの形 → 入出力の形 → DB 接続 → DB 操作 → HTTP の入口 → 組み立て」
   と理解しやすいです。各ファイルには日本語のコメントが付いています。
   - `crud.py` … DB の読み書きそのもの（HTTPException は投げない）
   - `routers/todos.py` … URL・ステータスコード・404 判定など HTTP の入口（crud を呼ぶ薄い層）
   - `main.py` … 上記を組み立てるだけ（`include_router` でルーターを登録）

2. **`tests/` を読む**
   テストを読むと「この API はどう呼ばれ、何を返すのが正しいのか」が具体的に分かります。
   `uv run pytest` で実際に動かして、全部通ることを確認しましょう。

3. **`EXERCISES.md` の課題を順に解く**
   お手本を真似しながら、自分で機能を足していきます。
   最初の課題は「**誰のタスクか（`assignee`）を DB に追加する**」です。
   `models.py` / `schemas.py` / `crud.py` / `routers/todos.py` のどこをどう直せばいいか、
   お手本を手がかりに考えてみてください。
