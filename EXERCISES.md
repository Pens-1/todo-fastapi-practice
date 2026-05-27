# 練習課題（EXERCISES）— 手取り足取り版

このリポジトリは **FastAPI + SQLModel + SQLite** で作った TODO の CRUD（作成・取得・更新・削除）API の学習教材。
`app/` に**お手本のコードが完成済み**なので、まずはそれを動かして・読んで・少しずつ自分で足していく。

> **このファイルの読み方（とても大事）**
> いきなりコードをガリガリ書く必要はない。
> 最初に **「準備運動」**（コードをほぼ書かない・触って慣れるだけ）をやり、
> そのあと **「本編課題」**（1〜数行ずつ穴埋めで足していく）に進む。
> どの課題も **「どのファイルの・どこに・何を書くか」** を細かく示している。
> 各ステップに **「✅ できたか確認」** が付いているので、1個ずつ確認しながら進めば必ずゴールにたどり着ける。

---

## まず用語をやさしく（迷ったらここに戻る）

- **エンドポイント / API の入口**: 「この URL にこういうリクエストを送ると、こう返ってくる」という窓口のこと。例: `POST /todos` は「TODO を作る窓口」。
- **モデル（model）**: DB（データベース＝データの保管庫）のテーブル（表）の形。`app/models.py` にある。
- **スキーマ（schema）**: API でやりとりする入力・出力の形。`app/schemas.py` にある。**モデルとは役割が別**（後でわかる）。
- **CRUD**: Create（作る）/ Read（読む）/ Update（更新）/ Delete（消す）の頭文字。
- **クエリパラメータ**: URL の `?` 以降のオプション指定。例: `/todos?assignee=田中` の `assignee=田中` の部分。
- **nullable（ヌラブル）**: 「空っぽ（未入力）でもOK」な項目のこと。逆に「必須」は空っぽが許されない。
- **外部キー（foreign key）**: 別のテーブルの行を「指し示す」ための値。発展課題で出てくる。
- **マイグレーション**: DB の形（列など）を後から安全に変える作業。これも発展課題。

---

# 第0部：準備運動（コードはほぼ書かない）

ここはウォーミングアップ。**お手本を起動して触る・読む**だけ。ここを飛ばさないこと。慣れておくと本編が一気にラクになる。

> **コマンドの打ち方には A / B の2通りがある**
> このリポジトリは2通りの環境に対応している。**自分の環境に合うほうだけ**を使えばよい。
> - **A. `venv` + `pip`**（標準ツールだけ。`uv` を入れていない人はこちら）
>   先に仮想環境を有効化（`.\.venv\Scripts\Activate.ps1`）した状態でコマンドを打つ。
> - **B. `uv`**（速い。入っている人はこちら）。コマンドの先頭に `uv run` を付ける。
>
> セットアップ（仮想環境作成・依存インストール）の手順は **README.md** にある。まだの人は先にそちらを済ませること。

## 準備運動0：お手本を起動して、ブラウザで触ってみる

**目標**: サーバを立ち上げて、ブラウザの画面から TODO を作る・完了にする・消す、を体験する。

### ステップ 0-1：サーバを起動する

ターミナル（PowerShell）で、プロジェクトのフォルダにいる状態で次を実行する。

```
A（venv + pip。先に仮想環境を有効化しておく）:
  uvicorn app.main:app --reload

B（uv）:
  uv run uvicorn app.main:app --reload
```

`Application startup complete.` のような表示が出たら起動成功。
**このターミナルは開いたまま**にしておく（閉じるとサーバが止まる）。

✅ できたか確認：エラーで止まらず、起動メッセージが出ている。

### ステップ 0-2：ブラウザでお手本フロントを開く

ブラウザで次を開く。

```
http://127.0.0.1:8000/
```

TODO アプリの画面（お手本フロント）が出る。
入力欄にタイトルを打って追加 → 一覧に出る → チェックで完了 → 削除、を実際にやってみる。

✅ できたか確認：作成・完了・削除がブラウザの画面で動く。

### ステップ 0-3：Swagger UI（API を画面から試せるページ）を開く

