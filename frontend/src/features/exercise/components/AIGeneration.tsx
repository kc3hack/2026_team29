"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { generateQuest } from "../api/generateQuest";

export function AIGeneration() {
  const router = useRouter();
  const [documentContent, setDocumentContent] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    const pdfFiles = files.filter((file) => file.type === "application/pdf");

    if (pdfFiles.length > 0) {
      alert(
        `${pdfFiles.length}個のPDFファイルをアップロードしました（PDF対応は今後実装予定）`,
      );
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      alert(
        `${files.length}個のPDFファイルを選択しました（PDF対応は今後実装予定）`,
      );
    }
  };

  const handleGenerate = async () => {
    const content = documentContent.trim();

    // バリデーション
    if (!content) {
      setError("内容を入力してください");
      return;
    }
    if (content.length < 10) {
      setError("内容が短すぎます（最低10文字）");
      return;
    }
    if (content.length > 10000) {
      setError("内容が長すぎます（最大10,000文字）");
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      const result = await generateQuest({
        document_content: content,
        // user_rankは省略（バックエンドでデフォルト値0を使用）
      });

      // 結果をsessionStorageに保存
      sessionStorage.setItem("questGenerationResult", JSON.stringify(result));

      // 結果ページに遷移
      router.push("/exercises/generate/result");
    } catch (err) {
      console.error("Quest generation failed:", err);
      setError(err instanceof Error ? err.message : "問題の生成に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* タイトルエリア */}
      <div className="mb-8 text-center">
        <h2 className="text-3xl font-bold text-[#14532D] mb-2 flex items-center justify-center gap-2">
          <span className="text-4xl">🤖</span>
          <span>AI問題生成</span>
          <span className="text-4xl">✨</span>
        </h2>
        <p className="text-[#14532D] text-lg">
          PDFや技術記事から自動的に問題を生成します
        </p>
      </div>

      {/* PDFアップロードエリア */}
      <div
        className={`relative border-8 border-dashed p-12 text-center transition-all ${
          isDragging
            ? "border-[#4ADE80] bg-[#4ADE80]/20 scale-105 shadow-[12px_12px_0_rgba(0,0,0,0.4)]"
            : "border-[#14532D] bg-white hover:border-[#4ADE80] shadow-[8px_8px_0_rgba(0,0,0,0.2)] hover:shadow-[10px_10px_0_rgba(0,0,0,0.25)]"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept="application/pdf"
          multiple
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        <div className="pointer-events-none">
          <div className="flex justify-center mb-4">
            <div className="text-6xl animate-bounce">📄</div>
          </div>
          <p className="text-[#14532D] font-bold text-xl mb-2">
            📎 PDFをアップロード（今後実装予定）
          </p>
          <p className="text-[#14532D] text-base">
            現在はテキスト入力のみ対応しています
          </p>
        </div>
      </div>

      {/* または */}
      <div className="flex items-center justify-center my-8">
        <div className="flex-1 border-t-2 border-[#14532D]"></div>
        <span className="px-6 text-[#14532D] font-bold text-lg">または</span>
        <div className="flex-1 border-t-2 border-[#14532D]"></div>
      </div>

      {/* ドキュメント入力 */}
      <div className="bg-white border-8 border-[#14532D] p-4 shadow-[4px_4px_0_rgba(0,0,0,0.15)]">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-2xl">📝</span>
          <span className="font-bold text-[#14532D] text-lg">
            技術記事・ドキュメントから生成
          </span>
        </div>

        <textarea
          value={documentContent}
          onChange={(e) => setDocumentContent(e.target.value)}
          placeholder="技術記事やドキュメントの内容をコピー&ペーストしてください（10〜10,000文字）&#10;&#10;例: React、TypeScript、FastAPIなどの技術解説文、チュートリアル、公式ドキュメントなど"
          className="w-full h-64 px-4 py-3 border-4 border-[#14532D] bg-[#FDFEF0] text-[#14532D] placeholder-[#14532D]/40 font-medium focus:outline-none focus:border-[#4ADE80] focus:bg-white transition-colors resize-y"
        />

        <div className="flex items-center justify-between mt-3">
          <p
            className={`text-sm ml-1 ${
              documentContent.length < 10
                ? "text-[#559C71]"
                : documentContent.length > 10000
                  ? "text-red-500 font-bold"
                  : "text-[#14532D]"
            }`}
          >
            {documentContent.length} / 10,000 文字
          </p>
          <button
            onClick={handleGenerate}
            disabled={isLoading || documentContent.trim().length < 10}
            className="px-8 py-3 bg-[#4ADE80] border-4 border-[#14532D] text-[#14532D] font-bold hover:bg-[#86EFAC] disabled:bg-gray-300 disabled:cursor-not-allowed transition-all shadow-[4px_4px_0_#000] active:shadow-none active:translate-x-1 active:translate-y-1 disabled:shadow-[2px_2px_0_#000]"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin">⏳</span>
                <span>生成中...</span>
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <span className="text-lg">問題を生成</span>
                <span className="text-xl">🚀</span>
              </span>
            )}
          </button>
        </div>

        {error && (
          <div className="mt-3 p-3 bg-red-50 border-2 border-red-500 text-red-700 font-medium">
            ⚠️ {error}
          </div>
        )}

        <p className="text-[#559C71] text-sm mt-3 ml-1">
          💡 ヒント:
          技術記事のURLからコンテンツをコピーするか、自分で要約した内容を貼り付けてください
        </p>
      </div>
    </div>
  );
}
