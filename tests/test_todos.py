"""全エンドポイントのテスト。

ポイント:
- 本番用の SQLite ファイル(todo.db)を汚さないように、
  テスト専用のインメモリ DB に差し替えてから実行する。
- FastAPI の dependency_overrides を使うと、
  本番の get_session をテスト用のものに置き換えられる。
- TestClient を使うと、サーバを起動しなくても API を呼べる。
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """テストごとに使い捨てのインメモリ DB セッションを用意する。

    - sqlite:///:memory: でメモリ上だけの DB を作る（ファイルに残らない）。
    - StaticPool を使うことで、複数の接続でも同じインメモリ DB を共有できる。
    - create_all でテーブルを作ってからセッションを渡す。
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """本番の get_session をテスト用セッションに差し替えた TestClient。"""

    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    # テストが終わったら差し替えを元に戻す（他テストへの影響を防ぐ）。
    app.dependency_overrides.clear()


def test_create_todo(client: TestClient) -> None:
    """POST /todos: 作成すると 201 と保存後の中身が返る。"""
    response = client.post("/todos", json={"title": "牛乳を買う"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "牛乳を買う"
    assert data["done"] is False  # 省略時は未完了
    assert data["id"] is not None
    assert "created_at" in data


def test_create_todo_with_done(client: TestClient) -> None:
    """POST /todos: done=True を明示して作成できる。"""
    response = client.post("/todos", json={"title": "完了済みタスク", "done": True})
    assert response.status_code == 201
    assert response.json()["done"] is True


def test_list_todos(client: TestClient) -> None:
    """GET /todos: 作成した分だけ一覧に並ぶ。"""
    client.post("/todos", json={"title": "task1"})
    client.post("/todos", json={"title": "task2"})

    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = [t["title"] for t in data]
    assert "task1" in titles
    assert "task2" in titles


def test_list_todos_empty(client: TestClient) -> None:
    """GET /todos: 何も無ければ空リスト。"""
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_get_todo(client: TestClient) -> None:
    """GET /todos/{id}: 作成した 1 件を id で取得できる。"""
    created = client.post("/todos", json={"title": "取得テスト"}).json()
    todo_id = created["id"]

    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "取得テスト"


def test_get_todo_not_found(client: TestClient) -> None:
    """GET /todos/{id}: 存在しない id は 404。"""
    response = client.get("/todos/9999")
    assert response.status_code == 404


def test_update_todo(client: TestClient) -> None:
    """PATCH /todos/{id}: done だけ送ると done だけ更新される。"""
    created = client.post("/todos", json={"title": "更新前"}).json()
    todo_id = created["id"]

    response = client.patch(f"/todos/{todo_id}", json={"done": True})
    assert response.status_code == 200
    data = response.json()
    assert data["done"] is True
    assert data["title"] == "更新前"  # title は送っていないので変わらない


def test_update_todo_title(client: TestClient) -> None:
    """PATCH /todos/{id}: title を書き換えられる。"""
    created = client.post("/todos", json={"title": "古いタイトル"}).json()
    todo_id = created["id"]

    response = client.patch(f"/todos/{todo_id}", json={"title": "新しいタイトル"})
    assert response.status_code == 200
    assert response.json()["title"] == "新しいタイトル"


def test_update_todo_not_found(client: TestClient) -> None:
    """PATCH /todos/{id}: 存在しない id は 404。"""
    response = client.patch("/todos/9999", json={"done": True})
    assert response.status_code == 404


def test_delete_todo(client: TestClient) -> None:
    """DELETE /todos/{id}: 削除すると 204、その後の取得は 404。"""
    created = client.post("/todos", json={"title": "消す対象"}).json()
    todo_id = created["id"]

    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204

    # 削除後はもう取得できない。
    assert client.get(f"/todos/{todo_id}").status_code == 404


def test_delete_todo_not_found(client: TestClient) -> None:
    """DELETE /todos/{id}: 存在しない id は 404。"""
    response = client.delete("/todos/9999")
    assert response.status_code == 404
