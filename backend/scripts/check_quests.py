#!/usr/bin/env python3
"""演習データを確認するスクリプト"""

from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 全演習数
result = db.execute(text("SELECT COUNT(*) FROM quests"))
total = result.scalar()
print(f"演習数: {total}")

# webカテゴリーの演習
result = db.execute(text("SELECT id, title FROM quests WHERE category = 'web' LIMIT 10"))
web_quests = result.fetchall()
print(f"\nwebカテゴリー: {len(web_quests)}件")
for q in web_quests:
    print(f"  ID: {q[0]}, Title: {q[1]}")

# web-html-basics を探す
result = db.execute(text("SELECT id, title FROM quests WHERE id = 'web-html-basics'"))
quest = result.fetchone()
if quest:
    print(f"\n✓ web-html-basics が見つかりました: {quest[1]}")
else:
    print("\n✗ web-html-basics が見つかりません")

db.close()
