"""データベース接続まわりをまとめたファイル。

ここでやっていること:
- SQLite に接続する「エンジン」を作る
- アプリ起動時にテーブルを作る関数 (init_db)
- リクエストごとに DB セッションを渡す依存性注入の関数 (get_session)

SQLModel は SQLAlchemy をラップしたライブラリ。
「モデル定義」と「テーブル定義」を 1 つのクラスで書けるのが特徴。
"""

import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

# SQLite のデータベースファイル名。
# このファイル(todo.db)がプロジェクト直下に作られ、その中にデータが保存される。
SQLITE_FILE_NAME = "todo.db"

# 接続先 URL。環境変数 DB_URL があればそれを優先する。
# こうしておくと、テストのときに DB_URL=sqlite:// のように上書きして
# 本番の todo.db を汚さずに済む（テスト容易性のための定番テクニック）。
DATABASE_URL = os.getenv("DB_URL", f"sqlite:///{SQLITE_FILE_NAME}")

# エンジン = DB への接続口。アプリ全体で 1 つだけ作って使い回す。
#
# connect_args={"check_same_thread": False} について:
#   SQLite はデフォルトで「1スレッドからしか触らせない」設定。
#   FastAPI は複数スレッドからアクセスするので、この制限を外す必要がある。
#   （SQLite を使うときの定番のおまじない）
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """テーブルをまとめて作成する。

    SQLModel.metadata には、これまでに import された全モデル
    （models.py の Todo クラスなど）のテーブル定義が登録されている。
    create_all はそれらをまとめて CREATE TABLE する。
    すでに同じテーブルがあれば作り直さない（既存はそのまま）。
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """1 リクエストにつき 1 つの DB セッションを用意する依存性注入用の関数。

    FastAPI の Depends(get_session) でこの関数を指定すると、
    エンドポイントの処理が始まるときにセッションが作られ、
    処理が終わると（yield の後で）自動的に閉じられる。

    yield を使った「ジェネレータ依存性」にすることで、
    with 文と同じく「使い終わったら必ず閉じる」を保証できる。
    """
    with Session(engine) as session:
        yield session