別のタブで次を開く。

```
http://127.0.0.1:8000/docs
```

`POST /todos` や `GET /todos` などの一覧が出る。
試しに `POST /todos` を開いて「Try it out」→ `title` を入れて「Execute」してみる。下に結果（レスポンス）が出る。

> **メモ**: この `/docs` ページは、コードを書かずに API を試せる超便利ツール。本編課題でも「curl の代わりに /docs で試す」でOK。

✅ できたか確認：`/docs` で TODO を1件作れて、`GET /todos` に出てくる。

---

## 準備運動1：どのファイルが何の役割か（読むだけクイズ）

**目標**: コードは書かない。お手本を開いて「どのファイルが何担当か」を頭に入れる。
下の穴埋めクイズに、**実際にファイルを開いて**答えを確認しよう（答え合わせは自分でファイルを見ること）。

| ファイル | 役割（一言で） |
| --- | --- |
| `app/models.py` | DB の **テーブルの形**（`Todo` クラス）。`id` / `title` / `done` / `created_at` がある |
| `app/schemas.py` | API の **入力・出力の形**（`TodoCreate` / `TodoRead` / `TodoUpdate`） |
| `app/database.py` | DB への **接続・セッション・テーブル作成** |
| `app/crud.py` | **DB の読み書きそのもの**。`HTTPException`（404 など）は**投げない** |
| `app/routers/todos.py` | **HTTP の入口**。URL・ステータスコード・**404 判定**はここ。crud を呼ぶ薄い層 |
| `app/main.py` | アプリの **組み立てだけ**（フロント配信・ルーター登録）。ロジックは置かない |

### 穴埋めクイズ（答えはコードを開いて確認）

1. 「TODO を保存する処理（DB に書き込む）」は、`routers/todos.py` と `crud.py` の **どっち** に書いてある？
   → ヒント: `create_todo` という関数を両方のファイルで探してみる。「実際に `session.add` して保存している」のはどっち？
2. 「`done` のデフォルトが `False`」はどのファイルのどこで決まっている？（複数あるかも）
   → ヒント: `models.py` と `schemas.py` の両方に `done` が出てくる。`Field(default=False)` や `done: bool = False` を探す。
3. 「id が無いとき 404 を返す」判定は、`crud.py` と `routers/todos.py` の **どっち** に書いてある？
   → ヒント: `raise HTTPException(status_code=404` を grep（検索）してみる。

✅ できたか確認：上の3問を、**自分でファイルを開いて**答えられた。

> **覚えておくと得すること（本編でずっと使う）**
> このお手本は **「DB 操作 = `crud.py`」「HTTP の入口 = `routers/todos.py`」** にきれいに分かれている。
> だから本編では **「DB の話は crud、URL や 404 の話は routers」** と覚えておけば、どこを直せばいいか迷わない。

---

## 準備運動2：ごく小さな「探す」体験

**目標**: コードを壊さずに、「設定がどこで決まっているか」を1つだけ自分で突き止める。

お題：**新しく作った TODO の `done` が、最初なぜ `False`（未完了）になるのか？**

1. `app/schemas.py` を開く。`TodoCreate` の中に `done: bool = False` という行がある。
   → これは「作成時に `done` を省略したら `False` 扱いにする」という意味。
2. `app/models.py` を開く。`done: bool = Field(default=False)` という行がある。
   → これは「DB のテーブルとしても、初期値は `False`」という意味。
3. つまり、**入力の形（schemas）でも、テーブルの形（models）でも `False` がデフォルト**になっている。

✅ できたか確認：「`done` のデフォルト `False` は schemas と models の両方で決まっている」と説明できる。

> **これで準備運動は完了！** 「どこを見ればいいか」の地図が頭に入ったはず。
> ここまで来たら、もうあなたは本編課題を進められる。次へ！

---

# 第1部：本編課題（やさしい順・1〜数行ずつ穴埋め）

> **進め方のコツ**
> - 課題は **上から順に**やる。1つ終わったら必ずブラウザ or `/docs` で動かして確認してから次へ。
> - コードは **骨格（まわりの行）を見せる**ので、**空欄 `# ここに ○○ を書く` だけ**を自分で埋める。
> - 詰まったら、お手本の似た処理（`title` の扱いなど）を真似する。

