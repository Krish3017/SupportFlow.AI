'use client';

import React, { useState, useEffect } from 'react';
import { Plus, X } from 'lucide-react';

export function IsometricLoader({ text }: { text?: string }) {
  const [statusIndex, setStatusIndex] = useState(0);
  const statusTexts = ['Initializing System...', 'Connecting to Agents...', 'Loading SupportFlow Data...'];

  useEffect(() => {
    const interval = setInterval(() => {
      setStatusIndex((prev) => (prev + 1) % statusTexts.length);
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  const currentText = text || statusTexts[statusIndex];

  return (
    <div className="fixed inset-0 z-50 bg-[#09090b]/95 backdrop-blur-md flex flex-col items-center justify-center text-zinc-50 select-none">
      <div className="flex flex-col items-center justify-center gap-5">
        {/* 3D CUBE CONTAINER */}
        <div className="w-8 h-8 flex items-center justify-center [perspective:400px]">
          <div className="relative w-7 h-7 [transform-style:preserve-3d] animate-[spinCubeZ_3.5s_infinite_linear]">
            {/* FACE 1: FRONT */}
            <div className="absolute inset-0 bg-[#121214] border border-white/90 rounded-sm flex items-center justify-center [transform:translateZ(14px)]">
              <Plus className="h-3.5 w-3.5 text-white stroke-[2]" />
            </div>

            {/* FACE 2: BACK */}
            <div className="absolute inset-0 bg-[#121214] border border-white/90 rounded-sm flex items-center justify-center [transform:rotateY(180deg)_translateZ(14px)]">
              <X className="h-3.5 w-3.5 text-white stroke-[2]" />
            </div>

            {/* FACE 3: RIGHT */}
            <div className="absolute inset-0 bg-[#18181b] border border-white/90 rounded-sm flex items-center justify-center [transform:rotateY(90deg)_translateZ(14px)]">
              <X className="h-3.5 w-3.5 text-white stroke-[2]" />
            </div>

            {/* FACE 4: LEFT */}
            <div className="absolute inset-0 bg-[#18181b] border border-white/90 rounded-sm flex items-center justify-center [transform:rotateY(-90deg)_translateZ(14px)]">
              <Plus className="h-3.5 w-3.5 text-white stroke-[2]" />
            </div>

            {/* FACE 5: TOP */}
            <div className="absolute inset-0 bg-[#27272a] border border-white/90 rounded-sm flex items-center justify-center [transform:rotateX(90deg)_translateZ(14px)]">
              <Plus className="h-3.5 w-3.5 text-white stroke-[2]" />
            </div>

            {/* FACE 6: BOTTOM */}
            <div className="absolute inset-0 bg-[#09090b] border border-white/90 rounded-sm flex items-center justify-center [transform:rotateX(-90deg)_translateZ(14px)]">
              <X className="h-3.5 w-3.5 text-white stroke-[2]" />
            </div>
          </div>
        </div>

        {/* Dynamic Status Subtitle Text */}
        <div className="flex flex-col items-center gap-1.5 mt-0.5">
          <span className="text-[11px] font-semibold tracking-wide text-zinc-300 min-h-[16px] transition-all duration-300">
            {currentText}
          </span>
          <div className="w-20 h-0.5 bg-zinc-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-zinc-500 via-white to-zinc-500 rounded-full animate-[progressSweep_1.5s_infinite_linear]" />
          </div>
        </div>
      </div>
    </div>
  );
}
