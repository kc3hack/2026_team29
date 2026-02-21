"use client";

import { useRef, useEffect, useCallback, useMemo } from "react";
import { SKILL_NODES, type SkillNode } from "../types/data";

interface Props {
  nodes?: SkillNode[]; // オプショナル: APIから取得した動的ノードデータ
  onSelectNode: (node: SkillNode | null) => void;
  selectedNode: SkillNode | null;
  zoomAction: { type: string; ts: number } | null;
}

const PX = 3; // pixel block size

/* ---- helpers ---- */
function px(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  c: string,
) {
  ctx.fillStyle = c;
  ctx.fillRect(
    Math.round(x / PX) * PX,
    Math.round(y / PX) * PX,
    Math.max(w, PX),
    Math.max(h, PX),
  );
}

function pxLine(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  c: string,
  thick = 1,
) {
  ctx.fillStyle = c;
  const dx = x1 - x0,
    dy = y1 - y0;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const steps = Math.max(Math.ceil(dist / PX), 1);
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const bx = x0 + dx * t,
      by = y0 + dy * t;
    for (let ty = 0; ty < thick; ty++)
      for (let tx = 0; tx < thick; tx++)
        ctx.fillRect(
          Math.round((bx + tx * PX) / PX) * PX,
          Math.round((by + ty * PX) / PX) * PX,
          PX,
          PX,
        );
  }
}

/* ---- 滑らかな枝を描画（ベジェ曲線風） ---- */
function drawSmoothBranch(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
) {
  const trunkColors = ["#5c3a1e", "#6b4226", "#7a4e30", "#6b4226"];

  // ベジェ曲線の制御点（自然な曲線を作る）
  const dx = x1 - x0;
  const dy = y1 - y0;
  const dist = Math.sqrt(dx * dx + dy * dy);

  // 制御点を計算（中間点で少し下に垂れる）
  const mx = (x0 + x1) / 2;
  const my = (y0 + y1) / 2 + Math.abs(dx) * 0.1; // 横距離に応じて垂れる

  // 曲線を分割して描画
  const steps = Math.max(Math.ceil(dist / (PX * 2)), 10);
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;

    // 二次ベジェ曲線: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
    const s = 1 - t;
    const bx = s * s * x0 + 2 * s * t * mx + t * t * x1;
    const by = s * s * y0 + 2 * s * t * my + t * t * y1;

    // 太さを徐々に変化（根元太く、先細り）
    const thickness = Math.max(2, Math.round(4 * (1 - t * 0.5)));

    // 色を選択（位置に応じて）
    const colorIndex = Math.floor((i / 3) % trunkColors.length);
    ctx.fillStyle = trunkColors[colorIndex];

    // ピクセル単位で描画
    for (let dy = -thickness; dy <= thickness; dy++) {
      for (let dx = -thickness; dx <= thickness; dx++) {
        if (dx * dx + dy * dy > thickness * thickness) continue;
        ctx.fillRect(
          Math.round((bx + dx * PX) / PX) * PX,
          Math.round((by + dy * PX) / PX) * PX,
          PX,
          PX,
        );
      }
    }
  }
}

/* ---- palettes ---- */
const PAL = {
  completed: { fill: "#e8b849", hi: "#f7e8a0", lo: "#a67c20", rim: "#7a5a10" },
  available: { fill: "#5abf5a", hi: "#b0f0b0", lo: "#2e8a2e", rim: "#1a5c1a" },
  locked: { fill: "#555e68", hi: "#7a8290", lo: "#3a3e44", rim: "#2a2e34" },
};
const CAT: Record<string, string> = {
  web: "#55aaff",
  ai: "#f0c040",
  security: "#f06050",
  infra: "#50cc60",
  design: "#dd70ee",
};

/* ---- sparkle pool ---- */
interface Sparkle {
  x: number;
  y: number;
  t: number;
  max: number;
  c: string;
}