---

## 課題1【担当者を足す】`assignee`（担当者名）を追加する ← 最重要・いちばん丁寧に

### この課題のゴール
TODO に「担当者名（`assignee`）」を持たせる。
作成時に担当者を指定でき、取得したときに担当者名が返ってくるようにする。

> **なぜ models と schemas の両方を直すのか？**
> `models.py` は **DB のテーブルの形**、`schemas.py` は **API の入出力の形**。役割が別なので、**両方**に `assignee` を足す必要がある。
> 「テーブルに列を足す」だけでは API が受け取ってくれないし、「API の形だけ直す」だけでは DB に保存場所が無い。

### ステップ 1-1：`models.py` に列を足す（DB のテーブルに `assignee` を追加）

`app/models.py` の `Todo` クラスを開く。`title` の行のすぐ下あたりに、新しい行を1行足す。

```python
class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)

    # ↓ この1行を追加する。担当者名（必須・文字列）。
    # ここに assignee の列を書く（ヒント: title の行を真似して、型は str）
    # 例の形:  assignee: str

    done: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
```

> **補足**: まずは `assignee: str`（必須）でOK。
> 「省略してもいい（任意）」にしたいなら `assignee: str = Field(default="")` のようにデフォルト値を持たせる。最初は必須で進めると分かりやすい。

✅ できたか確認：`models.py` の `Todo` に `assignee` の行が1行増えた。

### ステップ 1-2：`schemas.py` の入力・出力の両方に足す

`app/schemas.py` を開く。**2か所**直す。

```python
class TodoCreate(SQLModel):
    title: str
    done: bool = False
    # ここに assignee を書く（ヒント: title と同じく str。作成時に受け取りたい項目）


class TodoRead(SQLModel):
    id: int
    title: str
    done: bool
    created_at: datetime
    # ここに assignee を書く（ヒント: レスポンスで返したい項目。型は str）
```

> **なぜ2か所？** `TodoCreate` は「作成時に**受け取る**形」、`TodoRead` は「**返す**形」。担当者は受け取りたいし返したいので、両方に要る。
> （`TodoUpdate` は今回いじらなくてOK。担当者の変更は後回しでよい。）

✅ できたか確認：`TodoCreate` と `TodoRead` の両方に `assignee` が増えた。

### ステップ 1-3：`crud.py` の `create_todo` で保存する

`app/crud.py` の `create_todo` を開く。`Todo(...)` を作っている行に `assignee` を足す。

```python
def create_todo(session: Session, todo_in: TodoCreate) -> Todo:
    # ↓ ここに assignee=todo_in.assignee を足す
    todo = Todo(title=todo_in.title, done=todo_in.done)  # ← この行に assignee を追記する
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
```

> **ヒント**: `Todo(title=todo_in.title, done=todo_in.done, assignee=todo_in.assignee)` のように、カンマ区切りで1項目足すだけ。

✅ できたか確認：`create_todo` の `Todo(...)` に `assignee=todo_in.assignee` が入った。

### ステップ 1-4：`routers/todos.py` は基本そのままでOK

`routers/todos.py` の `create_todo` は `crud.create_todo` を呼ぶだけの**薄い層**。入出力の形は schemas が面倒を見るので、**たいてい変更不要**。何もしなくてよい。

✅ できたか確認：routers は触っていない（それで正しい）。

### ステップ 1-5：⚠️ DB を作り直す（ここ超重要・必ず読む）

> **⚠️ 太字の警告：SQLite は既存テーブルに列を後から自動で足してくれない！**
> お手本の起動処理は「テーブルが**無ければ**作る」だけ。**すでにある `todo.db` には新しい `assignee` 列は足されない**。
> そのままだと「そんな列は無い」というエラーになる。

学習用なので、いちばん簡単な対処は **`todo.db` ファイルを消して作り直す**こと。

