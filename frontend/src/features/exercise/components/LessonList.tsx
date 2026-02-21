"use client";

import { useState } from "react";
import { Lesson } from "../types/exerciseDetail";

interface LessonListProps {
  lessons: Lesson[];
  onLessonClick: (lessonId: string) => void;
}

export default function LessonList({ lessons, onLessonClick }: LessonListProps) {
  const [expandedLessonId, setExpandedLessonId] = useState<string | null>(null);

  const handleLessonClick = (lessonId: string) => {
    setExpandedLessonId(expandedLessonId === lessonId ? null : lessonId);
    onLessonClick(lessonId);
  };

  return (
    <div className="space-y-2">
      {lessons.map((lesson) => {
        const isExpanded = expandedLessonId === lesson.id;
        
        return (
          <div key={lesson.id} className="border-4 border-[#14532D]" style={{ boxShadow: "4px 4px 0 #14532D" }}>
            {/* レッスンヘッダー */}
            <div
              onClick={() => handleLessonClick(lesson.id)}
              className="flex items-start gap-4 p-4 bg-white cursor-pointer hover:bg-[#F0F7F0] transition-colors"
            >
              <div className="flex-shrink-0 w-12 h-12 bg-[#4ADE80] border-2 border-[#14532D] flex items-center justify-center">
                <span className="text-2xl font-bold text-[#14532D]">
                  {String(lesson.number).padStart(2, "0")}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-bold text-[#14532D] mb-1">
                  {lesson.title}
                </h3>
                <p className="text-sm text-[#14532D]">{lesson.description}</p>
              </div>
              <div className="flex-shrink-0 text-2xl text-[#14532D] transition-transform" style={{ transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)' }}>
                ▶
              </div>
            </div>

            {/* レッスンの詳細コンテンツ */}
            {isExpanded && (
              <div className="border-t-4 border-[#14532D] bg-[#FDFEF0] p-6">
                {lesson.type === "reading" ? (
                  <div className="space-y-6">
                    <div className="bg-white border-2 border-[#14532D] p-6" style={{ boxShadow: "4px 4px 0 #14532D" }}>
                      <h3 className="text-xl font-bold text-[#14532D] mb-4">📖 解説</h3>
                      <div className="text-[#14532D] space-y-4">
                        <p className="leading-relaxed">{lesson.description}</p>
                        
                        {/* サンプルコンテンツ */}
                        {lesson.number === 1 && (
                          <>
                            <div className="mt-6">
                              <h4 className="font-bold text-lg mb-2">HTMLタグの基本</h4>
                              <p>HTMLでは、さまざまなタグを使って文書の構造を表現します。</p>
                              <ul className="list-disc list-inside mt-2 space-y-1">
                                <li><code className="bg-gray-100 px-2 py-1">&lt;h1&gt;</code> - 見出し（最も重要）</li>
                                <li><code className="bg-gray-100 px-2 py-1">&lt;p&gt;</code> - 段落</li>
                                <li><code className="bg-gray-100 px-2 py-1">&lt;div&gt;</code> - コンテナ</li>
                              </ul>
                            </div>
                            
                            <div className="mt-6 bg-gray-100 border-2 border-[#14532D] p-4">
                              <h4 className="font-bold mb-2">💻 コード例</h4>
                              <pre className="bg-white p-4 rounded overflow-x-auto">
                                <code>{`<h1>ようこそ！</h1>
<p>これは段落です。</p>
<div class="container">
  <p>divの中の段落</p>
</div>`}</code>
                              </pre>
                            </div>
                          </>
                        )}

                        {lesson.number === 2 && (
                          <>
                            <div className="mt-6">
                              <h4 className="font-bold text-lg mb-2">インデントの重要性</h4>
                              <p>インデント（字下げ）を使うことで、コードの構造が分かりやすくなります。</p>
                            </div>
                            
                            <div className="mt-6">
                              <h4 className="font-bold mb-2">❌ 悪い例</h4>
                              <pre className="bg-red-50 border-2 border-red-300 p-4 rounded">
                                <code>{`<div>
<p>読みにくい</p>
<ul>
<li>項目1</li>
<li>項目2</li>
</ul>
</div>`}</code>
                              </pre>
                            </div>

                            <div className="mt-4">
                              <h4 className="font-bold mb-2">✅ 良い例</h4>
                              <pre className="bg-green-50 border-2 border-green-300 p-4 rounded">
                                <code>{`<div>
  <p>読みやすい</p>
  <ul>
    <li>項目1</li>
    <li>項目2</li>
  </ul>
</div>`}</code>
                              </pre>
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    <div className="bg-[#FCD34D] border-2 border-[#14532D] p-4" style={{ boxShadow: "4px 4px 0 #14532D" }}>
                      <p className="text-[#14532D] font-bold">💡 ポイント: 正しいタグを使うことで、検索エンジンやスクリーンリーダーにもやさしいWebサイトが作れます！</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="bg-white border-2 border-[#14532D] p-6" style={{ boxShadow: "4px 4px 0 #14532D" }}>
                      <h3 className="text-xl font-bold text-[#14532D] mb-4">✏️ 演習問題</h3>
                      <p className="text-[#14532D] mb-4">{lesson.description}</p>
                      <div className="mt-6 bg-gray-50 border-2 border-[#14532D] p-4">
                        <h4 className="font-bold mb-2">課題:</h4>
                        <p>以下の要件を満たすHTMLを作成してください：</p>
                        <ul className="list-disc list-inside mt-2 space-y-1">
                          <li>h1タグで「私のプロフィール」という見出しを作る</li>
                          <li>pタグで自己紹介文を書く</li>
                          <li>ulとliタグで趣味のリストを作る</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
