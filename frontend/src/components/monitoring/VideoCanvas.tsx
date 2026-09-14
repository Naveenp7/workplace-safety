import React, { useEffect, useRef, useCallback } from 'react';
import { DetectionFrame } from '../../types';

interface VideoCanvasProps {
  frame: DetectionFrame | null;
  isActive?: boolean;
}

export function VideoCanvas({ frame, isActive = true }: VideoCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Resize canvas to match container aspect ratio
  const resizeCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const rect = container.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
  }, []);

  useEffect(() => {
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    return () => window.removeEventListener('resize', resizeCanvas);
  }, [resizeCanvas]);

  // Render incoming frame
  useEffect(() => {
    if (!frame || !frame.frame_base64 || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Calculate scale and position to preserve aspect ratio (contain mode)
      const hRatio = canvas.width / img.width;
      const vRatio = canvas.height / img.height;
      const scale = Math.min(hRatio, vRatio);

      const displayW = img.width * scale;
      const displayH = img.height * scale;
      const offsetX = (canvas.width - displayW) / 2;
      const offsetY = (canvas.height - displayH) / 2;

      // Draw background frame
      ctx.drawImage(img, offsetX, offsetY, displayW, displayH);

      // Helper to convert original frame coordinates to canvas coordinates
      const toCanvas = (bbox: any) => {
        if (Array.isArray(bbox)) {
          return {
            x: offsetX + bbox[0] * scale,
            y: offsetY + bbox[1] * scale,
            w: (bbox[2] - bbox[0]) * scale,
            h: (bbox[3] - bbox[1]) * scale,
          };
        }
        return {
          x: offsetX + bbox.x1 * scale,
          y: offsetY + bbox.y1 * scale,
          w: (bbox.x2 - bbox.x1) * scale,
          h: (bbox.y2 - bbox.y1) * scale,
        };
      };

      const drawBox = (rect: { x: number; y: number; w: number; h: number }, color: string, label: string) => {
        // Box
        ctx.strokeStyle = color;
        ctx.lineWidth = 2.5;
        ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);

        // Label background
        ctx.font = 'bold 11px Inter, system-ui, sans-serif';
        const textWidth = ctx.measureText(label).width;
        const labelHeight = 18;
        const labelY = rect.y - labelHeight;
        
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.roundRect(rect.x, Math.max(labelY, 0), textWidth + 10, labelHeight, [3, 3, 0, 0]);
        ctx.fill();

        // Label text
        ctx.fillStyle = '#ffffff';
        ctx.fillText(label, rect.x + 5, Math.max(labelY, 0) + 13);
      };

      // 1. Draw individual gear detections (Helmets & Vests)
      if (Array.isArray(frame.detections)) {
        frame.detections.forEach((d) => {
          if (!d || !d.bbox) return;
          if (d.object_class === 'helmet') {
            const rect = toCanvas(d.bbox);
            const confPct = Math.round((d.confidence || 0.7) * 100);
            drawBox(rect, '#06b6d4', `HARD HAT (${confPct}%)`);
          } else if (d.object_class === 'safety-vest') {
            const rect = toCanvas(d.bbox);
            const confPct = Math.round((d.confidence || 0.7) * 100);
            drawBox(rect, '#10b981', `SAFETY VEST (${confPct}%)`);
          }
        });
      }

      // 2. Draw PPE Status worker boxes
      if (Array.isArray(frame.ppe_statuses)) {
        frame.ppe_statuses.forEach((ppe) => {
          if (!ppe || !ppe.bbox) return;
          const isCompliant = ppe.compliance_status === 'compliant';
          const hasHelmet = ppe.has_helmet;
          const color = isCompliant ? '#10b981' : (hasHelmet ? '#f59e0b' : '#ef4444');
          
          let statusText = 'PPE COMPLIANT';
          if (ppe.compliance_status === 'violation') statusText = 'HELMET + VEST MISSING';
          else if (ppe.compliance_status === 'helmet_missing') statusText = 'HELMET MISSING';
          else if (ppe.compliance_status === 'vest_missing') statusText = 'HELMET DETECTED (VEST MISSING)';

          const rect = toCanvas(ppe.bbox);
          drawBox(rect, color, statusText);

          // Small status dot in corner
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(rect.x + rect.w - 8, rect.y + 8, 5, 0, Math.PI * 2);
          ctx.fill();
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        });
      }

      // 3. Draw Obstacle warnings
      if (Array.isArray(frame.obstacle_warnings)) {
        frame.obstacle_warnings.forEach((obs) => {
          if (!obs || !obs.bbox) return;
          const rect = toCanvas(obs.bbox);
          const label = `⚠ ${obs.object_class || 'Obstacle'} in ${obs.zone_name || 'Zone'}`;
          drawBox(rect, '#f59e0b', label);

          // Dashed border for emphasis
          ctx.setLineDash([4, 4]);
          ctx.strokeStyle = '#f59e0b';
          ctx.lineWidth = 1.5;
          ctx.strokeRect(rect.x - 2, rect.y - 2, rect.w + 4, rect.h + 4);
          ctx.setLineDash([]);
        });
      }
    };

    img.src = `data:image/jpeg;base64,${frame.frame_base64}`;
  }, [frame, resizeCanvas]);

  return (
    <div ref={containerRef} className="absolute inset-0 flex items-center justify-center">
      <canvas ref={canvasRef} className="w-full h-full block" />
      {!isActive && (
        <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm flex flex-col items-center justify-center text-white">
          <div className="w-16 h-16 rounded-2xl bg-white/10 flex items-center justify-center mb-4">
            <span className="text-2xl">📹</span>
          </div>
          <h3 className="text-lg font-semibold mb-1">No Detection Active</h3>
          <p className="text-sm text-slate-300 max-w-sm text-center">
            Select a camera source and click "Start Detection" to begin real-time safety analysis.
          </p>
        </div>
      )}
    </div>
  );
}
