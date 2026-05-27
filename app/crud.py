"""DB 操作（CRUD）だけをまとめたファイル。

なぜルートと分けるのか？
- main.py / routers が「HTTP の入口（URL・ステータスコード・404 判定など）」を担当し、
  crud.py が「DB に対する読み書きそのもの」を担当する、と役割をハッキリ分けるため。
- こうすると、DB 操作を他の場所からも再利用でき、テストもしやすくなる。

このファイルのルール:
- 関数は Session を引数で受け取る「純粋な DB 操作」に徹する。
- HTTPException は投げない（404 などの「HTTP の都合」は呼び出し側＝routers の仕事）。
  見つからなければ None を返すだけ。
"""

from sqlmodel import Session, select

from app.models import Todo
from app.schemas import TodoCreate, TodoUpdate


def get_todos(session: Session) -> list[Todo]:
    """TODO を全件取得する。

    select(Todo) で「Todo テーブルを全部選ぶ」クエリを作り、
    session.exec(...).all() で結果をリストとして取り出す。
    """
    todos = session.exec(select(Todo)).all()
    return list(todos)


def get_todo(session: Session, todo_id: int) -> Todo | None:
    """指定 id の TODO を 1 件取得する。無ければ None を返す。

    session.get(Todo, todo_id) は主キーで 1 件引く便利メソッド。
    見つからないと None が返る（404 にするかは呼び出し側が決める）。
    """
    return session.get(Todo, todo_id)


def create_todo(session: Session, todo_in: TodoCreate) -> Todo:
    """TODO を 1 件作成して返す。

    1. 受け取った入力 (TodoCreate) からテーブル用の Todo オブジェクトを作る
    2. session に add して commit（実際に DB へ書き込む）
    3. refresh で DB が採番した id や created_at を読み戻す
    """
    todo = Todo(title=todo_in.title, done=todo_in.done)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def update_todo(session: Session, todo: Todo, todo_in: TodoUpdate) -> Todo:
    """既存の Todo を、送られてきた項目だけ書き換えて返す。

    model_dump(exclude_unset=True) で「クライアントが実際に送った項目」
    だけを取り出せる。これにより done だけ送れば done だけ更新される。
    ※ 対象の Todo が存在するかの確認（404 判定）は呼び出し側で済ませる前提。
    """
    update_data = todo_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def delete_todo(session: Session, todo: Todo) -> None:
    """既存の Todo を削除する。

    ※ 対象の Todo が存在するかの確認（404 判定）は呼び出し側で済ませる前提。
    """
    session.delete(todo)
    session.commit()
