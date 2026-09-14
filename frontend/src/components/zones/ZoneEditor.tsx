import React, { useRef, useState, useEffect } from 'react';

export function ZoneEditor({ onSave }: { onSave: (zone: any) => void }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [currentRect, setCurrentRect] = useState<{x: number, y: number, w: number, h: number} | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#f8fafc'; // slate-50
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#94a3b8'; // slate-400
    ctx.font = '14px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('Click and drag to draw a safety zone', canvas.width/2, canvas.height/2);

    if (currentRect) {
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.strokeRect(currentRect.x, currentRect.y, currentRect.w, currentRect.h);
      ctx.fillStyle = 'rgba(59, 130, 246, 0.2)';
      ctx.fillRect(currentRect.x, currentRect.y, currentRect.w, currentRect.h);
    }
  }, [currentRect]);

  const handleMouseDown = (e: React.MouseEvent) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setStartPos({ x, y });
    setIsDrawing(true);
    setCurrentRect(null);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDrawing) return;
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setCurrentRect({
      x: Math.min(startPos.x, x),
      y: Math.min(startPos.y, y),
      w: Math.abs(x - startPos.x),
      h: Math.abs(y - startPos.y)
    });
  };

  const handleMouseUp = () => {
    setIsDrawing(false);
  };

  return (
    <div className="space-y-4">
      <div className="border border-slate-200 rounded-lg overflow-hidden bg-slate-100 relative">
        <canvas
          ref={canvasRef}
          width={640}
          height={360}
          className="w-full h-auto cursor-crosshair"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        />
      </div>
      <div className="flex justify-between items-center">
        <p className="text-sm text-slate-500">Draw a bounding box to define a zone.</p>
        <div className="space-x-3">
          <button 
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900"
            onClick={() => setCurrentRect(null)}
          >
            Clear
          </button>
          <button 
            className="px-4 py-2 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            onClick={() => {
              if (currentRect && canvasRef.current) {
                const cw = canvasRef.current.width;
                const ch = canvasRef.current.height;
                // Normalize to 0-1 and output as 4-point polygon
                const points = [
                  [currentRect.x / cw, currentRect.y / ch],
                  [(currentRect.x + currentRect.w) / cw, currentRect.y / ch],
                  [(currentRect.x + currentRect.w) / cw, (currentRect.y + currentRect.h) / ch],
                  [currentRect.x / cw, (currentRect.y + currentRect.h) / ch],
                ];
                onSave(points);
              }
            }}
            disabled={!currentRect}
          >
            Save Zone
          </button>
        </div>
      </div>
    </div>
  );
}
