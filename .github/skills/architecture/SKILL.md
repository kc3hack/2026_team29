---
name: architecture
description: Application Architecture (Frontend/Backend Separation), Directory Structure (FastAPI/Next.js)
---

# Architecture Guidelines

## 1. System Overview

本プロジェクトは、**Frontend (Next.js)** と **Backend (Python/FastAPI)** が分離された構成を採用しています。
Frontendはユーザーインターフェースを提供し、Backendはビジネスロジック、データベース操作、およびLLMチェーンの実行を担当します。

## 2. Backend Architecture (Python/FastAPI)

Backendは、関心事の分離（Separation of Concerns）を重視し、以下のようなレイヤー構造を意識してください。

### Directory Structure & Responsibilities

- **`app/api/` (Presentation Layer)**:
  - ルーティング定義とリクエスト/レスポンスのハンドリングのみを行う。
  - ビジネスロジックをここに書かないこと。ServiceやChainを呼び出す役割に徹する。
  - Pydanticモデル(`schemas/`)を使用してバリデーションを行う。

- **`app/chains/` & `app/services/` (Business Logic Layer)**:
  - コアとなるビジネスロジックや、LangChain等を用いたLLMのオーケストレーションを記述する。
  - 特定のAPIエンドポイントに依存しない再利用可能なロジックを目指す。

- **`app/models/` (Data Access Layer)**:
  - データベースのモデル定義（SQLAlchemy等）。
  - DB操作の具体的な実装（CRUD）は、必要に応じて `crud/` ディレクトリ（またはRepositoryパターン）に分離することを推奨するが、規模が小さいうちはService内で完結させても良い。

- **`app/schemas/` (Data Transfer Object)**:
  - APIの入出力定義（Pydanticモデル）。
  - DBモデルとAPIレスポンスモデルは分離して定義すること。

### Key Principles

- **Dependency Injection (DI)**: DBセッションや設定、Serviceクラスの依存関係は、FastAPIの `Depends` を使用して注入する。
- **Statelessness**: サーバーはステートレスに保ち、スケーラビリティを確保する。

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
