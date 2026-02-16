FROM python:3.13-slim

WORKDIR /app

# Poetryのインストール
RUN pip install poetry

# 依存関係ファイルのコピー
COPY pyproject.toml poetry.lock* ./

# 仮想環境を作成せずにシステムにインストール（コンテナ内なので問題なし）
RUN poetry config virtualenvs.create false

# 依存関係のインストール（詳細なログを出力するために -vv 追加、ルートパッケージを除外）
RUN poetry install --no-interaction --no-ansi --no-root -vv

# ソースコードのコピー
COPY . .

# 開発サーバー起動 (ホストからの接続を許可するために 0.0.0.0 を指定)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]