"""Issue #88 Part 1: スキルツリー生成パーソナライゼーション検証スクリプト

プロンプト修正により、ベースライン固定20ノードから
パーソナライズ可能な20-30ノードに変更されたことを検証する。
"""

from app.core import prompts


def test_prompt_changes():
    """プロンプトテンプレートの変更内容を確認"""
    template = prompts.SKILL_TREE_ANALYSIS_TEMPLATE

    print("=" * 80)
    print("Issue #88 Part 1: プロンプト修正検証")
    print("=" * 80)

    # 修正前の文言が含まれていないことを確認
    old_requirement = "ベースラインの全ノードを含める"
    if old_requirement in template:
        print("❌ FAIL: 旧要件が残っています")
        print(f"   '{old_requirement}'")
        return False
    else:
        print(f"✅ PASS: 旧要件が削除されています（'{old_requirement}'）")

    # 修正後の文言が含まれていることを確認
    new_requirements = [
        "ベースラインスキルツリーの重要ノード（10-15個）",
        "合計目標: 20-30ノード",
        "パーソナライズされたノード（10-15個）",
        "習熟度が高いカテゴリでは基礎を削減",
        "弱点カテゴリでは基礎・中級ノードを手厚く配置",
    ]

    all_found = True
    for req in new_requirements:
        if req in template:
            print(f"✅ PASS: 新要件が含まれています（'{req}'）")
        else:
            print(f"❌ FAIL: 新要件が見つかりません（'{req}'）")
            all_found = False

    print("=" * 80)
    if all_found:
        print("🎉 プロンプト修正完了: パーソナライゼーション強化")
        print()
        print("【改善点】")
        print("  - ベースライン固定20ノード → パーソナライズ可能な20-30ノード")
        print("  - 初心者: 基礎ノード手厚く（20-25ノード）")
        print("  - 上級者: 応用・発展ノード追加（25-30ノード）")
        print()
        print("【次のステップ】")
        print("  1. 実際にスキルツリー生成APIを呼び出して動作確認")
        print("  2. 初心者ユーザーで20-25ノード生成されることを確認")
        print("  3. 上級者ユーザーで25-30ノード生成されることを確認")
        return True
    else:
        print("❌ プロンプト修正が不完全です")
        return False


if __name__ == "__main__":
    success = test_prompt_changes()
    exit(0 if success else 1)
