import React, { useState } from "react";
import { Compass, Sparkles, Table as TableIcon } from "lucide-react";
import SpeechButton from "./SpeechButton";

export default function BhavChalitChart({ kpCusps, isHindi = true }) {
  const [selectedCusp, setSelectedCusp] = useState(1);
  const [viewMode, setViewMode] = useState("table"); // "table" | "grid"

  if (!kpCusps || !kpCusps.cusps || kpCusps.cusps.length === 0) {
    return null;
  }

  const cusps = kpCusps.cusps;
  const activeCuspData = cusps.find((c) => c.cusp_number === selectedCusp) || cusps[0];

  return (
    <div className="cosmic-card rounded-2xl p-4 sm:p-5 space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/15 text-amber-400">
            <Compass className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-amber-300">
              {isHindi ? "KP भाव चलित कस्प चार्ट (Placidus Cuspal Chart)" : "KP Bhav Chalit Cuspal Chart (Placidus)"}
            </h2>
            <p className="text-[11px] text-slate-400">
              {isHindi
                ? "12 भावों की सटीक कस्प डिग्रियां, भाव संधि विस्तार व चलित ग्रह स्थिति"
                : "Exact 12-house cuspal degrees, sandhi spans & chalit planet placements"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex rounded-xl border border-slate-800 bg-slate-950 p-1 text-xs">
            <button
              type="button"
              onClick={() => setViewMode("table")}
              className={`rounded-lg px-2.5 py-1 font-semibold transition ${
                viewMode === "table"
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {isHindi ? "कस्प तालिका" : "Cusp Table"}
            </button>
            <button
              type="button"
              onClick={() => setViewMode("grid")}
              className={`rounded-lg px-2.5 py-1 font-semibold transition ${
                viewMode === "grid"
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {isHindi ? "12 भाव ग्रिड" : "12-House Grid"}
            </button>
          </div>
        </div>
      </div>

      {viewMode === "table" ? (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400">
              <tr>
                <th className="py-2 pr-2">{isHindi ? "कस्प" : "Cusp"}</th>
                <th className="py-2 pr-2">{isHindi ? "राशि (Sign)" : "Sign"}</th>
                <th className="py-2 pr-2">{isHindi ? "कस्प अंश (DMS)" : "Cusp Deg"}</th>
                <th className="py-2 pr-2">{isHindi ? "नक्षत्र (Pada)" : "Nakshatra"}</th>
                <th className="py-2 pr-2 text-amber-300">RL</th>
                <th className="py-2 pr-2 text-amber-300">NL</th>
                <th className="py-2 pr-2 text-emerald-300">SL</th>
                <th className="py-2 pr-2 text-emerald-300">SSL</th>
                <th className="py-2">{isHindi ? "चलित स्थित ग्रह" : "Chalit Occupants"}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/70">
              {cusps.map((c) => (
                <tr
                  key={c.cusp_number}
                  onClick={() => setSelectedCusp(c.cusp_number)}
                  className={`cursor-pointer transition hover:bg-slate-900/60 ${
                    selectedCusp === c.cusp_number ? "bg-amber-500/10" : ""
                  }`}
                >
                  <td className="py-2 pr-2 font-bold text-amber-300">
                    {isHindi ? `भाव ${c.cusp_number}` : `H${c.cusp_number}`}
                  </td>
                  <td className="py-2 pr-2 text-white">{isHindi ? c.rashi_hi : c.rashi}</td>
                  <td className="py-2 pr-2 font-mono text-slate-300">{c.dms}</td>
                  <td className="py-2 pr-2 text-slate-300">
                    {c.nakshatra} ({isHindi ? "चरण" : "P"}{c.pada})
                  </td>
                  <td className="py-2 pr-2 text-amber-200">{isHindi ? c.rl_hi : c.rl}</td>
                  <td className="py-2 pr-2 text-amber-200">{isHindi ? c.nl_hi : c.nl}</td>
                  <td className="py-2 pr-2 font-bold text-emerald-400">{isHindi ? c.sl_hi : c.sl}</td>
                  <td className="py-2 pr-2 font-bold text-emerald-400">{isHindi ? c.ssl_hi : c.ssl}</td>
                  <td className="py-2">
                    {c.occupants.length === 0 ? (
                      <span className="text-slate-500 text-[10px]">—</span>
                    ) : (
                      <div className="flex flex-wrap gap-1">
                        {c.occupants.map((p, idx) => (
                          <span
                            key={idx}
                            className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                              p.is_benefic ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
                            }`}
                          >
                            {isHindi ? p.planet_hi : p.planet}
                            {p.retrograde ? " (R)" : ""}
                          </span>
                        ))}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        /* 12-House Grid View */
        <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 text-xs">
          {cusps.map((c) => (
            <div
              key={c.cusp_number}
              onClick={() => setSelectedCusp(c.cusp_number)}
              className={`rounded-2xl border p-3.5 space-y-2 cursor-pointer transition ${
                selectedCusp === c.cusp_number
                  ? "border-amber-400 bg-amber-950/20 shadow-lg scale-[1.02]"
                  : "border-slate-800 bg-slate-900/70 hover:border-slate-700"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="rounded-lg bg-amber-500/20 px-2 py-0.5 text-xs font-bold text-amber-300">
                  {isHindi ? `भाव ${c.cusp_number}` : `House ${c.cusp_number}`}
                </span>
                <span className="font-mono text-amber-200 font-bold">{c.dms}</span>
              </div>

              <div className="text-white font-semibold">
                {isHindi ? c.rashi_hi : c.rashi} · {c.nakshatra} ({isHindi ? "चरण" : "P"}{c.pada})
              </div>

              <div className="grid grid-cols-4 gap-1 text-[10px] text-center border-t border-slate-800 pt-1.5">
                <div className="rounded bg-slate-950 p-1">
                  <span className="text-slate-400 block">RL</span>
                  <span className="font-bold text-amber-300">{isHindi ? c.rl_hi : c.rl}</span>
                </div>
                <div className="rounded bg-slate-950 p-1">
                  <span className="text-slate-400 block">NL</span>
                  <span className="font-bold text-amber-300">{isHindi ? c.nl_hi : c.nl}</span>
                </div>
                <div className="rounded bg-slate-950 p-1">
                  <span className="text-slate-400 block">SL</span>
                  <span className="font-bold text-emerald-400">{isHindi ? c.sl_hi : c.sl}</span>
                </div>
                <div className="rounded bg-slate-950 p-1">
                  <span className="text-slate-400 block">SSL</span>
                  <span className="font-bold text-emerald-400">{isHindi ? c.ssl_hi : c.ssl}</span>
                </div>
              </div>

              {c.occupants.length > 0 && (
                <div className="pt-1 border-t border-slate-800/80">
                  <span className="text-[10px] text-slate-400 block mb-1">
                    {isHindi ? "चलित ग्रह:" : "Chalit Planets:"}
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {c.occupants.map((p, idx) => (
                      <span
                        key={idx}
                        className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                          p.is_benefic ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
                        }`}
                      >
                        {isHindi ? p.planet_hi : p.planet}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Selected Cusp Detail Card */}
      {activeCuspData && (
        <div className="rounded-2xl border border-amber-500/30 bg-amber-950/15 p-3.5 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-bold text-amber-300">
              {isHindi
                ? `भाव ${activeCuspData.cusp_number} कस्प एवं संधि विस्तार`
                : `House ${activeCuspData.cusp_number} Cusp & Sandhi Span`}
            </span>
            <span className="text-[11px] text-slate-400">
              {isHindi ? "संधि प्रारंभ से अंत:" : "Span:"} {activeCuspData.sandhi_start_dms} → {activeCuspData.sandhi_end_dms}
            </span>
          </div>
          <p className="text-slate-200 text-[11px] leading-relaxed">
            {isHindi
              ? `भाव ${activeCuspData.cusp_number} का कस्प बिंदु ${activeCuspData.rashi_hi} राशि में ${activeCuspData.dms} पर है। नक्षत्र स्वामी ${activeCuspData.nl_hi} और उप-स्वामी (Sub Lord) ${activeCuspData.sl_hi} हैं, जो इस भाव के फल निर्धारण में निर्णायक भूमिका निभाते हैं।`
              : `House ${activeCuspData.cusp_number} cusp falls in ${activeCuspData.rashi} at ${activeCuspData.dms}. Nakshatra Lord is ${activeCuspData.nl} and Sub Lord is ${activeCuspData.sl}, serving as the primary significator for events governed by this house.`}
          </p>
        </div>
      )}
    </div>
  );
}