1. サーバを止める（起動中ターミナルで `Ctrl + C`）。
2. プロジェクト直下の **`todo.db` を削除**する（`*.db` は `.gitignore` 済みなので消してOK。中身のデータは消えるが練習用なので問題なし）。
3. サーバを再起動する（準備運動0のコマンド）。新しい形でテーブルが作り直される。

> 本番では DB を消す代わりに「マイグレーション」（列だけ後から足す）を使う。これは発展課題で扱う。

✅ できたか確認：`todo.db` を消して再起動し、エラーなく起動した。

### ステップ 1-6：動かして確認する

**方法A：`/docs` で試す（おすすめ・らくちん）**
`http://127.0.0.1:8000/docs` → `POST /todos` → 「Try it out」→ `title` と `assignee` を入れて Execute。
レスポンスに `"assignee": "田中"` が含まれていれば成功。

**方法B：curl で試す（PowerShell）**

```powershell
curl.exe -X POST http://127.0.0.1:8000/todos `
  -H "Content-Type: application/json" `
  -d '{"title": "資料作成", "assignee": "田中"}'
```

> **PowerShell の注意**: `curl` ではなく必ず **`curl.exe`**（PowerShell の `curl` は別物でエラーになる）。行の続きは bash の `\` ではなく **バッククォート `` ` ``**。**面倒なら改行せず1行で打ってOK**。

確認ポイント：
- レスポンスに `"assignee": "田中"` が入っている。
- `curl.exe http://127.0.0.1:8000/todos`（一覧）でも `assignee` が返る。
- `assignee` を省いて送ると、必須にした場合はエラー（422）になる（任意にした人は通る）。

✅ できたか確認：担当者付きで作成でき、レスポンスとリストに `assignee` が出る。

> **ここまで動いたら大成功！** 一番大事な「テーブルとスキーマの両方を直す」感覚をつかんだ。次へ。

---

## 課題2【担当者でしぼりこむ】`GET /todos?assignee=...` で絞り込む

### この課題のゴール
`GET /todos?assignee=田中` のように担当者を指定すると、その人の TODO だけ返る。
指定しなければ今まで通り全件返す（今の動きを壊さない）。

> **どこを直す？** 「URL からの受け取り（`?assignee=...`）」は **routers**、「DB の絞り込み（条件付き検索）」は **crud**。この2つを直す。

### ステップ 2-1：`crud.py` の `get_todos` を「任意で絞れる」ようにする

`app/crud.py` の `get_todos` を開いて、引数に「担当者名（任意）」を受け取れるようにし、渡されたときだけ絞る。

```python
def get_todos(session: Session, assignee: str | None = None) -> list[Todo]:
    # まず「全部選ぶ」クエリを用意する（お手本のまま）
    statement = select(Todo)

    # assignee が渡されたときだけ、その担当者に絞る
    if assignee is not None:
        # ここに where で絞る1行を書く
        # ヒント: statement = statement.where(Todo.assignee == assignee)

    todos = session.exec(statement).all()
    return list(todos)
```

> **用語**: `where` は「この条件に合うものだけ」という DB の絞り込み命令。`Todo.assignee == assignee` で「担当者が一致するものだけ」になる。
> **`str | None = None`** は「文字列、または未指定（None）。デフォルトは未指定」という意味（＝任意）。

✅ できたか確認：`assignee` が `None` なら全件、値があれば `where` で絞る形になった。

### ステップ 2-2：`routers/todos.py` の `list_todos` でクエリパラメータを受け取る

`app/routers/todos.py` の `list_todos` を開く。引数に `assignee` を足して、`crud.get_todos` に渡す。

```python
@router.get("", response_model=list[TodoRead])
def list_todos(
    # ここに assignee のクエリパラメータを足す
    # ヒント: assignee: str | None = None
    session: Session = Depends(get_session),
) -> list[Todo]:
    # ここで crud.get_todos に assignee を渡す
    # ヒント: return crud.get_todos(session, assignee)
    return crud.get_todos(session)  # ← この行を直す
```

> **なぜこれでクエリパラメータになる？** FastAPI では、関数の引数に「デフォルト値付きの普通の値」を書くと、URL の `?assignee=...` から自動で受け取ってくれる。便利。

