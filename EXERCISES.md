# 練習課題（EXERCISES）

このリポジトリは **FastAPI + SQLModel + SQLite** で作った TODO の CRUD API の学習教材。
`app/` にお手本のコードが完成済み。

> **進め方**
> まず **お手本(`app/`)を読んで理解する**こと。`models.py` → `schemas.py` → `database.py` → `main.py` の順がおすすめ。
> 仕組みが分かったら、この課題を **上から順に解く**。1つ解けたら次へ進む。
> いきなり全部やろうとせず、1課題ずつ「動く」ところまで確認してから先へ。

## お手本の今の仕様（変更前のスタート地点）

- `Todo` モデルのカラム: `id` / `title` / `done` / `created_at`（**`assignee` は無い**）
- エンドポイント（すべて `/todos`）:
  - `POST /todos` … 作成
  - `GET /todos` … 一覧
  - `GET /todos/{id}` … 1件取得（無ければ 404）
  - `PATCH /todos/{id}` … 更新（`title` / `done`）
  - `DELETE /todos/{id}` … 削除
- 主なファイル: `app/models.py` / `app/schemas.py` / `app/database.py` / `app/main.py`
- パッケージ管理は **uv**
  - テスト実行: `uv run pytest`
  - サーバ起動: `uv run uvicorn app.main:app --reload`（→ http://127.0.0.1:8000/docs で試せる）

---

## 課題1【誰のタスクか】担当者カラムを追加する

### ゴール
`Todo` に「担当者名」を持たせ、作成時に担当者を指定でき、取得時に担当者が返ってくるようにする。

### やること
- `app/models.py`: `Todo` に `assignee: str`（担当者名）カラムを追加する。
- `app/schemas.py`: 入力用 `TodoCreate` と出力用 `TodoRead` の**両方**に `assignee` を反映する。
  - 作成時に受け取りたい（`TodoCreate`）／レスポンスで返したい（`TodoRead`）の両方が必要。
- `app/main.py`: `create_todo` で受け取った `assignee` を `Todo` に渡して保存する。
- **DBの作り直し**を行う（下のヒント必読）。

### ヒント
- カラム追加は `models.py` のクラスに 1 行足すだけ。型は `str`。
- 「必須にする」か「任意（デフォルト値あり）」かで書き方が変わる。まずは必須でよい。
  - 任意にしたいなら `Field(default=...)` のようにデフォルトを持たせる発想。
- **重要 — SQLite は既存テーブルに列を自動追加しない**:
  - お手本の `init_db()` は `create_all` で「テーブルが無ければ作る」だけ。**すでにある `todo.db` には新しい列は足されない**。
  - そのため、モデルだけ直しても古い `todo.db` のままだと、保存・取得でカラム不一致のエラーになる。
  - **学習用なので、いちばん簡単なのは `todo.db` ファイルを削除して作り直す方法**。
    プロジェクト直下の `todo.db` を消して（`*.db` は `.gitignore` 済み）、サーバを再起動すれば新しい形でテーブルが作り直される。
    - 中身のデータは消えるが、練習用なので問題ない。
  - 本番ではこういうとき「マイグレーション」（列だけ後から足す）を使う。これは発展課題で扱う。
- `models.py`（テーブルの形）と `schemas.py`（API入出力の形）は**役割が別**。両方直す必要がある理由を、お手本のコメントで確認しておくと理解が深まる。

### 確認方法
- サーバ起動後、担当者付きで作成してみる:
  ```bash
  curl -X POST http://127.0.0.1:8000/todos \
    -H "Content-Type: application/json" \
    -d '{"title": "資料作成", "assignee": "田中"}'
  ```
  → レスポンスに `"assignee": "田中"` が含まれること。
- `curl http://127.0.0.1:8000/todos` で一覧を取り、`assignee` が返ってくること。
- `assignee` を省いてエラーになるか（必須にした場合）も試す。

---

## 課題2【担当者でフィルタ】クエリパラメータで絞り込む

### ゴール
`GET /todos?assignee=田中` のように、担当者を指定して TODO を絞り込めるようにする。
指定しなければ今まで通り全件返す。

### やること
- `app/main.py`: `list_todos` に「担当者名」のクエリパラメータ（任意）を追加する。
  - パラメータが渡されたときだけ、その担当者のものに絞る。
  - 渡されなければ全件返す（今の挙動を壊さない）。

### ヒント
- FastAPI のクエリパラメータ: 関数の引数にデフォルト値付きで書くと、URL の `?key=value` を受け取れる。
  - 任意にしたいので `str | None = None`（Optional）の形。
- SQLModel の絞り込み: `select(Todo).where(...)` を使う。
  - 「パラメータがあるときだけ `where` を足す」という分岐を書く。
  - `select` した文に対して、条件があるときだけ `.where(Todo.assignee == ...)` を追加する発想。

### 確認方法
- 担当者違いを2件以上作ってから:
  ```bash
  curl "http://127.0.0.1:8000/todos?assignee=田中"
  ```
  → 田中のものだけ返ること。
- パラメータ無し `curl http://127.0.0.1:8000/todos` で全件返ること。
- 存在しない担当者を指定すると空リスト `[]` が返ること。

---

## 課題3【正規化】Userテーブルを新設して外部キーにする

### ゴール
担当者を「ただの文字列」ではなく、独立した `User` テーブルで管理する。
`Todo` は担当者を**文字列 `assignee` ではなく、`User` への外部キー `user_id` で**持つように置き換える。

