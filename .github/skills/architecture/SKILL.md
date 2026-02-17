---
name: architecture
description: Application Architecture (Frontend/Backend Separation), Directory Structure (FastAPI/Next.js)
---

# Architecture Guidelines

## 1. System Overview

本プロジェクトは、**Frontend (Next.js)** と **Backend (Python/FastAPI)** が分離された構成を採用しています。
Frontendはユーザーインターフェースを提供し、Backendはビジネスロジック、データベース操作、およびLLMチェーンの実行を担当します。

## 2. Backend Architecture (Python/FastAPI)

バックエンドは関心事の分離（Separation of Concerns）と依存性注入（Dependency Injection）を重視したレイヤー構造を意識してください。

### 2.1. Directory Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── api.py          # ルーター集約
│   │   └── endpoints/      # 各エンドポイント
│   ├── services/           # Business Logic（調整役）
│   ├── chains/             # LLM実装詳細
│   ├── crud/               # データアクセス
│   ├── core/               # ユーティリティ
│   ├── middleware/         # 横断的処理
│   ├── db/                 # DB接続
│   ├── models/             # SQLAlchemyモデル
│   ├── schemas/            # Pydantic（Request/Response）
│   └── main.py
├── tests/                  # テストコード
│   ├── test_api/
│   ├── test_services/
│   └── test_chains/
└── pyproject.toml
```

### 2.2. レイヤー構造

#### **Presentation Layer (`api/`)**
- ルーティング、リクエスト/レスポンス処理
- ビジネスロジックは書かず、サービス呼び出しのみ

#### **Business Logic Layer (`services/`, `chains/`)**
- `services/`: 複数のRepository/Chainの調整（薄い層）
- `chains/`: LLM実装の詳細（変更頻度が高い可能性がある）
- 特定のエンドポイントに依存しない、再利用可能なロジック

#### **Infrastructure Layer (`crud/`, `core/`, `middleware/`, `db/`)**
- `crud/`: データアクセス
- `core/`: 技術的実装（JWT, ハッシュ化, 設定等）
- `middleware/`: 横断的処理（認証、ログ等）
- `db/`: DB接続管理

### 2.3. 設計原則

- **Dependency Injection**: `Depends`で依存注入
- **Separation of Concerns**: 各層は単一責任
- **Reusability**: 特定エンドポイントに依存しない
- **Testability**: DIによるモック化

## 3. Frontend Architecture (Next.js)

Feature-based な構成と、App Router の機能を活用したアーキテクチャを採用します。

### Directory Structure (src/)

- **`app/`**:
  - ルーティング定義（page.tsx, layout.tsx）のみを配置する。
  - ページコンポーネントは、`features/` 内のコンポーネントを組み立てる役割に徹する。

- **`features/`**:
  - 機能単位（ドメイン単位）で分割する（例: `auth`, `skills`, `generation`）。
  - 各featureフォルダ内で `components`, `hooks`, `api`, `types` を持つことで、機能ごとの凝集度を高める。

- **`components/ui/`**:
  - ドメインに依存しない、汎用的なUIコンポーネント（Button, Input, Cardなど）。
  - shadcn/ui 等のコンポーネントはここに配置される。

### Server vs Client Components

- **Server Components (Default)**:
  - 原則としてServer Componentを使用する。
  - データフェッチ、機密情報へのアクセス、重い計算処理はサーバー側で行う。
  - DBへの直接アクセスや、バックエンドAPIへの直接コールはServer Componentで行うことが望ましい。

- **Client Components**:
  - `use client` ディレクティブが必要な場合のみ使用する（例: `useState`, `useEffect`, イベントハンドラを使用する場合）。
  - Treeの末端（Leaf nodes）に配置することを心がける。
