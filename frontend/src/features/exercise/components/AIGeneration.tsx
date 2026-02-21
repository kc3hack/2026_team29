"use client";

import { useState } from "react";

export function AIGeneration() {
  const [url, setUrl] = useState("");
  const [isDragging, setIsDragging] = useState(false);

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
    const pdfFiles = files.filter(file => file.type === "application/pdf");

    if (pdfFiles.length > 0) {
      alert(`${pdfFiles.length}個のPDFファイルをアップロードしました`);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      alert(`${files.length}個のPDFファイルを選択しました`);
    }
  };

  const handleUrlSubmit = () => {
    if (!url.trim()) return;
    alert(`URLから問題を生成します: ${url}`);
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
        <p className="text-[#14532D] text-lg">PDFやURLから自動的に問題を生成します</p>
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
            <div className="text-6xl animate-bounce">
              📄
            </div>
          </div>
          <p className="text-[#14532D] font-bold text-xl mb-2">
            📎 PDFをアップロード
          </p>
          <p className="text-[#14532D] text-base">
            ファイルをドラッグ&ドロップするか、クリックして選択
          </p>
        </div>
      </div>

      {/* または */}
      <div className="flex items-center justify-center my-8">
        <div className="flex-1 border-t-2 border-[#14532D]"></div>
        <span className="px-6 text-[#14532D] font-bold text-lg">または</span>
        <div className="flex-1 border-t-2 border-[#14532D]"></div>
      </div>

      {/* URL入力 */}
      <div className="bg-white border-8 border-[#14532D] p-4 shadow-[4px_4px_0_rgba(0,0,0,0.15)]">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-2xl">🔗</span>
          <span className="font-bold text-[#14532D] text-lg">URLから生成</span>
        </div>
        <div className="flex gap-2">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/article"
            className="flex-1 px-4 py-3 border-4 border-[#14532D] bg-[#FDFEF0] text-[#14532D] placeholder-[#14532D]/40 font-medium focus:outline-none focus:border-[#4ADE80] focus:bg-white transition-colors"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleUrlSubmit();
              }
            }}
          />
          <button
            onClick={handleUrlSubmit}
            className="px-8 py-3 bg-[#4ADE80] border-4 border-[#14532D] text-[#14532D] font-bold hover:bg-[#86EFAC] transition-all shadow-[4px_4px_0_#000] active:shadow-none active:translate-x-[4px] active:translate-y-[4px]"
          >
            <span className="text-lg">生成</span>
            <span className="text-xl">🚀</span>
          </button>
        </div>
        <p className="text-[#559C71] text-sm mt-3 ml-1">💡 記事、ブログ、技術ドキュメントなどのURLを入力</p>
      </div>

    </div>
  );
}
