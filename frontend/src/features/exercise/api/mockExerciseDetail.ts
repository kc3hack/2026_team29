import { ExerciseDetail } from "../types/exerciseDetail";

const mockExerciseDetails: Record<string, ExerciseDetail> = {
  "web-html-basics": {
    id: "web-html-basics",
    title: "タグを使い分けよう",
    category: "web",
    difficulty: "beginner",
    description: "HTMLの基本的なタグの使い分けを学びます",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "タグを使い分けよう",
        type: "reading",
        description: "解説解説解説解説解説解説",
        completed: false,
      },
      {
        id: "lesson-2",
        number: 2,
        title: "インデントを整えよう",
        type: "reading",
        description: "座学座学座学座学座学座学",
        completed: false,
      },
      {
        id: "lesson-3",
        number: 3,
        title: "レイアウトの基礎を身につけよう",
        type: "practice",
        description: "",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-1",
      title: "確認テスト",
      description: "これまで学んだ内容を確認しましょう",
      problem: `以下の要件を満たすHTMLコードを記述してください：

【要件】
1. h1タグで「私の好きな食べ物ベスト3」という見出しを作成
2. pタグで「私が好きな食べ物を紹介します。」という説明文を記述
3. ulとliタグを使って、好きな食べ物を3つリストアップ
4. 各食べ物の後に、strongタグで「★★★」のような評価を追加
5. 適切なインデントを保って記述

【記述例の形式】
<h1>タイトル</h1>
<p>説明文</p>
<ul>
  <li>項目1 <strong>評価</strong></li>
  ...
</ul>`,
      placeholder: "HTMLコードをここに記述してください...",
    },
  },
  "web-css-basics": {
    id: "web-css-basics",
    title: "CSSの基礎を学ぼう",
    category: "web",
    difficulty: "beginner",
    description: "CSSの基本的な記法とスタイリングを学びます",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "セレクタの使い方",
        type: "reading",
        description: "CSSセレクタの基礎を学びます",
        completed: false,
      },
      {
        id: "lesson-2",
        number: 2,
        title: "色とフォントの設定",
        type: "practice",
        description: "色やフォントを変更してみましょう",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-2",
      title: "確認テスト",
      description: "CSSの基礎を確認しましょう",
      problem: `以下の要件を満たすCSSコードを記述してください：

【HTML】
<div class="card">
  <h2 class="card-title">カードタイトル</h2>
  <p class="card-text">カードの説明文です。</p>
</div>

【要件】
1. .cardクラスに対して：
   - 背景色を薄い青色（#E0F2FE）に設定
   - 内側の余白（padding）を20pxに設定
   - 角を丸く（border-radius: 8px）
   - 影をつける（box-shadow: 0 2px 4px rgba(0,0,0,0.1)）

2. .card-titleクラスに対して：
   - 文字色を濃い青色（#1E40AF）に設定
   - フォントサイズを24pxに設定
   - 下の余白を10pxに設定

3. .card-textクラスに対して：
   - 文字色をグレー（#6B7280）に設定
   - 行の高さを1.6に設定`,
      placeholder: "CSSコードをここに記述してください...",
    },
  },
  "web-responsive-design": {
    id: "web-responsive-design",
    title: "レスポンシブデザイン入門",
    category: "web",
    difficulty: "beginner",
    description: "モバイルフレンドリーなWebサイトの作り方を学びます",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "メディアクエリの基本",
        type: "reading",
        description: "画面サイズに応じたスタイル変更を学びます",
        completed: false,
      },
      {
        id: "lesson-2",
        number: 2,
        title: "Flexboxでレイアウト",
        type: "practice",
        description: "柔軟なレイアウトを作成しましょう",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-3",
      title: "確認テスト",
      description: "レスポンシブデザインの理解を確認しましょう",
      problem: `以下の要件を満たすレスポンシブなCSSコードを記述してください：

【HTML】
<div class="container">
  <div class="box">Box 1</div>
  <div class="box">Box 2</div>
  <div class="box">Box 3</div>
</div>

【要件】
1. .containerクラスに対して：
   - Flexboxを使用（display: flex）
   - 横並びに配置
   - アイテム間に20pxの間隔

2. .boxクラスに対して：
   - 背景色を緑色（#4ADE80）に設定
   - 内側の余白を20pxに設定
   - テキストを中央揃え
   - 等幅で並ぶように設定（flex: 1）

3. 画面幅768px以下の場合：
   - .containerを縦並びに変更（flex-direction: column）
   - 各.boxを幅100%に設定

【ヒント】
@media (max-width: 768px) { ... } を使います`,
      placeholder: "CSSコードをここに記述してください...",
    },
  },
  "web-javascript-basics": {
    id: "web-javascript-basics",
    title: "JavaScript基礎",
    category: "web",
    difficulty: "intermediate",
    description: "JavaScriptの基本文法とDOM操作を学びます",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "変数とデータ型",
        type: "reading",
        description: "JavaScriptの変数宣言とデータ型について学びます",
        completed: false,
      },
      {
        id: "lesson-2",
        number: 2,
        title: "関数の基礎",
        type: "reading",
        description: "関数の定義と呼び出し方を学びます",
        completed: false,
      },
      {
        id: "lesson-3",
        number: 3,
        title: "DOM操作の基本",
        type: "reading",
        description: "HTMLをJavaScriptで操作する方法を学びます",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-4",
      title: "確認テスト（座学）",
      description: "JavaScriptの基礎知識を確認しましょう",
      problem: `以下の問いに答えてください：

【問題1】
JavaScriptにおける「let」「const」「var」の違いについて説明してください。
特に、スコープと再代入可能性の観点から説明してください。

【問題2】
以下のコードの実行結果を予測し、なぜそのような結果になるのか説明してください。

\`\`\`javascript
console.log(typeof null);
console.log(typeof undefined);
console.log(typeof []);
\`\`\`

【問題3】
DOMとは何か、またdocument.querySelector()とdocument.getElementById()の違いについて説明してください。`,
      placeholder: "各問題について、理由を含めて説明してください...",
    },
  },
  "ai-machine-learning-basics": {
    id: "ai-machine-learning-basics",
    title: "機械学習の基礎",
    category: "ai",
    difficulty: "beginner",
    description: "機械学習の基本概念と用語を学びます",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "機械学習とは",
        type: "reading",
        description: "機械学習の定義と種類について学びます",
        completed: false,
      },
      {
        id: "lesson-2",
        number: 2,
        title: "教師あり学習と教師なし学習",
        type: "reading",
        description: "学習方法の違いを理解します",
        completed: false,
      },
      {
        id: "lesson-3",
        number: 3,
        title: "過学習と汎化",
        type: "reading",
        description: "モデルの性能評価について学びます",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-5",
      title: "確認テスト（座学）",
      description: "機械学習の基礎概念を確認しましょう",
      problem: `以下の問いに答えてください：

【問題1】
教師あり学習と教師なし学習の違いを、具体例を挙げて説明してください。
また、それぞれどのような場面で使用されるか説明してください。

【問題2】
「過学習（オーバーフィッティング）」とは何か説明してください。
また、過学習を防ぐためにはどのような対策があるか、2つ以上挙げてください。

【問題3】
訓練データ（Training Data）、検証データ（Validation Data）、テストデータ（Test Data）の
それぞれの役割と、なぜ3つに分ける必要があるのか説明してください。`,
      placeholder: "各問題について、具体例や理由を含めて説明してください...",
    },
  },
  "security-web-security-basics": {
    id: "security-web-security-basics",
    title: "Webセキュリティ基礎",
    category: "security",
    difficulty: "intermediate",
    description: "Webアプリケーションの基本的な脆弱性と対策を学びます",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "XSS（クロスサイトスクリプティング）",
        type: "reading",
        description: "XSS攻撃の仕組みと対策を学びます",
        completed: false,
      },
      {
        id: "lesson-2",
        number: 2,
        title: "SQLインジェクション",
        type: "reading",
        description: "SQLインジェクションの危険性と防御方法を学びます",
        completed: false,
      },
      {
        id: "lesson-3",
        number: 3,
        title: "認証とセッション管理",
        type: "reading",
        description: "安全な認証方法とセッション管理について学びます",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-6",
      title: "確認テスト（座学）",
      description: "Webセキュリティの基礎知識を確認しましょう",
      problem: `以下の問いに答えてください：

【問題1】
XSS（クロスサイトスクリプティング）攻撃とは何か説明してください。
また、この攻撃を防ぐための対策を3つ以上挙げてください。

【問題2】
以下のコードにはSQLインジェクションの脆弱性があります。
どこが問題で、どのように修正すべきか説明してください。

\`\`\`python
username = request.GET['username']
query = "SELECT * FROM users WHERE username = '" + username + "'"
cursor.execute(query)
\`\`\`

【問題3】
パスワードをデータベースに保存する際、平文（プレーンテキスト）で保存してはいけない理由と、
推奨される保存方法について説明してください。
ハッシュ化とソルトの概念についても触れてください。`,
      placeholder: "各問題について、セキュリティの観点から詳しく説明してください...",
    },
  },
};

export const getExerciseDetail = async (
  exerciseId: string
): Promise<ExerciseDetail | null> => {
  // 実際のAPIコールをシミュレート
  await new Promise((resolve) => setTimeout(resolve, 300));
  return mockExerciseDetails[exerciseId] || null;
};
