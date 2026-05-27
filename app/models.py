"""DB テーブルの形（モデル）を定義するファイル。

SQLModel のクラスに table=True を付けると、
そのクラスがそのまま 1 つのテーブルになる。
"""

from datetime import datetime

from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    """TODO 1 件分のテーブル定義。

    各属性が 1 つのカラムになる。
    - id:         主キー。None を渡すと DB が自動採番する。
    - title:      タスクのタイトル（必須）。
    - done:       完了したかどうか。デフォルトは未完了 (False)。
    - created_at: 作成日時。レコードを作った瞬間の時刻が自動で入る。

    ※ ここには「誰のタスクか (assignee)」をあえて入れていない。
       それを追加するのが EXERCISES.md の課題1。
    """

    # primary_key=True で主キー。int 型で None を許すと自動採番される。
    id: int | None = Field(default=None, primary_key=True)

    # index=True にしておくと、タイトル検索が速くなる（学習用に付けている）。
    title: str = Field(index=True)

    # 完了フラグ。新規作成時は未完了が自然なのでデフォルト False。
    done: bool = Field(default=False)

    # default_factory に関数を渡すと「レコードを作る瞬間」に実行される。
    # datetime.now を渡すことで、作成時刻が自動的に入る。
    created_at: datetime = Field(default_factory=datetime.now)
