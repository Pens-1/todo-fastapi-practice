"""/todos 系エンドポイント（API の入口）を定義するファイル。

役割分担:
- ここ（routers）は「HTTP の入口」担当。URL・メソッド・ステータスコード、
  そして「無ければ 404」のような HTTP 都合の判定だけを書く。
- 実際の DB 読み書きは crud.py の関数に任せ、このファイルは**薄い層**にする。
  こうすると「URL の話」と「DB の話」が混ざらず、読みやすく直しやすい。

URL とそれに対応する処理を 5 つ用意している:
- POST   /todos        作成
- GET    /todos        一覧
- GET    /todos/{id}   1 件取得（無ければ 404）
- PATCH  /todos/{id}   更新（title / done）
- DELETE /todos/{id}   削除
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud
from app.database import get_session
from app.models import Todo
from app.schemas import TodoCreate, TodoRead, TodoUpdate

# APIRouter は「エンドポイントのまとまり」。main.py で include_router して本体に登録する。
# prefix="/todos" を付けると、このファイル内のパスはすべて先頭に /todos が付く。
# tags=["todos"] は /docs（Swagger UI）でのグループ表示名。
router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoRead, status_code=201)
def create_todo(
    todo_in: TodoCreate,
    session: Session = Depends(get_session),
) -> Todo:
    """TODO を 1 件作成する。

    実際の保存は crud.create_todo に任せ、ここは入力を受け取って渡すだけ。
    保存後の Todo を返す（response_model により TodoRead の形になる）。
    """
    return crud.create_todo(session, todo_in)


@router.get("", response_model=list[TodoRead])
def list_todos(session: Session = Depends(get_session)) -> list[Todo]:
    """TODO を全件取得する。"""
    return crud.get_todos(session)


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(
    todo_id: int,
    session: Session = Depends(get_session),
) -> Todo:
    """指定 id の TODO を 1 件取得する。無ければ 404 を返す。

    crud.get_todo は見つからないと None を返すので、
    その「404 にするか」の判断はここ（HTTP の入口）で行う。
    """
    todo = crud.get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int,
    todo_in: TodoUpdate,
    session: Session = Depends(get_session),
) -> Todo:
    """指定 id の TODO を更新する。送られてきた項目だけ書き換える。

    まず存在チェック（無ければ 404）。あれば crud.update_todo で更新する。
    """
    todo = crud.get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return crud.update_todo(session, todo, todo_in)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(
    todo_id: int,
    session: Session = Depends(get_session),
) -> None:
    """指定 id の TODO を削除する。無ければ 404。

    削除成功時は本文を返さない（204 No Content）。
    """
    todo = crud.get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    crud.delete_todo(session, todo)
    # 204 なので return は無し（何も返さない）。
