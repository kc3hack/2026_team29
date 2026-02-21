"use client";

import { useState, useCallback } from "react";
import { withAuth } from "@/lib/auth/withAuth";
import { SkillTreeCanvas } from "../../features/skill-tree/components/SkillTreeCanvas";
import { SkillNodePanel } from "../../features/skill-tree/components/SkillNodePanel";
import { RankBar } from "../../features/skill-tree/components/RankBar";
import { SkillLegend } from "../../features/skill-tree/components/SkillLegend";
import { ZoomControls } from "../../features/skill-tree/components/ZoomControls";
import type { SkillNode } from "../../features/skill-tree/types/data";

function SkillTreePage() {
  const [selectedNode, setSelectedNode] = useState<SkillNode | null>(null);
  const [zoomAction, setZoomAction] = useState<{
    type: string;
    ts: number;
  } | null>(null);
  const [mounted] = useState(true);

  const handleSelectNode = useCallback((node: SkillNode | null) => {
    setSelectedNode(node);
  }, []);

  return (
    <div
      className="relative w-full h-[calc(100vh-4rem)] overflow-hidden rounded-lg border border-border"
      style={{ background: "#0a0f08" }}
    >
      <SkillTreeCanvas
        onSelectNode={handleSelectNode}
        selectedNode={selectedNode}
        zoomAction={zoomAction}
      />

      <RankBar />
      <SkillLegend />
      <ZoomControls
        onZoomIn={() => setZoomAction({ type: "in", ts: Date.now() })}
        onZoomOut={() => setZoomAction({ type: "out", ts: Date.now() })}
        onReset={() => setZoomAction({ type: "reset", ts: Date.now() })}
      />

      {/* Title */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 text-center pointer-events-none font-sans">
        <h1
          className="text-base font-bold tracking-widest"
          style={{
            color: "#e8b849",
            textShadow: "2px 2px 0 #7a5a10, -1px -1px 0 #0a0a0a",
          }}
        >
          {"SKILL TREE"}
        </h1>
        {mounted && (
          <p
            className="text-[9px] mt-1"
            style={{ color: "#666680" }}
            suppressHydrationWarning
          >
            {
              "\u30C9\u30E9\u30C3\u30B0\u3067\u79FB\u52D5 / \u30B9\u30AF\u30ED\u30FC\u30EB\u3067\u30BA\u30FC\u30E0 / \u30CE\u30FC\u30C9\u3092\u30AF\u30EA\u30C3\u30AF\u3067\u8A73\u7D30"
            }
          </p>
        )}
      </div>

      {selectedNode && (
        <SkillNodePanel
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
}

export default withAuth(SkillTreePage);
