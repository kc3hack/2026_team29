"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  content: string;
}

/**
 * Markdown コンテンツをレトロゲーム風スタイルで表示 (Issue #93, ADR 012)
 * react-markdown + remark-gfm によるレンダリング
 */
export function QuestMarkdownContent({ content }: Props) {
  return (
    <div
      className="bg-white border-4 border-[#14532D] p-6 mb-6"
      style={{ boxShadow: "6px 6px 0 #14532D" }}
    >
      <div className="
        text-[#14532D] leading-relaxed
        [&_h1]:text-2xl [&_h1]:font-bold [&_h1]:mb-4 [&_h1]:border-b-2 [&_h1]:border-[#4ADE80] [&_h1]:pb-2
        [&_h2]:text-xl [&_h2]:font-bold [&_h2]:mb-3 [&_h2]:mt-6
        [&_h3]:text-lg [&_h3]:font-bold [&_h3]:mb-2 [&_h3]:mt-4
        [&_p]:mb-4 [&_p]:leading-relaxed
        [&_ul]:list-disc [&_ul]:pl-6 [&_ul]:mb-4 [&_ul]:space-y-1
        [&_ol]:list-decimal [&_ol]:pl-6 [&_ol]:mb-4 [&_ol]:space-y-1
        [&_li]:leading-relaxed
        [&_code]:bg-gray-100 [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:text-sm [&_code]:font-mono [&_code]:text-[#14532D] [&_code]:border [&_code]:border-gray-300
        [&_pre]:bg-[#1E1E1E] [&_pre]:text-[#4ADE80] [&_pre]:p-4 [&_pre]:overflow-x-auto [&_pre]:mb-4 [&_pre]:border-2 [&_pre]:border-[#14532D] [&_pre]:font-mono [&_pre]:text-sm
        [&_pre_code]:bg-transparent [&_pre_code]:border-0 [&_pre_code]:p-0 [&_pre_code]:text-[#4ADE80]
        [&_blockquote]:border-l-4 [&_blockquote]:border-[#4ADE80] [&_blockquote]:pl-4 [&_blockquote]:italic [&_blockquote]:text-[#3A6B4A] [&_blockquote]:mb-4 [&_blockquote]:bg-[#F0F7F0] [&_blockquote]:py-2
        [&_a]:text-[#14532D] [&_a]:underline [&_a]:hover:text-[#4ADE80]
        [&_strong]:font-bold
        [&_em]:italic
        [&_hr]:border-[#4ADE80] [&_hr]:my-6
        [&_table]:w-full [&_table]:border-collapse [&_table]:mb-4
        [&_th]:border-2 [&_th]:border-[#14532D] [&_th]:bg-[#14532D] [&_th]:text-white [&_th]:px-3 [&_th]:py-2 [&_th]:font-bold
        [&_td]:border-2 [&_td]:border-[#14532D] [&_td]:px-3 [&_td]:py-2
        [&_tr:nth-child(even)]:bg-[#F0F7F0]
      ">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
