import React from "react";

const HOUSE_COORDS = {
  1: { x: 180, y: 92 },
  2: { x: 96, y: 46 },
  3: { x: 46, y: 96 },
  4: { x: 92, y: 180 },
  5: { x: 46, y: 264 },
  6: { x: 96, y: 314 },
  7: { x: 180, y: 268 },
  8: { x: 264, y: 314 },
  9: { x: 314, y: 264 },
  10: { x: 268, y: 180 },
  11: { x: 314, y: 96 },
  12: { x: 264, y: 46 },
};

export default function NorthIndianChart({
  houses = [],
  title = "Lagan Kundli",
  selectedHouse,
  onSelectHouse,
  isHindi = false,
}) {
  const byHouse = {};
  houses.forEach((h) => {
    byHouse[h.house] = h;
  });

  return (
    <div className="cosmic-card animate-fade-up rounded-2xl p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-bold text-amber-300">{title}</h3>
        <span className="text-[11px] text-slate-400">
          {isHindi ? "किसी भी भाव पर क्लिक करें" : "Tap any house"}
        </span>
      </div>
      <div className="relative mx-auto max-w-[360px]">
        <svg viewBox="0 0 360 360" className="w-full rounded-2xl border border-amber-500/35 bg-slate-950/90 shadow-inner">
          <defs>
            <radialGradient id="chartGlow" cx="50%" cy="50%" r="55%">
              <stop offset="0%" stopColor="rgba(245,158,11,0.12)" />
              <stop offset="100%" stopColor="rgba(2,6,23,0)" />
            </radialGradient>
          </defs>
          <rect x="0" y="0" width="360" height="360" fill="url(#chartGlow)" />
          <rect x="10" y="10" width="340" height="340" rx="6" fill="none" stroke="#f59e0b" strokeOpacity="0.85" strokeWidth="1.8" />
          <line x1="10" y1="10" x2="350" y2="350" stroke="#b45309" strokeOpacity="0.7" strokeWidth="1.3" />
          <line x1="350" y1="10" x2="10" y2="350" stroke="#b45309" strokeOpacity="0.7" strokeWidth="1.3" />
          <polygon points="180,10 350,180 180,350 10,180" fill="none" stroke="#f59e0b" strokeOpacity="0.85" strokeWidth="1.6" />

          {Object.entries(HOUSE_COORDS).map(([hStr, pos]) => {
            const hNum = Number(hStr);
            const info = byHouse[hNum] || { sign_index: hNum, planets: [] };
            const isSel = selectedHouse === hNum;
            const pText = (info.planets || []).join(" ");
            const houseLabel = isHindi ? `घर ${hNum} · रा${info.sign_index}` : `H${hNum} · R${info.sign_index}`;
            return (
              <g
                key={hNum}
                onClick={() => onSelectHouse && onSelectHouse(hNum)}
                className="cursor-pointer transition-opacity hover:opacity-90"
              >
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="25"
                  fill={isSel ? "rgba(245, 158, 11, 0.24)" : "transparent"}
                  stroke={isSel ? "#fbbf24" : "none"}
                  strokeWidth="1.5"
                />
                <text x={pos.x} y={pos.y - 10} textAnchor="middle" fill="#94a3b8" fontSize="9.5" fontWeight="600">
                  {houseLabel}
                </text>
                <text x={pos.x} y={pos.y + 8} textAnchor="middle" fill="#fcd34d" fontSize="12" fontWeight="700">
                  {pText || "—"}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
