"""FastAPI アプリ本体。エンドポイント（API の入口）をここで定義する。

URL とそれに対応する処理を 5 つ用意している:
- POST   /todos        作成
- GET    /todos        一覧
- GET    /todos/{id}   1 件取得（無ければ 404）
- PATCH  /todos/{id}   更新（title / done）
- DELETE /todos/{id}   削除

実行方法:
    uv run uvicorn app.main:app --reload
ブラウザで http://127.0.0.1:8000/docs を開くと Swagger UI で試せる。
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from app.database import get_session, init_db
from app.models import Todo
from app.schemas import TodoCreate, TodoRead, TodoUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリの起動・終了時に走る処理（lifespan）。

    yield より前 = 起動時、yield より後 = 終了時。
    起動時に init_db() を呼んでテーブルを作っておく。
    （初回起動で todo.db が無くても、ここで自動的に作られる）
    """
    init_db()
    yield
    # 終了時に後片付けが必要ならここに書く（今回は無し）。


# FastAPI アプリ本体。lifespan を渡して起動時処理を登録する。
app = FastAPI(title="TODO練習API", lifespan=lifespan)


@app.post("/todos", response_model=TodoRead, status_code=201)
def create_todo(
    todo_in: TodoCreate,
    session: Session = Depends(get_session),
) -> Todo:
    """TODO を 1 件作成する。

    1. 受け取った入力 (TodoCreate) からテーブル用の Todo オブジェクトを作る
    2. session に add して commit（実際に DB へ書き込む）
    3. refresh で DB が採番した id や created_at を読み戻す
    4. 保存後の Todo を返す（response_model により TodoRead の形になる）
    """
    todo = Todo(title=todo_in.title, done=todo_in.done)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@app.get("/todos", response_model=list[TodoRead])
def list_todos(session: Session = Depends(get_session)) -> list[Todo]:
    """TODO を全件取得する。

    select(Todo) で「Todo テーブルを全部選ぶ」クエリを作り、
    session.exec(...).all() で結果をリストとして取り出す。
    """
    todos = session.exec(select(Todo)).all()
    return list(todos)


@app.get("/todos/{todo_id}", response_model=TodoRead)
def get_todo(
    todo_id: int,
    session: Session = Depends(get_session),
) -> Todo:
    """指定 id の TODO を 1 件取得する。無ければ 404 を返す。

    session.get(Todo, todo_id) は主キーで 1 件引く便利メソッド。
    見つからないと None が返るので、その場合は 404 エラーにする。
    """
    todo = session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.patch("/todos/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int,
    todo_in: TodoUpdate,
    session: Session = Depends(get_session),
) -> Todo:
    """指定 id の TODO を更新する。送られてきた項目だけ書き換える。

    model_dump(exclude_unset=True) で「クライアントが実際に送った項目」
    だけを取り出せる。これにより done だけ送れば done だけ更新される。
    """
    todo = session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # 送られてきた項目だけ取り出して、1 つずつ上書きする。
    update_data = todo_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(
    todo_id: int,
    session: Session = Depends(get_session),
) -> None:
    """指定 id の TODO を削除する。無ければ 404。

    削除成功時は本文を返さない（204 No Content）。
    """
    todo = session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    session.delete(todo)
    session.commit()
    # 204 なので return は無し（何も返さない）。
