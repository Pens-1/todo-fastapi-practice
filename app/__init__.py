# app パッケージ。
# このディレクトリ全体が 1 つの Python パッケージ（app）になる。
# 役割ごとにファイルを分けている:
#   main.py      … FastAPI 本体の組み立て（lifespan・/ でフロント配信・ルーター登録）
#   routers/     … エンドポイント（HTTP の入口）。todos.py が /todos 系
#   crud.py      … DB 操作そのもの（読み書き関数を集約）
#   database.py  … DB 接続・セッション・テーブル作成
#   models.py    … DB テーブルの形（Todo モデル）
#   schemas.py   … API 入出力の形（スキーマ）