export function SkillTreeCanvas({
  nodes,
  onSelectNode,
  selectedNode,
  zoomAction,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const boxRef = useRef<HTMLDivElement>(null);
  const tf = useRef({ x: 0, y: 0, s: 0.7 });
  const drag = useRef({ on: false, sx: 0, sy: 0, lx: 0, ly: 0 });
  const sparks = useRef<Sparkle[]>([]);
  const raf = useRef(0);
  const tick = useRef(0);

  // nodes が渡された場合は動的データを使用、そうでなければ既存のハードコードデータを使用（後方互換性）
  const activeNodes = useMemo(() => nodes || SKILL_NODES, [nodes]);

  // デバッグ: activeNodesの内容を確認 (プロダクションでは無効化)
  // useEffect(() => {
  //   console.log("=== SkillTreeCanvas Debug ===");
  //   console.log("Active Nodes count:", activeNodes.length);
  //   console.log(
  //     "Nodes with children:",
  //     activeNodes.filter((n) => n.children.length > 0).length,
  //   );
  //   activeNodes.forEach((n, i) => {
  //     if (n.children.length > 0) {
  //       console.log(
  //         `Node ${i + 1}: ${n.label} has ${n.children.length} children:`,
  //         n.children,
  //       );
  //     }
  //   });
  // }, [activeNodes]);

  // zoom actions
  useEffect(() => {
    if (!zoomAction) return;
    const t = tf.current;
    if (zoomAction.type === "in") t.s = Math.min(t.s * 1.25, 3);
    else if (zoomAction.type === "out") t.s = Math.max(t.s / 1.25, 0.7);
    else {
      t.s = 0.7;
      t.x = 0;
      t.y = 0;
    }
  }, [zoomAction]);

  // init sparkles
  useEffect(() => {
    const arr: Sparkle[] = [];
    for (const n of activeNodes) {
      if (n.status === "locked") continue;
      for (let i = 0; i < 2; i++) {
        arr.push({
          x: n.x + (Math.random() - 0.5) * 70,
          y: n.y + (Math.random() - 0.5) * 70,
          t: Math.floor(Math.random() * 50),
          max: 50 + Math.floor(Math.random() * 40),
          c: n.status === "completed" ? "#f7e8a0" : "#b0f0b0",
        });
      }
    }
    sparks.current = arr;
  }, [activeNodes]);

  const toWorld = useCallback((sx: number, sy: number) => {
    const c = canvasRef.current;
    if (!c) return { x: 0, y: 0 };
    const t = tf.current;
    return {
      x: (sx - c.width / 2 - t.x) / t.s,
      y: (sy - c.height / 2 - t.y) / t.s,
    };
  }, []);

  const hitNode = useCallback(
    (wx: number, wy: number) => {
      for (let i = activeNodes.length - 1; i >= 0; i--) {
        const n = activeNodes[i];
        if (Math.abs(wx - n.x) < 32 && Math.abs(wy - n.y) < 32) return n;
      }
      return null;
    },
    [activeNodes],
  );

  /* ============ DRAW ============ */
  useEffect(() => {
    const canvas = canvasRef.current,
      box = boxRef.current;
    if (!canvas || !box) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    function resize() {
      if (!canvas || !box) return;
      const dpr = window.devicePixelRatio;
      canvas.width = box.clientWidth * dpr;
      canvas.height = box.clientHeight * dpr;
      canvas.style.width = box.clientWidth + "px";
      canvas.style.height = box.clientHeight + "px";
    }
    resize();
    window.addEventListener("resize", resize);

    /* ---- background: pixel grass & sky ---- */
    function drawBg(ctx: CanvasRenderingContext2D) {
      if (!canvas) return;
      ctx.fillStyle = "#101820";
      ctx.fillRect(-3000, -1200, 6000, 3000);

      // starry sky
      for (let i = 0; i < 60; i++) {
        const sx = ((i * 173 + 37) % 4000) - 2000;
        const sy = ((i * 131 + 19) % 600) - 800;
        const twinkle = Math.sin(tick.current * 0.04 + i * 2) > 0.2;
        if (twinkle) {
          ctx.fillStyle = i % 3 === 0 ? "#667788" : "#556677";
          ctx.fillRect(
            Math.round(sx / PX) * PX,
            Math.round(sy / PX) * PX,
            PX,
            PX,
          );
        }
      }

      // ground / grass strip
      for (let gx = -2000; gx < 2000; gx += PX * 2) {
        const gy = 620 + Math.sin(gx * 0.015) * 6;
        const gc = ((Math.floor(gx / PX) * 7) & 15) > 8 ? "#1a3a1a" : "#254a25";
        ctx.fillStyle = gc;
        const h = PX * (2 + (Math.abs(Math.floor(gx / PX)) % 3));
        ctx.fillRect(Math.round(gx / PX) * PX, Math.round(gy / PX) * PX, PX, h);
      }
      // dirt
      ctx.fillStyle = "#2a1a0a";
      ctx.fillRect(-2000, 640, 4000, 400);
      ctx.fillStyle = "#3a2a1a";
      ctx.fillRect(-2000, 640, 4000, PX * 2);
    }

    /* ---- Pixel tree trunk & branches ---- */
    function drawTree(ctx: CanvasRenderingContext2D) {
      const sway = Math.sin(tick.current * 0.015) * 1.5;
      const trunkC = ["#5c3a1e", "#6b4226", "#7a4e30", "#6b4226", "#5c3a1e"];

      // Trunk: 地面(y=632) → ノード最上部まで伸びる主幹
      const minNodeY = Math.min(...activeNodes.map((n) => n.y)) - 100;
      const trunkTop = Math.min(minNodeY, -450); // ノード最上部を確実にカバー
      const trunkBot = 632;
      const totalH = trunkBot - trunkTop;
      for (let y = trunkBot; y >= trunkTop; y -= PX * 4) {
        // ステップ幅2倍で高速化
        const prog = (trunkBot - y) / totalH; // 0=地面（太い）, 1=上部（細い）
        const w = Math.round(44 - prog * 38); // 44px → 6px（より細く）
        const ci = Math.floor(
          ((Math.abs(y) + Math.floor(sway)) / (PX * 3)) % trunkC.length,
        );
        const xo =
          Math.sin(prog * 2.0 + tick.current * 0.015) * prog * 3 + sway;
        px(ctx, -w / 2 + xo, y, w, PX, trunkC[ci]);
      }

      // 滑らかな枝を描画（ベジェ曲線風）
      for (const nd of activeNodes) {
        for (const cid of nd.children) {
          const ch = activeNodes.find((n) => n.id === cid);
          if (!ch) {
            console.warn(`Child node not found: ${cid} for parent ${nd.id}`);
            continue;
          }

          // 滑らかな枝（曲線）を描画
          drawSmoothBranch(ctx, nd.x, nd.y - 20, ch.x, ch.y + 20);
        }
      }
    }

    /* ---- Pixel leaf clusters (静的・美しい配置) ---- */
    function drawLeaves(ctx: CanvasRenderingContext2D) {
      // 各ノードの位置に葉っぱクラスターを配置
      const clusters: Array<{ x: number; y: number; rx: number; ry: number }> =
        [];

      activeNodes.forEach((node) => {
        const tier = node.tier ?? 0;
        // ノード位置の少し上に葉っぱを配置
        const baseRadius = 60 + tier * 5; // tierが深いほど少し大きく
        clusters.push({
          x: node.x,
          y: node.y - 35, // ノードの上
          rx: baseRadius,
          ry: baseRadius * 0.65,
        });
      });
      const greens = [
        "#1a4a1a",
        "#255a25",
        "#306830",
        "#1e5020",
        "#2a6a2a",
        "#3a7a3a",
      ];

      // 葉っぱを静的に美しく描画（動きは最小限）
      for (const cl of clusters) {
        const sw = Math.sin(tick.current * 0.01 + cl.x * 0.002) * 1; // 動きを抑える
        const srx = cl.rx / PX;
        const sry = cl.ry / PX;
        for (let dy = -sry; dy <= sry; dy++) {
          for (let dx = -srx; dx <= srx; dx++) {
            const ex = dx / srx;
            const ey = dy / sry;
            if (ex * ex + ey * ey > 1) continue;

            // より密度の高い葉っぱ（hash判定を緩和）
            const hash = ((Math.abs(dx) * 7 + Math.abs(dy) * 13) * 31) & 255;
            if (hash > 230 && ex * ex + ey * ey > 0.3) continue; // 200→230で密度up

            // 静的な色配置
            const ci =
              Math.abs(Math.floor(dx * 3) + Math.floor(dy * 5)) % greens.length;
            ctx.fillStyle = greens[ci];
            ctx.fillRect(
              Math.round((cl.x + dx * PX + sw) / PX) * PX,
              Math.round((cl.y + dy * PX) / PX) * PX,
              PX,
              PX,
            );
          }
        }
      }
    }

    /* ---- Connection lines (on top of branches, colored by status) ---- */
    function drawConnections(ctx: CanvasRenderingContext2D) {
      for (const nd of activeNodes) {
        for (const cid of nd.children) {
          const ch = activeNodes.find((n) => n.id === cid);
          if (!ch) continue;
          const both = nd.status === "completed" && ch.status === "completed";
          const avail = nd.status === "completed" && ch.status === "available";

          if (both) {
            pxLine(ctx, nd.x, nd.y, ch.x, ch.y, "#e8b849", 2);
            // animated dot
            const sp = (tick.current * 0.02) % 1;
            const sx = nd.x + (ch.x - nd.x) * sp;
            const sy = nd.y + (ch.y - nd.y) * sp;
            px(ctx, sx - PX, sy - PX, PX * 3, PX * 3, "#f7e8a0");
          } else if (avail) {
            const blink = Math.sin(tick.current * 0.06) > 0;
            pxLine(
              ctx,
              nd.x,
              nd.y,
              ch.x,
              ch.y,
              blink ? "#5abf5a" : "#2e8a2e",
              1,
            );
          } else {
            // dashed for locked
            const dx = ch.x - nd.x,
              dy = ch.y - nd.y;
            const d = Math.sqrt(dx * dx + dy * dy);
            const segs = Math.ceil(d / (PX * 6));
            for (let i = 0; i < segs; i += 2) {
              const t0 = i / segs,
                t1 = Math.min((i + 1) / segs, 1);
              pxLine(
                ctx,
                nd.x + dx * t0,
                nd.y + dy * t0,
                nd.x + dx * t1,
                nd.y + dy * t1,
                "#3a3e44",
                1,
              );
            }
          }
        }
      }
    }

    /* ---- Node drawing ---- */
    function drawNode(
      ctx: CanvasRenderingContext2D,
      n: SkillNode,
      sel: boolean,
    ) {
      const { x, y, status, category } = n;
      const p = PAL[status];
      const S = 22; // half-size

      // Selection bounce arrow
      if (sel) {
        const b = Math.sin(tick.current * 0.1) * 4;
        const ay = y - S - 18 + b;
        ctx.fillStyle = CAT[category];
        ctx.fillRect(
          Math.round((x - PX) / PX) * PX,
          Math.round(ay / PX) * PX,
          PX * 2,
          PX * 4,
        );
        ctx.fillRect(
          Math.round((x - PX * 3) / PX) * PX,
          Math.round((ay + PX * 4) / PX) * PX,
          PX * 6,
          PX,
        );
        ctx.fillRect(
          Math.round((x - PX * 2) / PX) * PX,
          Math.round((ay + PX * 5) / PX) * PX,
          PX * 4,
          PX,
        );
        ctx.fillRect(
          Math.round((x - PX) / PX) * PX,
          Math.round((ay + PX * 6) / PX) * PX,
          PX * 2,
          PX,
        );
      }

      // Category color outer ring (3px)
      const cc = status === "locked" ? "#2a2e34" : CAT[category];
      px(
        ctx,
        x - S - PX * 3,
        y - S - PX * 3,
        (S + PX * 3) * 2,
        (S + PX * 3) * 2,
        cc,
      );

      // Outline
      px(ctx, x - S - PX, y - S - PX, (S + PX) * 2, (S + PX) * 2, p.rim);

      // Main fill
      px(ctx, x - S, y - S, S * 2, S * 2, p.fill);

      // 3D highlight top-left
      px(ctx, x - S, y - S, S * 2, PX, p.hi);
      px(ctx, x - S, y - S, PX, S * 2, p.hi);

      // 3D shadow bottom-right
      px(ctx, x - S, y + S - PX, S * 2, PX, p.lo);
      px(ctx, x + S - PX, y - S, PX, S * 2, p.lo);

      // Inner icon
      if (status === "completed") {
        // checkmark
        const ic = "#3d2510";
        const pts = [
          [-3, -1],
          [-2, 0],
          [-1, 1],
          [0, 0],
          [1, -1],
          [2, -2],
          [3, -3],
        ];
        for (const [dx, dy] of pts)
          px(ctx, x + dx * PX, y + dy * PX, PX, PX, ic);
      } else if (status === "locked") {
        // lock body
        const ic = "#7a8290";
        px(ctx, x - PX * 2, y - PX * 3, PX, PX * 2, ic);
        px(ctx, x - PX, y - PX * 4, PX * 2, PX, ic);
        px(ctx, x + PX, y - PX * 3, PX, PX * 2, ic);
        px(ctx, x - PX * 3, y - PX, PX * 6, PX * 4, ic);
        px(ctx, x, y + PX * 0.5, PX, PX, p.rim);
      } else {
        // exclamation / quest marker
        const ic = "#1a5c1a";
        px(ctx, x, y - PX * 3, PX, PX * 4, ic);
        px(ctx, x, y + PX * 2, PX, PX, ic);
      }

      // Label
      ctx.save();
      // Use fallback if DotGothic16 is not loaded.
      ctx.font = "bold 21px 'DotGothic16', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      // shadow
      ctx.fillStyle = "#000";
      // ctx.fillText(n.label, x + 1, y + S + 9)
      // main
      ctx.fillStyle =
        status === "locked"
          ? "#5a6068"
          : status === "completed"
            ? "#f7e8a0"
            : "#b0f0b0";
      ctx.fillText(n.label, x, y + S + 8);
      ctx.restore();
    }

    /* ---- sparkles ---- */
    function drawSparkles(ctx: CanvasRenderingContext2D) {
      for (const s of sparks.current) {
        s.t++;
        if (s.t > s.max) {
          const pool = activeNodes.filter((n) => n.status !== "locked");
          const nd = pool[Math.floor(Math.random() * pool.length)];
          if (nd) {
            s.x = nd.x + (Math.random() - 0.5) * 80;
            s.y = nd.y + (Math.random() - 0.5) * 80;
            s.t = 0;
          }
          continue;
        }
        if (s.t / s.max > 0.85) continue;
        const phase = Math.floor((s.t / 6) % 4);
        ctx.fillStyle = s.c;
        const bx = Math.round(s.x / PX) * PX,
          by = Math.round(s.y / PX) * PX;
        if (phase === 0) {
          ctx.fillRect(bx, by, PX, PX);
        } else if (phase === 1) {
          ctx.fillRect(bx, by, PX, PX);
          ctx.fillRect(bx - PX, by, PX, PX);
          ctx.fillRect(bx + PX, by, PX, PX);
          ctx.fillRect(bx, by - PX, PX, PX);
          ctx.fillRect(bx, by + PX, PX, PX);
        } else if (phase === 2) {
          ctx.fillRect(bx, by, PX, PX);
          ctx.fillRect(bx - PX, by - PX, PX, PX);
          ctx.fillRect(bx + PX, by - PX, PX, PX);
          ctx.fillRect(bx - PX, by + PX, PX, PX);
          ctx.fillRect(bx + PX, by + PX, PX, PX);
        } else {
          ctx.fillRect(bx, by, PX, PX);
          ctx.fillRect(bx - PX, by, PX, PX);
          ctx.fillRect(bx + PX, by, PX, PX);
        }
      }
    }

    /* ---- main loop ---- */
    function draw() {
      if (!canvas || !ctx) return;
      tick.current++;
      const t = tf.current;
      ctx.imageSmoothingEnabled = false;
      ctx.fillStyle = "#0a1008";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.save();
      ctx.translate(canvas.width / 2 + t.x, canvas.height / 2 + t.y);
      ctx.scale(t.s, t.s);

      drawBg(ctx);
      drawLeaves(ctx);
      drawTree(ctx);
      drawConnections(ctx);
      drawSparkles(ctx);

      const sorted = [...activeNodes].sort((a, b) => {
        const o = { locked: 0, available: 1, completed: 2 } as const;
        return o[a.status] - o[b.status];
      });
      for (const n of sorted) drawNode(ctx, n, selectedNode?.id === n.id);

      ctx.restore();
      raf.current = requestAnimationFrame(draw);
    }
    draw();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(raf.current);
    };
  }, [selectedNode, activeNodes]);

  /* ============ EVENTS ============ */
  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;

    const onMD = (e: MouseEvent) => {
      drag.current = {
        on: false,
        sx: e.clientX,
        sy: e.clientY,
        lx: e.clientX,
        ly: e.clientY,
      };
    };
    const onMM = () => {
      /* drag disabled */
    };
    const onMU = (e: MouseEvent) => {
      const d = drag.current;
      const moved =
        Math.abs(e.clientX - d.sx) > 5 || Math.abs(e.clientY - d.sy) > 5;
      if (!moved) {
        const rect = c.getBoundingClientRect();
        const sx = (e.clientX - rect.left) * window.devicePixelRatio;
        const sy = (e.clientY - rect.top) * window.devicePixelRatio;
        const w = toWorld(sx, sy);
        onSelectNode(hitNode(w.x, w.y));
      }
    };
    const onWh = (e: WheelEvent) => {
      // Prevent default only if Ctrl key is pressed or using pinch gesture (generic heuristic)
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        tf.current.s = Math.max(
          0.7,
          Math.min(3, tf.current.s * (e.deltaY > 0 ? 0.92 : 1.08)),
        );
      }
    };

    let lastDist = 0;
    const onTS = (e: TouchEvent) => {
      if (e.touches.length === 1)
        drag.current = {
          on: false,
          sx: e.touches[0].clientX,
          sy: e.touches[0].clientY,
          lx: e.touches[0].clientX,
          ly: e.touches[0].clientY,
        };
      else if (e.touches.length === 2) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        lastDist = Math.sqrt(dx * dx + dy * dy);
      }
    };
    const onTM = (e: TouchEvent) => {
      e.preventDefault();
      if (e.touches.length === 2) {
        /* 1-finger pan disabled */
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (lastDist > 0)
          tf.current.s = Math.max(
            0.7,
            Math.min(3, tf.current.s * (dist / lastDist)),
          );
        lastDist = dist;
      }
    };
    const onTE = (e: TouchEvent) => {
      if (e.touches.length === 0) {
        const ch = e.changedTouches[0];
        if (
          Math.abs(ch.clientX - drag.current.sx) < 10 &&
          Math.abs(ch.clientY - drag.current.sy) < 10
        ) {
          const rect = c.getBoundingClientRect();
          const sx = (ch.clientX - rect.left) * window.devicePixelRatio;
          const sy = (ch.clientY - rect.top) * window.devicePixelRatio;
          const w = toWorld(sx, sy);
          onSelectNode(hitNode(w.x, w.y));
        }
        drag.current.on = false;
      }
    };

    c.addEventListener("mousedown", onMD);
    window.addEventListener("mousemove", onMM);
    window.addEventListener("mouseup", onMU);
    c.addEventListener("wheel", onWh, { passive: false });
    c.addEventListener("touchstart", onTS, { passive: false });
    c.addEventListener("touchmove", onTM, { passive: false });
    c.addEventListener("touchend", onTE);

    return () => {
      c.removeEventListener("mousedown", onMD);
      window.removeEventListener("mousemove", onMM);
      window.removeEventListener("mouseup", onMU);
      c.removeEventListener("wheel", onWh);
      c.removeEventListener("touchstart", onTS);
      c.removeEventListener("touchmove", onTM);
      c.removeEventListener("touchend", onTE);
    };
  }, [onSelectNode, toWorld, hitNode]);

  return (
    <div ref={boxRef} className="absolute inset-0">
      <canvas
        ref={canvasRef}
        className="block w-full h-full cursor-default"
        style={{ imageRendering: "pixelated" }}
      />
    </div>
  );
}