✅ できたか確認：`list_todos` が `assignee` を受け取り、それを `get_todos` に渡している。

### ステップ 2-3：動かして確認する

担当者違いを2件以上作ってから（課題1のやり方で `assignee` を変えて2件作る）：

```powershell
curl.exe "http://127.0.0.1:8000/todos?assignee=田中"
```

確認ポイント：
- 田中のものだけ返る。
- パラメータ無し `curl.exe http://127.0.0.1:8000/todos` で全件返る。
- いない担当者を指定すると空リスト `[]` が返る。

> `/docs` でも `GET /todos` を開くと `assignee` の入力欄が増えているはず。そこから試してもOK。

✅ できたか確認：絞り込みも、無指定の全件も、どちらも正しく動く。

> **ここまで動いたら大成功！** クエリパラメータと条件付き検索を覚えた。次へ。

---

## 課題3【期限を足す】`due_date` と「期限切れ一覧」

### この課題のゴール
TODO に期限 `due_date`（任意＝nullable）を持たせ、
`GET /todos/overdue` で **期限切れ（今より前が期限）の TODO だけ** 返せるようにする。

> **nullable（任意）にする理由**: 期限を決めない TODO もあるので、「空っぽでもOK」にする。

### ステップ 3-1：`models.py` に `due_date` を足す（nullable）

`app/models.py` の `Todo` に、任意の日時の列を足す。

```python
    done: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    # ここに due_date を書く（任意＝nullable。期限が無い TODO もある）
    # ヒント: due_date: datetime | None = Field(default=None)
```

> **用語**: `datetime | None` は「日時、または空っぽ（None）」。`default=None` で「省略したら空っぽ」。これで nullable になる。

✅ できたか確認：`Todo` に `due_date: datetime | None` の行が増えた。

### ステップ 3-2：`schemas.py` の入力・出力に足す

`app/schemas.py` の `TodoCreate` と `TodoRead` に `due_date` を足す。任意なのでデフォルト `None`。

```python
class TodoCreate(SQLModel):
    title: str
    done: bool = False
    # （課題1の assignee もここにある想定）
    # ここに due_date を書く（ヒント: due_date: datetime | None = None）


class TodoRead(SQLModel):
    id: int
    title: str
    done: bool
    created_at: datetime
    # （課題1の assignee もここにある想定）
    # ここに due_date を書く（ヒント: due_date: datetime | None = None）
```

✅ できたか確認：両スキーマに `due_date` が増えた。

### ステップ 3-3：`crud.py` で保存と「期限切れ取得」を作る

まず `create_todo` で `due_date` も保存する。

```python
def create_todo(session: Session, todo_in: TodoCreate) -> Todo:
    # 課題1で assignee を足した行に、due_date も足す
    todo = Todo(
        title=todo_in.title,
        done=todo_in.done,
        assignee=todo_in.assignee,
        # ここに due_date=todo_in.due_date を足す
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
```

次に「期限切れだけ引く」関数を新しく足す。ファイルの先頭で `datetime` を import するのを忘れずに（`from datetime import datetime`）。

```python
def get_overdue_todos(session: Session) -> list[Todo]:
    """期限切れ（due_date が今より前で、かつ due_date がある）TODO を返す。"""
    now = datetime.now()
    # ここに「due_date があり、かつ now より前」のクエリを書く
    # ヒント1: select(Todo).where(Todo.due_date != None).where(Todo.due_date < now)
    # ヒント2: statement = ... と組み立ててから session.exec(statement).all()
    todos = session.exec(statement).all()
    return list(todos)
```

> **なぜ `due_date != None` も要る？** 期限を決めていない（None の）TODO を「期限切れ」に混ぜないため。

✅ できたか確認：`create_todo` が `due_date` を保存し、`get_overdue_todos` が新設された。

### ステップ 3-4：⚠️ ルートを足す（定義の**順番**に超注意）

`app/routers/todos.py` に `GET /todos/overdue` を足す。

