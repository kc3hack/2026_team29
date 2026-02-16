FROM python:3.11-slim

WORKDIR /app

# Poetryのインストール
RUN pip install poetry

# 依存関係ファイルのコピー
COPY pyproject.toml poetry.lock* ./

# 仮想環境を作成せずにシステムにインストール（コンテナ内なので問題なし）
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# ソースコードのコピー
COPY . .

# 開発サーバー起動 (ホストからの接続を許可するために 0.0.0.0 を指定)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]