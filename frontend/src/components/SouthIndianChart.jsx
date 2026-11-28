import React from "react";

/**
 * South Indian (दक्षिण भारतीय) Chart Component
 * Fixed Sign clockwise grid (Pisces at top-left, Aries, Taurus, Gemini at top-right...).
 * Lagna (Ascendant) is indicated with [ASC / लग्न] and diagonal corner marks.
 */
export default function SouthIndianChart({
  chart,
  houses = [],
  isHindi = false,
  title = "दक्षिण भारतीय चक्र (South Indian Chart)",
  selectedHouse = 1,
  onSelectHouse = () => {},
}) {
  const RASHIS_EN = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
  ];
  const RASHIS_HI = [
    "मेष", "वृषभ", "मिथुन", "कर्क",
    "सिंह", "कन्या", "तुला", "वृश्चिक",
    "धनु", "मकर", "कुंभ", "मीन"
  ];

  // Find Ascendant sign index (0-11)
  const ascSignIdx = chart?.ascendant?.sign_index ? chart.ascendant.sign_index - 1 : 0;

  // South Indian fixed 4x4 matrix layout (12 outer boxes, center 2x2 empty)
  // Grid coordinates (row 0-3, col 0-3) mapped to sign indices (0-11)
  const SIGN_GRID_POSITIONS = {
    11: { r: 0, c: 0 }, // Pisces (top-left)
    0:  { r: 0, c: 1 }, // Aries
    1:  { r: 0, c: 2 }, // Taurus
    2:  { r: 0, c: 3 }, // Gemini (top-right)
    3:  { r: 1, c: 3 }, // Cancer
    4:  { r: 2, c: 3 }, // Leo
    5:  { r: 3, c: 3 }, // Virgo (bottom-right)
    6:  { r: 3, c: 2 }, // Libra
    7:  { r: 3, c: 1 }, // Scorpio
    8:  { r: 3, c: 0 }, // Sagittarius (bottom-left)
    9:  { r: 2, c: 0 }, // Capricorn
    10: { r: 1, c: 0 }, // Aquarius
  };

  // Map planets to sign index
  const planetsBySign = {};
  for (let i = 0; i < 12; i++) planetsBySign[i] = [];

  (chart?.planets || []).forEach((p) => {
    const sIdx = p.sign_index ? p.sign_index - 1 : (p.house ? (ascSignIdx + p.house - 1) % 12 : 0);
    if (planetsBySign[sIdx]) {
      planetsBySign[sIdx].push(p);
    }
  });

  // Calculate relative house for each sign
  const getHouseForSign = (sIdx) => {
    return ((sIdx - ascSignIdx + 12) % 12) + 1;
  };

  // Create 4x4 array of cells
  const gridCells = Array(4).fill(null).map(() => Array(4).fill(null));

  Object.entries(SIGN_GRID_POSITIONS).forEach(([sStr, pos]) => {
    const sIdx = parseInt(sStr, 10);
    const houseNum = getHouseForSign(sIdx);
    const isAsc = sIdx === ascSignIdx;
    const isSelected = selectedHouse === houseNum;

    gridCells[pos.r][pos.c] = {
      signIdx: sIdx,
      houseNum,
      isAsc,
      isSelected,
      signName: isHindi ? RASHIS_HI[sIdx] : RASHIS_EN[sIdx],
      planets: planetsBySign[sIdx] || [],
    };
  });

  return (
    <div className="cosmic-card relative overflow-hidden rounded-2xl border border-amber-500/30 p-3 sm:p-4 text-xs select-none">
      <div className="mb-2 text-center">
        <h3 className="font-bold text-amber-300 text-sm tracking-wide">{title}</h3>
        <p className="text-[10px] text-slate-400">
          {isHindi ? "दक्षिणावर्त स्थिर राशि चक्र · खाने पर क्लिक कर भाव चुनें" : "Clockwise fixed sign grid · Click box to inspect house"}
        </p>
      </div>

      <div className="grid grid-cols-4 grid-rows-4 gap-1.5 aspect-square max-w-[480px] mx-auto bg-slate-950/80 p-1.5 rounded-xl border border-slate-800">
        {/* Render 16 cells */}
        {gridCells.map((row, rIdx) =>
          row.map((cell, cIdx) => {
            // Central 2x2 area
            if (rIdx >= 1 && rIdx <= 2 && cIdx >= 1 && cIdx <= 2) {
              if (rIdx === 1 && cIdx === 1) {
                return (
                  <div
                    key={`center`}
                    className="col-span-2 row-span-2 flex flex-col items-center justify-center p-3 text-center bg-slate-900/40 rounded-lg border border-dashed border-amber-500/30"
                  >
                    <div className="text-[11px] font-bold text-amber-300">
                      {isHindi ? "दक्षिण भारतीय शैली" : "South Indian Chart"}
                    </div>
                    <div className="mt-1 text-[10px] text-slate-300 font-semibold">
                      {isHindi ? "लग्न:" : "Ascendant:"}{" "}
                      <span className="text-amber-200">
                        {isHindi ? RASHIS_HI[ascSignIdx] : RASHIS_EN[ascSignIdx]}
                      </span>
                    </div>
                    <div className="text-[9px] text-slate-400 mt-0.5">
                      {chart?.ascendant?.dms || ""}
                    </div>
                    <div className="mt-2 text-[9px] text-slate-400">
                      {isHindi ? "मेष से मीन तक स्थिर चक्र" : "Fixed Zodiac Signs"}
                    </div>
                  </div>
                );
              }
              return null; // covered by col-span-2
            }

            if (!cell) return <div key={`${rIdx}-${cIdx}`} className="bg-transparent" />;

            return (
              <div
                key={`${rIdx}-${cIdx}`}
                onClick={() => onSelectHouse(cell.houseNum)}
                className={`relative flex flex-col justify-between p-1.5 rounded-lg border transition cursor-pointer overflow-hidden ${
                  cell.isSelected
                    ? "border-amber-400 bg-amber-950/40 shadow-md ring-1 ring-amber-400"
                    : cell.isAsc
                    ? "border-amber-500/50 bg-slate-900/90 hover:border-amber-400"
                    : "border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900/90"
                }`}
              >
                {/* Diagonal Accent for Ascendant */}
                {cell.isAsc && (
                  <div className="absolute top-0 right-0 w-4 h-4 overflow-hidden pointer-events-none">
                    <div className="absolute top-0 right-0 w-6 h-1 bg-amber-400 rotate-45 transform origin-top-right shadow-sm" />
                  </div>
                )}

                {/* Box Header: Sign Name & House Badge */}
                <div className="flex items-center justify-between text-[9px]">
                  <span className="font-bold text-slate-400">
                    {cell.signName}
                  </span>
                  <div className="flex items-center gap-1">
                    {cell.isAsc && (
                      <span className="rounded bg-amber-500 px-1 py-0.2 text-[8px] font-black text-slate-950">
                        ASC
                      </span>
                    )}
                    <span
                      className={`rounded px-1 py-0.2 text-[8px] font-semibold ${
                        cell.isSelected ? "bg-amber-400 text-slate-950 font-bold" : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      H{cell.houseNum}
                    </span>
                  </div>
                </div>

                {/* Occupying Planets */}
                <div className="my-auto py-1 flex flex-wrap gap-1 items-center justify-center">
                  {cell.planets.length === 0 ? (
                    <span className="text-[9px] text-slate-700 select-none">•</span>
                  ) : (
                    cell.planets.map((p) => (
                      <span
                        key={p.planet}
                        className={`inline-flex items-center gap-0.5 rounded px-1 py-0.5 text-[9px] font-bold ${
                          p.is_benefic
                            ? "bg-emerald-500/20 text-emerald-300"
                            : "bg-rose-500/20 text-rose-300"
                        }`}
                      >
                        {p.abbr}
                        {p.retrograde && <span className="text-[7px] text-rose-400">R</span>}
                      </span>
                    ))
                  )}
                </div>

                {/* Degree indicator / footer */}
                <div className="text-right text-[8px] text-slate-500">
                  {cell.planets.length > 0 ? `${cell.planets.length} ${isHindi ? "ग्रह" : "pl"}` : ""}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