> **⚠️ 太字の警告：書く場所（順番）を間違えると動かない！**
> `GET /todos/{todo_id}`（id で1件取得）**より前**に `GET /todos/overdue` を定義すること。
> 後ろに書くと、`overdue` という文字列が `{todo_id}`（数字を入れる場所）に吸い込まれ、「overdue は数字に変換できない」というエラーになる。
> FastAPI は**上から順に**ルートを照合するので、より具体的な `/overdue` を先に置く。

```python
# ↓ 必ず @router.get("/{todo_id}") より「上」に書く！
@router.get("/overdue", response_model=list[TodoRead])
def list_overdue_todos(
    session: Session = Depends(get_session),
) -> list[Todo]:
    # ここで crud.get_overdue_todos を呼んで返す
    # ヒント: return crud.get_overdue_todos(session)
    ...
```

> **補足**: このルーターは `prefix="/todos"` 付き。だからファイル内ではパスを `/overdue` と書けば、実際の URL は `/todos/overdue` になる。

✅ できたか確認：`/overdue` のルートが、`/{todo_id}` の**前**に追加された。

### ステップ 3-5：⚠️ DB を作り直して、動作確認

課題1と同じく、列が増えたので **`todo.db` を消して再起動**する（ステップ 1-5 を参照）。

過去日と未来日の期限を1件ずつ作る：

```powershell
curl.exe -X POST http://127.0.0.1:8000/todos `
  -H "Content-Type: application/json" `
  -d '{"title": "締切すぎ", "assignee": "田中", "due_date": "2020-01-01T00:00:00"}'
```

（未来日のほうは `due_date` を `2099-01-01T00:00:00` などにして、もう1件作る。面倒なら1行で打ってOK。）

```powershell
curl.exe http://127.0.0.1:8000/todos/overdue
```

確認ポイント：
- 過去日（2020年）のものだけ返る。
- 未来日（2099年）や `due_date` 無しのものは含まれない。

✅ できたか確認：`/todos/overdue` が期限切れだけを返す。

> **ここまで動いたら大成功！** nullable・日時の比較・ルート順という、つまずきやすい所を全部クリアした。次へ。

---

## 課題4【テストを書いてみる】既存テストを真似て1〜2個

### この課題のゴール
課題1〜3で足した機能のテストを、**既存の `tests/test_todos.py` を真似て**1〜2個書く。
`pytest`（または `uv run pytest`）で全部 PASS する状態にする。

> **テストって難しそう…？** 大丈夫。お手本の `tests/test_todos.py` に「ほぼ同じ形」がもうある。それをコピペして少し変えるだけ。

### ステップ 4-1：お手本のテストを1つ見る

`tests/test_todos.py` の `test_create_todo` を開く。だいたいこういう形：

```python
def test_create_todo(client: TestClient) -> None:
    response = client.post("/todos", json={"title": "牛乳を買う"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "牛乳を買う"
```

- `client.post(...)` で API を呼ぶ（サーバ起動は不要。`client` フィクスチャが用意済み）。
- `assert ...` で「こうなっているはず」を確認する。違えばテスト失敗。

✅ できたか確認：「API を呼んで、assert で結果を確かめる」流れが分かった。

### ステップ 4-2：課題1（assignee）のテストを書く

`tests/test_todos.py` の末尾に、新しい関数を足す。

```python
def test_create_todo_with_assignee(client: TestClient) -> None:
    """POST /todos: assignee 付きで作ると、レスポンスに assignee が返る。"""
    response = client.post("/todos", json={"title": "資料作成", "assignee": "田中"})
    assert response.status_code == 201
    data = response.json()
    # ここに「assignee が "田中" であること」の assert を書く
    # ヒント: assert data["assignee"] == "田中"
```

✅ できたか確認：この関数を追加した。

### ステップ 4-3：課題2（絞り込み）のテストを書く（余裕があれば）

