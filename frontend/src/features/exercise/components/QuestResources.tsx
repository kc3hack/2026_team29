"use client";

interface Props {
  resources: string[];
}

export function QuestResources({ resources }: Props) {
  if (resources.length === 0) return null;

  return (
    <div
      className="bg-white border-4 border-[#14532D] p-6 mb-6"
      style={{ boxShadow: "6px 6px 0 #14532D" }}
    >
      <h2 className="text-xl font-bold text-[#14532D] mb-4">🔗 参考リソース</h2>
      <ul className="space-y-3">
        {resources.map((url, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="text-[#14532D] font-bold mt-0.5">→</span>
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#14532D] font-medium underline hover:text-[#4ADE80] transition-colors break-all"
            >
              {url}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
