'use client';

interface Props {
  onZoomIn: () => void
  onZoomOut: () => void
  onReset: () => void
}

const btnStyle = {
  background: "#1a1a2e",
  border: "3px solid #e8b849",
  color: "#e8b849",
  boxShadow: "inset 1px 1px 0 #f5d97a, inset -1px -1px 0 #a67c20, 0 2px 0 #0a0a1a",
  imageRendering: "pixelated" as const,
}

export function ZoomControls({ onZoomIn, onZoomOut, onReset }: Props) {
  return (
    <div className="absolute bottom-6 right-4 z-20 flex flex-col gap-2 font-sans">
      <button
        onClick={onZoomIn}
        className="w-9 h-9 flex items-center justify-center text-base font-bold transition-transform active:translate-y-0.5"
        style={btnStyle}
        aria-label="Zoom in"
      >
        {"+"}
      </button>
      <button
        onClick={onZoomOut}
        className="w-9 h-9 flex items-center justify-center text-base font-bold transition-transform active:translate-y-0.5"
        style={btnStyle}
        aria-label="Zoom out"
      >
        {"-"}
      </button>
      <button
        onClick={onReset}
        className="w-9 h-9 flex items-center justify-center text-xs font-bold transition-transform active:translate-y-0.5"
        style={btnStyle}
        aria-label="Reset view"
      >
        {"R"}
      </button>
    </div>
  )
}
