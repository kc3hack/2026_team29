'use client';

interface Props {
  onZoomIn: () => void
  onZoomOut: () => void
  onReset: () => void
}

const btnStyle = {
  background: "rgba(31, 41, 55, 0.95)",
  border: "2px solid #e8b849",
  color: "#e8b849",
  boxShadow: "2px 2px 0 #2C5F2D",
  imageRendering: "pixelated" as const,
}

export function ZoomControls({ onZoomIn, onZoomOut, onReset }: Props) {
  return (
    <div className="absolute bottom-6 right-4 z-20 flex flex-col gap-2 font-sans">
      <button
        onClick={onZoomIn}
        className="w-10 h-10 flex items-center justify-center text-xl font-bold transition-all active:translate-y-[2px] active:shadow-none hover:bg-[#374151]"
        style={btnStyle}
        aria-label="Zoom in"
      >
        {"+"}
      </button>
      <button
        onClick={onZoomOut}
        className="w-10 h-10 flex items-center justify-center text-xl font-bold transition-all active:translate-y-[2px] active:shadow-none hover:bg-[#374151]"
        style={btnStyle}
        aria-label="Zoom out"
      >
        {"-"}
      </button>
      <button
        onClick={onReset}
        className="w-10 h-10 flex items-center justify-center text-sm font-bold transition-all active:translate-y-[2px] active:shadow-none hover:bg-[#374151]"
        style={btnStyle}
        aria-label="Reset view"
      >
        {"RES"}
      </button>
    </div>
  )
}
