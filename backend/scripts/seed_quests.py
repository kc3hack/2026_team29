#!/usr/bin/env python3
"""演習データをシードするスクリプト"""

from app.db.session import SessionLocal
from sqlalchemy import text

# 難易度マッピング
DIFFICULTY_MAP = {
    "beginner": 1,     # 0-2
    "intermediate": 4, # 3-5
    "advanced": 7,     # 6-7
    "expert": 9        # 8-9
}

# シードする演習データ
QUESTS = [
    {
        "id": 1,
        "title": "HTML/CSSの基礎",
        "description": "HTMLとCSSの基本的な使い方を学びます\n\n## 学習内容\n\n- HTML要素の基礎\n- CSSセレクタとプロパティ\n- レイアウト基礎",
        "difficulty": DIFFICULTY_MAP["beginner"],
        "category": "web",
        "is_generated": False
    },
    {
        "id": 2,
        "title": "レスポンシブデザイン入門",
        "description": "モバイルフレンドリーなWebサイトの作り方を学びます\n\n## 学習内容\n\n- メディアクエリ\n- Flexboxレイアウト\n- モバイルファースト設計",
        "difficulty": DIFFICULTY_MAP["beginner"],
        "category": "web",
        "is_generated": False
    },
    {
        "id": 3,
        "title": "JavaScript基礎",
        "description": "JavaScriptの基本文法とDOM操作を学びます\n\n## 学習内容\n\n- 変数とデータ型\n- 関数とスコープ\n- DOM API",
        "difficulty": DIFFICULTY_MAP["intermediate"],
        "category": "web",
        "is_generated": False
    },
    {
        "id": 4,
        "title": "React入門",
        "description": "Reactコンポーネントの作成方法を学びます\n\n## 学習内容\n\n- コンポーネントとProps\n- StateとHooks\n- イベント処理",
        "difficulty": DIFFICULTY_MAP["intermediate"],
        "category": "web",
        "is_generated": False
    },
    {
        "id": 5,
        "title": "Next.jsでアプリ開発",
        "description": "Next.jsを使ったフルスタックアプリケーション開発を学びます\n\n## 学習内容\n\n- ファイルベースルーティング\n- Server Components\n- API Routes",
        "difficulty": DIFFICULTY_MAP["advanced"],
        "category": "web",
        "is_generated": False
    },
    # AI カテゴリー
    {
        "id": 10,
        "title": "機械学習入門",
        "description": "機械学習の基礎を学びます\n\n## 学習内容\n\n- 教師あり学習\n- 教師なし学習\n- モデル評価",
        "difficulty": DIFFICULTY_MAP["beginner"],
        "category": "ai",
        "is_generated": False
    },
    {
        "id": 11,
        "title": "ニューラルネットワーク基礎",
        "description": "ニューラルネットワークの基本を学びます\n\n## 学習内容\n\n- パーセプトロン\n- 活性化関数\n- 誤差逆伝播法",
        "difficulty": DIFFICULTY_MAP["intermediate"],
        "category": "ai",
        "is_generated": False
    },
    # Game カテゴリー
    {
        "id": 20,
        "title": "ゲームプログラミング基礎",
        "description": "ゲーム開発の基礎を学びます\n\n## 学習内容\n\n- ゲームループ\n- スプライト描画\n- 衝突判定",
        "difficulty": DIFFICULTY_MAP["beginner"],
        "category": "game",
        "is_generated": False
    },
    # Design カテゴリー
    {
        "id": 30,
        "title": "UI/UXデザイン基礎",
        "description": "UI/UXデザインの基本原則を学びます\n\n## 学習内容\n\n- デザイン原則\n- ユーザビリティ\n- プロトタイピング",
        "difficulty": DIFFICULTY_MAP["beginner"],
        "category": "design",
        "is_generated": False
    },
    # Infrastructure カテゴリー
    {
        "id": 40,
        "title": "Docker基礎",
        "description": "Dockerコンテナの基本を学びます\n\n## 学習内容\n\n- コンテナとイメージ\n- Dockerfile\n- Docker Compose",
        "difficulty": DIFFICULTY_MAP["beginner"],
        "category": "infrastructure",
        "is_generated": False
    },
    # Security カテゴリー
    {
        "id": 50,
        "title": "セキュリティ基礎",
        "description": "Webセキュリティの基礎を学びます\n\n## 学習内容\n\n- OWASP Top 10\n- 認証と認可\n- 暗号化技術",
        "difficulty": DIFFICULTY_MAP["beginner"],
        "category": "security",
        "is_generated": False
    },
]

def seed_quests():
    """演習データをシード"""
    db = SessionLocal()
    try:
        # 既存データを確認
        result = db.execute(text("SELECT COUNT(*) FROM quests"))
        count = result.scalar()
        
        if count > 0:
            print(f"⚠️  既に {count} 件の演習が存在します")
            response = input("既存データを削除して再作成しますか？ (y/N): ")
            if response.lower() != "y":
                print("キャンセルしました")
                return
            
            # 関連データを削除
            db.execute(text("DELETE FROM quest_progress"))
            db.execute(text("DELETE FROM quests"))
            db.commit()
            print("✓ 既存データを削除しました")
        
        # 演習データを投入
        for quest in QUESTS:
            db.execute(
                text("""
                    INSERT INTO quests (id, title, description, difficulty, category, is_generated)
                    VALUES (:id, :title, :description, :difficulty, :category, :is_generated)
                """),
                quest
            )
        
        db.commit()
        print(f"\n✓ {len(QUESTS)} 件の演習を追加しました")
        
        # 確認
        result = db.execute(text("SELECT id, title, category, difficulty FROM quests ORDER BY id"))
        quests = result.fetchall()
        print("\n登録された演習:")
        for q in quests:
            print(f"  ID {q[0]}: {q[1]} ({q[2]}, difficulty={q[3]})")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_quests()
