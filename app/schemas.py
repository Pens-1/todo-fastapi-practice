"""API の入出力の「形」を定義するファイル（スキーマ）。

なぜテーブル(models.py の Todo)と別に作るのか？
- 作成時に受け取りたい項目（title だけ）と
- 一覧で返したい項目（id や created_at も含む）と
- 更新時に受け取りたい項目（title / done を任意で）は
それぞれ違うから。

「入力用」「出力用」を分けることで、
クライアントに id を勝手に指定させない、などの制御がしやすくなる。
これがスキーマ分離。
"""

from datetime import datetime

from sqlmodel import SQLModel


class TodoCreate(SQLModel):
    """POST /todos で受け取る入力。

    新規作成時にクライアントから受け取るのは title と done だけ。
    id や created_at はサーバ側で決めるので、ここには含めない。
    done は省略可能（省略したら未完了 False 扱い）。
    """

    title: str
    done: bool = False


class TodoRead(SQLModel):
    """API が返す出力（レスポンス）の形。

    id や created_at を含めて、保存後の完全な状態をクライアントに返す。
    """

    id: int
    title: str
    done: bool
    created_at: datetime


class TodoUpdate(SQLModel):
    """PATCH /todos/{id} で受け取る入力。

    更新は「送られてきた項目だけ書き換える」ようにしたいので、
    すべての項目を省略可能（None 許容）にしている。
    例: done だけ送れば done だけ更新される。
    """

    title: str | None = None
    done: bool | None = None