### やること
- `app/models.py`:
  - `User` テーブルを新設する（最低限 `id` と `name`）。
  - `Todo` の `assignee`（文字列）を `user_id`（`User.id` への外部キー）に置き換える。
  - 任意で、`Todo` ↔ `User` を行き来できる **リレーション** を張る。
- `app/schemas.py`: 入出力を `user_id` ベースに直す（作成時に `user_id` を受け取る、など）。
- `app/main.py`: 作成・取得まわりを `user_id` ベースに直す。
- `todo.db` を作り直す（課題1と同じ理由。`User` テーブルが増えるため）。

### ヒント
- 外部キー: `Field(foreign_key="user.id")` のように、参照先テーブル名.列名を文字列で指定する。
  - SQLModel はクラス名を小文字にしたものをテーブル名にする（`User` → `user`）。
- リレーション: `Relationship(back_populates=...)` で双方向に紐づけられる。
  - `User` 側に「その人の Todo 一覧」、`Todo` 側に「担当 User」を持たせるイメージ。
- まず `User` を作っておかないと、その `user_id` を持つ `Todo` は作れない（外部キー制約）。先に `User` を1件作る流れを考える。
- 「正規化」= 同じ担当者名をあちこちに文字列でコピーせず、`User` に1か所だけ持つ、という考え方。

### 確認方法
- `User` を作る手段（新しいエンドポイントを足す or 起動時に投入）を用意してから、その `id` を使って `Todo` を作る。
- `GET /todos/{id}` で `user_id` が返ること。
- リレーションを張ったなら、`User` から担当 Todo 一覧をたどれること（Python のテストや `/docs` で確認）。
- 存在しない `user_id` で `Todo` を作ろうとしたときの挙動も観察する。

---

## 課題4【期限】due_date と「期限切れ一覧」

### ゴール
TODO に期限 `due_date` を持たせ、`GET /todos/overdue` で**期限切れ（今より前が期限）の TODO だけ**返せるようにする。

### やること
- `app/models.py`: `due_date`（`datetime`、**任意＝nullable**）を `Todo` に追加する。
- `app/schemas.py`: 作成入力・出力に `due_date` を反映する（任意なのでデフォルト `None`）。
- `app/main.py`:
  - 作成時に `due_date` を受け取って保存する。
  - 新しいエンドポイント `GET /todos/overdue` を追加し、期限切れのものだけ返す。
- `todo.db` を作り直す。

### ヒント
- nullable な日時: 型を `datetime | None`、デフォルト `None` にする。
- 「期限切れ」= `due_date` が**現在時刻より前**で、かつ `due_date` がある（`None` ではない）もの。
- 現在時刻は `datetime.now()`。これと `Todo.due_date` を `where` で比較する。
  - `select(Todo).where(Todo.due_date < datetime.now())` のような発想。`None` を除く条件も忘れずに。
- **ルート定義の順番に注意**: `GET /todos/{todo_id}` より**前**に `GET /todos/overdue` を定義する。
  - 後ろに書くと `overdue` が `{todo_id}` に吸われて `int` 変換エラーになりがち。なぜそうなるか考えてみる。

### 確認方法
- 過去日時の期限と、未来日時の期限の TODO を1件ずつ作る:
  ```bash
  curl -X POST http://127.0.0.1:8000/todos \
    -H "Content-Type: application/json" \
    -d '{"title": "締切すぎ", "due_date": "2020-01-01T00:00:00"}'
  ```
- `curl http://127.0.0.1:8000/todos/overdue` で**過去日のものだけ**返ること。
- 未来日のものや `due_date` 無しのものが含まれないこと。

---

## 課題5【発展: テスト】追加機能のテストを書く

### ゴール
課題1〜4で追加した機能それぞれに pytest を書き、`uv run pytest` が全部通る状態にする。

### やること
- `tests/test_todos.py`（または新しいテストファイル）に、以下を検証するテストを足す:
  - 課題1: `assignee` 付きで作成 → レスポンスに `assignee` が返る。
  - 課題2: 担当者でフィルタ → 指定した担当者のものだけ返る／無指定で全件。
  - 課題3: `User` を作って `user_id` で `Todo` を作れる／リレーションをたどれる。
  - 課題4: 期限切れと未来期限を作り、`/todos/overdue` が期限切れだけ返す。

### ヒント
- 既存の `tests/test_todos.py` の書き方をそのまま真似る。
  - インメモリ DB の `session` フィクスチャと、`TestClient` の `client` フィクスチャがすでにある。
- テストが本番 `todo.db` を汚さない仕組み = **`dependency_overrides`** で `get_session` を差し替えている。お手本のコメントを読んで理解する。
- 課題3/4で `select` や日時比較を入れた場合、テスト側のインメモリ DB でも同じテーブル定義が `create_all` で作られることを確認する。
- 日時のテストは「今より明確に前／後」の固定値を使うとブレない。

### 確認方法
- `uv run pytest` で**既存テストを含め全部 PASS** すること。
- わざと条件を外したデータを入れて、フィルタや overdue が**間違ったものを返さない**ことも1ケース入れると堅い。

---

## 全部解けたら（さらなる発展）

- **認証**: ユーザーログイン（トークン認証）を入れて、自分の TODO だけ見えるようにする。
- **ページネーション**: `GET /todos?limit=&offset=` で件数を区切って返す。
- **本格マイグレーション**: 列追加のたびに DB を消す代わりに、**Alembic** でマイグレーションを管理する。
