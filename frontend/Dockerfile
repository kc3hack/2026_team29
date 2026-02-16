# M2チップ対応の Node.js イメージを使用
FROM node:20-slim 

WORKDIR /app

# 依存関係のインストール
COPY package*.json ./
RUN npm install

# ソースコードのコピー
COPY . .

# Next.js 開発サーバー起動
CMD ["npm", "run", "dev"]