```python
def test_list_todos_filter_by_assignee(client: TestClient) -> None:
    """GET /todos?assignee=...: 指定した担当者のものだけ返る。"""
    client.post("/todos", json={"title": "A", "assignee": "田中"})
    client.post("/todos", json={"title": "B", "assignee": "鈴木"})

    response = client.get("/todos", params={"assignee": "田中"})
    assert response.status_code == 200
    data = response.json()
    # ここに「1件だけ返り、その assignee が "田中" であること」の assert を書く
    # ヒント:
    #   assert len(data) == 1
    #   assert data[0]["assignee"] == "田中"
```

> **メモ**: テストは毎回まっさらなインメモリ DB（メモリ上だけの使い捨て DB）で動くので、`todo.db` を汚さない。だから何度実行しても安全。

✅ できたか確認：（書いた人は）この関数も追加した。

### ステップ 4-4：テストを実行する

```
A（venv + pip。仮想環境を有効化した状態で）:
  pytest

B（uv）:
  uv run pytest
```

確認ポイント：
- 既存テストも含めて **全部 PASS**（緑）になる。
- もし課題3まで終えていて DB の列が増えている場合でも、テストはインメモリ DB を `create_all` で毎回作り直すので、最新のテーブル定義で動く。

✅ できたか確認：`pytest` が全件 PASS した。

> **ここまで来たら本編クリア！おめでとう！** 作って・絞って・期限を入れて・テストまで書けた。立派なバックエンド入門だ。

---

# 第2部：発展課題（むずかしめ・ヒントのみ）

> ここからは**任意**。本編がスッキリできた人向けの「もっと挑戦したい人」コーナー。
> いきなり全部やらず、興味のあるものを1つずつ。難しいので、調べながらでOK。

## 発展①【正規化】User テーブルを新設して外部キーにする（難しめ）

担当者を「ただの文字列 `assignee`」ではなく、独立した `User` テーブルで管理する。
`Todo` は担当者を **文字列ではなく `User` への外部キー `user_id`** で持つように置き換える。

> **正規化とは**: 同じ担当者名をあちこちに文字列でコピーせず、`User` に1か所だけ持つ考え方。名前を直すとき1か所で済む。

ヒント（難しいので調べながら）:
- `app/models.py`: `User` テーブルを新設（最低限 `id` と `name`）。`Todo` の `assignee` を `user_id` に置き換える。
  - 外部キー: `user_id: int = Field(foreign_key="user.id")`（SQLModel はクラス名を小文字にしたものをテーブル名にする。`User` → `user`）。
  - 双方向リレーション: `Relationship(back_populates=...)` で `User` ↔ `Todo` を行き来できる。
- `app/schemas.py` / `app/crud.py`: `user_id` ベースに直す。`User` を作る／引く DB 関数を足してもよい。
- `app/routers/`: `POST /users` を足すなら、別ファイル `app/routers/users.py` を新設して `main.py` で `include_router` するとお手本の分け方に沿う。
- 先に `User` を1件作らないと、その `user_id` を持つ `Todo` は作れない（外部キー制約）。
- 列構成が大きく変わるので **`todo.db` を作り直す**。

## 発展②【認証】ログインして自分の TODO だけ見えるようにする（難しめ）

ヒント:
- トークン認証（OAuth2 / JWT）を入れる。FastAPI の `Security` / `Depends` でログインユーザーを取り出す。
- TODO に「持ち主（owner）」を持たせ、一覧・取得を「自分のものだけ」に絞る。
- 公式ドキュメントの “Security” チュートリアルが出発点。

## 発展③【ページネーション】件数を区切って返す

ヒント:
- `GET /todos?limit=&offset=` を受け取り、`crud` 側で `select(Todo).offset(offset).limit(limit)` のように区切る。
- 課題2のクエリパラメータと同じ要領で routers に引数を足し、crud に渡す。

## 発展④【本格マイグレーション】Alembic で DB の変更を管理する

> 本編では列を足すたびに `todo.db` を消していた。本番ではデータを消せないので「マイグレーション」を使う。

ヒント:
- **Alembic** を導入し、`alembic revision --autogenerate` で「列を足す変更」を記録、`alembic upgrade head` で適用する。
- これで `todo.db` を消さずに（データを保ったまま）列を追加できる。
- マイグレーション = 「DB の形の変更履歴を、安全に積み重ねて適用する仕組み」。
