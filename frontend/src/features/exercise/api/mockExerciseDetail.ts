import { ExerciseDetail } from "../types/exerciseDetail";

const mockExerciseDetails: Record<string, ExerciseDetail> = {
  "web-html-basics": {
    id: "web-html-basics",
    title: "タグを使い分けよう",
    category: "web",
    difficulty: "beginner",
    description: "HTMLの基本的なタグの使い分けを学びます。見出し、段落、リストなどの基本要素を正しく使えるようになることで、意味のある構造化された文書を作成できるようになります。",
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
      title: "確認テスト（記述式）",
      description: "これまで学んだ内容を確認しましょう",
      type: "text",
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
    description: "CSSの基本的な記法とスタイリングを学びます。セレクタの使い方、色・フォントの設定、余白や境界線などをマスターして、美しいWebページを作れるようになります。",
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
      title: "確認テスト（記述式）",
      description: "CSSの基礎を確認しましょう",
      type: "text",
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
    description: "モバイルフレンドリーなWebサイトの作り方を学びます。メディアクエリやFlexboxを使って、様々な画面サイズに対応したレイアウトを作成できるようになります。",
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
      title: "確認テスト（記述式）",
      description: "レスポンシブデザインの理解を確認しましょう",
      type: "text",
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
    description: "JavaScriptの基本文法とDOM操作を学びます。変数、データ型、関数などの基礎を理解し、ブラウザ上でHTMLを動的に操作できるようになります。Webアプリケーション開発の第一歩です。",
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
      title: "確認テスト（選択式）",
      description: "JavaScriptの基礎知識を確認しましょう",
      type: "choice",
      problem: `以下のコードの実行結果として正しいものを選んでください：

\`\`\`javascript
let x = 5;
const y = 10;
x = x + y;
console.log(x);
\`\`\`

このコードを実行すると、コンソールに何が表示されますか？`,
      choices: [
        "5（xの初期値）",
        "10（yの値）",
        "15（xとyの合計）",
        "エラーが発生する（constは変更できないため）",
      ],
    },
  },
  "ai-machine-learning-basics": {
    id: "ai-machine-learning-basics",
    title: "機械学習の基礎",
    category: "ai",
    difficulty: "beginner",
    description: "機械学習の基本概念と用語を学びます。教師あり学習、教師なし学習、過学習などの重要な概念を理解し、AIエンジニアリングの基礎を身につけます。データサイエンスへの第一歩です。",
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
      title: "確認テスト（選択式）",
      description: "機械学習の基礎概念を確認しましょう",
      type: "choice",
      problem: `教師あり学習の説明として、最も適切なものを選んでください：`,
      choices: [
        "正解ラベル付きのデータを使って学習し、未知のデータに対して予測を行う手法",
        "正解ラベルなしのデータからパターンや構造を発見する手法",
        "報酬を最大化するように行動を学習する手法",
        "人間が全ての判断を行い、機械は補助的な役割のみ果たす手法",
      ],
    },
  },
  "security-web-security-basics": {
    id: "security-web-security-basics",
    title: "Webセキュリティ基礎",
    category: "security",
    difficulty: "intermediate",
    description: "Webアプリケーションの基本的な脆弱性と対策を学びます。XSS、SQLインジェクション、認証/セッション管理などの重要なセキュリティ概念を理解し、安全なWebアプリケーションを開発できるようになります。",
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
      title: "確認テスト（記述式）",
      description: "Webセキュリティの基礎知識を確認しましょう",
      type: "text",
      problem: `以下のPythonコードにはSQLインジェクションの脆弱性があります。
どこが問題で、どのように修正すべきか説明してください。

【脆弱なコード】
\`\`\`python
username = request.GET['username']
query = "SELECT * FROM users WHERE username = '" + username + "'"
cursor.execute(query)
\`\`\`

【解答に含めるべき内容】
1. どのような攻撃が可能か（例を挙げて）
2. なぜこのコードが危険なのか
3. 正しい修正方法（プリペアドステートメントなど）`,
      placeholder: "各問題について、セキュリティの観点から詳しく説明してください...",
    },
  },
  "web-react-intro": {
    id: "web-react-intro",
    title: "React入門",
    category: "web",
    difficulty: "intermediate",
    description: "Reactコンポーネントの作成方法を学びます。StateとPropsの使い方、イベント処理の基本をマスターしましょう。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "Reactコンポーネント基礎",
        type: "reading",
        description: "Reactコンポーネントの基本構造を理解します",
        completed: false,
      },
      {
        id: "lesson-2",
        number: 2,
        title: "Stateの管理",
        type: "practice",
        description: "useStateフックを使った状態管理",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-react-1",
      title: "確認テスト",
      description: "カウンターコンポーネントを作成してください",
      type: "text",
      problem: `以下の仕様を満たすReactコンポーネントを作成してください：

【要件】
1. カウンターの値を表示する
2. 「+」ボタンでカウントを増やす
3. 「-」ボタンでカウントを減らす
4. 「リセット」ボタンで0に戻す

【ヒント】
- useStateを使用してカウントを管理
- ボタンのonClickでカウントを更新`,
      placeholder: "Reactコンポーネントのコードを記述してください...",
    },
  },
  "web-nextjs-app": {
    id: "web-nextjs-app",
    title: "Next.jsでアプリ開発",
    category: "web",
    difficulty: "advanced",
    description: "Next.jsを使ったフルスタックアプリケーション開発を学びます。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "Next.jsプロジェクト構成",
        type: "reading",
        description: "App Routerの基礎",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-nextjs-1",
      title: "確認テスト",
      description: "Next.jsの基本を確認しましょう",
      type: "text",
      problem: `Next.jsのApp Routerについて説明してください。

【記述内容】
1. page.tsxとlayout.tsxの役割
2. Server ComponentsとClient Componentsの違い
3. データフェッチングの方法`,
      placeholder: "Next.jsの特徴を説明してください...",
    },
  },
  "ai-1": {
    id: "ai-1",
    title: "機械学習の基礎",
    category: "ai",
    difficulty: "beginner",
    description: "機械学習の基本概念と手法を学びます。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "機械学習とは",
        type: "reading",
        description: "教師あり学習と教師なし学習",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-ai-1",
      title: "確認テスト",
      description: "機械学習の基礎知識を確認します",
      type: "text",
      problem: `以下の質問に答えてください：

1. 教師あり学習と教師なし学習の違いを説明してください
2. 過学習（Overfitting）とは何か説明してください
3. 訓練データとテストデータを分ける理由を説明してください`,
      placeholder: "各質問に答えてください...",
    },
  },
  "ai-2": {
    id: "ai-2",
    title: "Python for AI",
    category: "ai",
    difficulty: "beginner",
    description: "AI開発に必要なPythonの基礎を学びます。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "NumPy入門",
        type: "practice",
        description: "配列操作の基礎",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-ai-2",
      title: "確認テスト",
      description: "NumPyの基本操作",
      type: "text",
      problem: `NumPyを使って以下の処理を実装してください：

1. 1から10までの配列を作成
2. 全要素を2倍にする
3. 平均値を計算する

【ヒント】
- np.arange()
- 配列の演算
- np.mean()`,
      placeholder: "Pythonコードを記述してください...",
    },
  },
  "game-1": {
    id: "game-1",
    title: "Unity基礎",
    category: "game",
    difficulty: "beginner",
    description: "Unityエンジンの基本操作を学びます。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "Unity画面構成",
        type: "reading",
        description: "Scene、Game、Hierarchyビューの使い方",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-game-1",
      title: "確認テスト",
      description: "Unityの基本を確認します",
      type: "text",
      problem: `Unityエディタの各ビューについて説明してください：

1. Sceneビュー：
2. Gameビュー：
3. Hierarchyビュー：
4. Inspectorビュー：
5. Projectビュー：`,
      placeholder: "各ビューの役割を説明してください...",
    },
  },
  "game-2": {
    id: "game-2",
    title: "C#ゲームプログラミング",
    category: "game",
    difficulty: "beginner",
    description: "UnityでのC#スクリプティングを学びます。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "MonoBehaviour基礎",
        type: "practice",
        description: "Start()とUpdate()の使い方",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-game-2",
      title: "確認テスト",
      description: "キューブを動かすスクリプトを作成",
      type: "text",
      problem: `UnityでGameObjectを動かすC#スクリプトを作成してください：

【要件】
1. 矢印キーで上下左右に移動
2. 移動速度は変数で調整可能
3. Transformコンポーネントを使用

【ヒント】
- Input.GetAxis()
- transform.Translate()`,
      placeholder: "C#コードを記述してください...",
    },
  },
  "infrastructure-1": {
    id: "infrastructure-1",
    title: "Docker基礎",
    category: "infrastructure",
    difficulty: "beginner",
    description: "コンテナ技術の基礎を学びます。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "Dockerとは",
        type: "reading",
        description: "コンテナとイメージの概念",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-infra-1",
      title: "確認テスト",
      description: "Dockerfileを作成してください",
      type: "text",
      problem: `Node.jsアプリケーション用のDockerfileを作成してください：

【要件】
1. Node.js 20を使用
2. package.jsonをコピー
3. npm installを実行
4. アプリケーションコードをコピー
5. ポート3000を公開
6. npm startで起動

【ヒント】
- FROM node:20
- COPY, RUN, EXPOSE, CMD`,
      placeholder: "Dockerfileを記述してください...",
    },
  },
  "infrastructure-2": {
    id: "infrastructure-2",
    title: "Kubernetes入門",
    category: "infrastructure",
    difficulty: "intermediate",
    description: "コンテナオーケストレーションを学びます。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "Kubernetesの概念",
        type: "reading",
        description: "Pod、Service、Deploymentの役割",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-infra-2",
      title: "確認テスト",
      description: "Kubernetesの基本を確認",
      type: "text",
      problem: `Kubernetesの主要なリソースについて説明してください：

1. Pod：
2. Service：
3. Deployment：
4. ReplicaSet：`,
      placeholder: "各リソースの役割を説明してください...",
    },
  },
  "design-1": {
    id: "design-1",
    title: "UI/UX基礎",
    category: "design",
    difficulty: "beginner",
    description: "ユーザーインターフェース設計の原則を学びます。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "UIデザインの原則",
        type: "reading",
        description: "一貫性、フィードバック、制約",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-design-1",
      title: "確認テスト",
      description: "UIデザインの原則",
      type: "text",
      problem: `良いUIデザインの原則について説明してください：

1. 一貫性（Consistency）：
2. フィードバック（Feedback）：
3. 可視性（Visibility）：
4. 制約（Constraints）：`,
      placeholder: "各原則について説明してください...",
    },
  },
  "design-2": {
    id: "design-2",
    title: "Figma実践",
    category: "design",
    difficulty: "beginner",
    description: "Figmaでのデザイン制作を学びます。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "Figmaの基本操作",
        type: "practice",
        description: "フレーム、シェイプ、テキストの作成",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-design-2",
      title: "確認テスト",
      description: "簡単なボタンをデザイン",
      type: "text",
      problem: `Figmaでボタンコンポーネントを作成する手順を説明してください：

【要件】
1. 角丸の長方形
2. テキストラベル
3. ホバー状態のバリエーション
4. コンポーネント化

【記述内容】
- 各ステップの手順
- 使用するツールと機能`,
      placeholder: "作成手順を説明してください...",
    },
  },
  "security-1": {
    id: "security-1",
    title: "セキュリティ基礎",
    category: "security",
    difficulty: "beginner",
    description: "情報セキュリティの基本を学びます。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "セキュリティの3要素",
        type: "reading",
        description: "機密性、完全性、可用性",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-security-1",
      title: "確認テスト",
      description: "セキュリティの基礎知識",
      type: "text",
      problem: `情報セキュリティの3要素（CIA）について説明してください：

1. 機密性（Confidentiality）：
2. 完全性（Integrity）：
3. 可用性（Availability）：

それぞれの例も挙げてください。`,
      placeholder: "各要素について説明してください...",
    },
  },
  "security-2": {
    id: "security-2",
    title: "Webセキュリティ",
    category: "security",
    difficulty: "intermediate",
    description: "XSSやCSRFなどの脆弱性対策を学びます。",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "XSS対策",
        type: "practice",
        description: "クロスサイトスクリプティングの防止",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-security-2",
      title: "確認テスト",
      description: "XSSとCSRFの対策",
      type: "text",
      problem: `以下の脆弱性について説明し、対策方法を記述してください：

1. XSS（クロスサイトスクリプティング）：
   - 攻撃方法：
   - 対策方法：

2. CSRF（クロスサイトリクエストフォージェリ）：
   - 攻撃方法：
   - 対策方法：`,
      placeholder: "各脆弱性と対策を説明してください...",
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
