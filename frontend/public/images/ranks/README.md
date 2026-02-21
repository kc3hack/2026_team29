# ランク画像ディレクトリ

このディレクトリには、各エンジニアランク（Rank 0～9）に対応する画像ファイルを配置します。

## 必要な画像ファイル

以下の10個の画像ファイルをこのディレクトリに配置してください:

```
rank_tree_0.png  - Rank 0
rank_tree_1.png  - Rank 1
rank_tree_2.png  - Rank 2
rank_tree_3.png  - Rank 3
rank_tree_4.png  - Rank 4
rank_tree_5.png  - Rank 5
rank_tree_6.png  - Rank 6
rank_tree_7.png  - Rank 7
rank_tree_8.png  - Rank 8
rank_tree_9.png  - Rank 9
```

## 画像の仕様

- **フォーマット**: PNG推奨
- **サイズ**: 80x80px以上（アスペクト比は維持されます）
- **背景**: 透過背景推奨

## フォールバック動作

画像ファイルが見つからない場合や読み込みに失敗した場合、`RankBadge`コンポーネントは自動的に色分け表示モードにフォールバックします。

## 使用箇所

- `frontend/src/features/dashboard/components/RankBadge.tsx`
- `frontend/src/features/dashboard/components/StatusCard.tsx`
