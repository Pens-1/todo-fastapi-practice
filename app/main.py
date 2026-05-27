"""FastAPI アプリ本体（組み立て役）。

このファイルの責務は「アプリの組み立て」だけに絞っている:
- FastAPI インスタンスを作る
- 起動時処理（lifespan で init_db）を登録する
- ルート / で、お手本フロント (app/static/index.html) を配信する
- /todos 系のエンドポイントは routers/todos.py のルーターを include_router で登録する

ビジネスロジック（DB 操作）は crud.py、HTTP の入口は routers/todos.py に分けてある。
こうして「組み立て / 入口 / DB 操作」を分けると、ファイルごとの役割が明確になる。

実行方法:
    uv run uvicorn app.main:app --reload
ブラウザで http://127.0.0.1:8000/docs を開くと Swagger UI で試せる。
http://127.0.0.1:8000/ を開くと、お手本フロント (app/static/index.html) が表示される。
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.database import init_db
from app.routers import todos


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

# /todos 系のエンドポイントをまとめて登録する。
# ルーティングの中身は app/routers/todos.py 側にある。
app.include_router(todos.router)

# お手本フロントの場所を、このファイル (__file__) を基準に絶対パスで解決する。
# どこから起動しても確実に見つかるようにするため。
STATIC_DIR = Path(__file__).parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """ルート / で、お手本フロント (app/static/index.html) を返す。

    StaticFiles を / に丸ごとマウントすると /todos などの API ルートを
    食ってしまう恐れがあるので、ここでは / だけを担当する単純な route にしている。
    """
    return FileResponse(INDEX_HTML)
