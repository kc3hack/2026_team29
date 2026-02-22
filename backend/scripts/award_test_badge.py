#!/usr/bin/env python
"""
テストユーザーにBUILDERバッジを付与するスクリプト

Usage:
    docker-compose exec backend python scripts/award_test_badge.py
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import SessionLocal


def main():
    db: Session = SessionLocal()
    
    try:
        # シンプルにSQLクエリで最初のユーザーを取得
        result = db.execute(text("SELECT id, username FROM users LIMIT 1"))
        row = result.fetchone()
        
        if not row:
            print("ユーザーが見つかりませんでした")
            return
        
        user_id, username = row
        print(f"ユーザー: {username} (ID: {user_id})")
        
        # BUILDERバッジを直接INSERTで付与
        for tier in [1, 2, 3]:
            try:
                db.execute(text(
                    "INSERT INTO badges (user_id, category, tier) "
                    "VALUES (:user_id, :category, :tier)"
                ), {"user_id": user_id, "category": "builder", "tier": tier})
                db.commit()
                print(f"✓ Builder Tier {tier} バッジを付与しました")
            except Exception as e:
                db.rollback()
                print(f"⚠ Builder Tier {tier}: {str(e)[:80]}")
        
        print("\n全てのバッジ:")
        result = db.execute(text(
            "SELECT id, category, tier FROM badges WHERE user_id = :user_id"
        ), {"user_id": user_id})
        for row in result:
            badge_id, category, tier = row
            print(f"  - {category} Tier {tier} (ID: {badge_id})")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
