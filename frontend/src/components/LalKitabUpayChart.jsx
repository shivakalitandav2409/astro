import React, { useState } from "react";
import { createPortal } from "react-dom";
import { AlertCircle, Clock, ShieldCheck, Sparkles, XCircle } from "lucide-react";
import SpeechButton from "./SpeechButton";

export default function LalKitabUpayChart({ visualUpays, isHindi = true }) {
  const [selectedHouse, setSelectedHouse] = useState(null);

  if (!visualUpays || !Array.isArray(visualUpays) || visualUpays.length === 0) {
    return null;
  }

  const activeHouse = selectedHouse
    ? visualUpays.find((u) => u.house === selectedHouse)
    : null;

  return (
    <div className="cosmic-card rounded-2xl p-4 sm:p-5 space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/15 text-amber-400">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-amber-300">
              {isHindi ? "लाल किताब सचित्र उपाय नक्शा (12-House Graphic Upay Chart)" : "Lal Kitab 12-House Graphic Upay Chart"}
            </h2>
            <p className="text-[11px] text-slate-400">
              {isHindi
                ? "12 भावों के निश्चित ठोस लाल किताब उपाय, वस्तुएं, समय एवं आवश्यक सावधानियां"
                : "Authentic 12-house tangible Lal Kitab remedy substances, timings & precautions"}
            </p>
          </div>
        </div>
      </div>

      {/* 12-House Visual Graphic Grid */}
      <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 text-xs">
        {visualUpays.map((item) => (
          <div
            key={item.house}
            onClick={() => setSelectedHouse(item.house)}
            className={`rounded-2xl border p-3.5 space-y-2 cursor-pointer transition hover:scale-[1.02] ${
              item.has_planets
                ? "border-amber-500/50 bg-amber-950/15 shadow-md hover:border-amber-400"
                : "border-slate-800 bg-slate-900/70 hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="rounded-lg bg-amber-500/20 px-2 py-0.5 text-xs font-bold text-amber-300">
                {isHindi ? `भाव ${item.house}` : `House ${item.house}`}
              </span>
              {item.has_planets && (
                <span className="rounded-full bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-300">
                  {item.occupants.length} {isHindi ? "ग्रह स्थित" : "Planets"}
                </span>
              )}
            </div>

            <div className="font-bold text-white text-[13px] leading-snug">
              {isHindi ? item.substance_hi : item.substance_en}
            </div>

            <p className="text-slate-300 text-[11px] line-clamp-2 leading-relaxed">
              {isHindi ? item.rule_hi : item.rule_en}
            </p>

            <div className="flex items-center justify-between pt-1 border-t border-slate-800/80 text-[10px] text-slate-400">
              <span>{isHindi ? item.timing_hi.split(" ")[0] : item.timing_en.split(" ")[0]}</span>
              <span className="text-amber-400 font-semibold">{isHindi ? "विस्तार देखें →" : "View →"}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Detailed Modal on Box Click */}
      {activeHouse &&
        typeof document !== "undefined" &&
        createPortal(
          <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/85 p-3 sm:p-4 backdrop-blur-md animate-fade-up">
            <div className="cosmic-card w-full max-w-lg rounded-3xl p-5 sm:p-6 border border-amber-500/40 shadow-2xl max-h-[82vh] flex flex-col justify-between">
              {/* Sticky Header */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 flex-shrink-0">
                <div className="flex items-center gap-2">
                  <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-amber-500/15 text-amber-400">
                    <Sparkles className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">
                      {isHindi ? activeHouse.title_hi : activeHouse.title_en}
                    </h3>
                    <p className="text-[11px] text-amber-300 font-semibold">
                      {isHindi ? activeHouse.substance_hi : activeHouse.substance_en}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <SpeechButton
                    text={`${isHindi ? activeHouse.title_hi : activeHouse.title_en}. ${isHindi ? activeHouse.substance_hi : activeHouse.substance_en}. ${isHindi ? activeHouse.rule_hi : activeHouse.rule_en}. ${isHindi ? activeHouse.parhez_hi : activeHouse.parhez_en}`}
                    lang={isHindi ? "hi" : "en"}
                  />
                  <button
                    type="button"
                    onClick={() => setSelectedHouse(null)}
                    className="rounded-xl border border-slate-700 bg-slate-900 p-1.5 text-slate-400 hover:text-white transition"
                  >
                    <XCircle className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Scrollable Content Body */}
              <div className="flex-1 overflow-y-auto py-3 space-y-3 pr-1 text-xs">
                {/* Occupants in this house */}
                {activeHouse.occupants && activeHouse.occupants.length > 0 && (
                  <div className="rounded-xl bg-slate-900 p-3 space-y-1.5 border border-slate-800">
                    <span className="text-slate-400 text-[11px] font-semibold block">
                      {isHindi ? "इस भाव में उपस्थित जन्मकालीन ग्रह:" : "Natal planets in this house:"}
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {activeHouse.occupants.map((p, idx) => (
                        <span
                          key={idx}
                          className={`rounded-lg px-2.5 py-1 text-xs font-bold ${
                            p.is_benefic ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
                          }`}
                        >
                          {isHindi ? p.planet_hi : p.planet} ({p.dms})
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Upay Rule */}
                <div className="rounded-xl bg-amber-950/20 border border-amber-500/30 p-3 space-y-1">
                  <span className="text-amber-300 text-xs font-bold block flex items-center gap-1.5">
                    <ShieldCheck className="h-4 w-4 text-amber-400" />
                    {isHindi ? "उपाय करने का सही नियम व विधि" : "Remedy Procedure & Rules"}
                  </span>
                  <p className="text-slate-200 text-xs leading-relaxed">
                    {isHindi ? activeHouse.rule_hi : activeHouse.rule_en}
                  </p>
                </div>

                {/* Timing & Precautions */}
                <div className="grid gap-2 sm:grid-cols-2 text-xs">
                  <div className="rounded-xl bg-slate-900/80 p-2.5 border border-slate-800 space-y-1">
                    <span className="text-slate-400 text-[11px] font-bold flex items-center gap-1">
                      <Clock className="h-3.5 w-3.5 text-emerald-400" />
                      {isHindi ? "शुभ समय (Timing)" : "Prescribed Timing"}
                    </span>
                    <p className="text-slate-200 text-[11px]">
                      {isHindi ? activeHouse.timing_hi : activeHouse.timing_en}
                    </p>
                  </div>

                  <div className="rounded-xl bg-rose-950/20 p-2.5 border border-rose-500/30 space-y-1">
                    <span className="text-rose-300 text-[11px] font-bold flex items-center gap-1">
                      <AlertCircle className="h-3.5 w-3.5 text-rose-400" />
                      {isHindi ? "परहेज व सावधानियां (Don'ts)" : "Strict Prohibitions"}
                    </span>
                    <p className="text-slate-200 text-[11px]">
                      {isHindi ? activeHouse.parhez_hi : activeHouse.parhez_en}
                    </p>
                  </div>
                </div>
              </div>

              {/* Sticky Footer Button */}
              <div className="flex justify-end pt-3 border-t border-slate-800 flex-shrink-0">
                <button
                  type="button"
                  onClick={() => setSelectedHouse(null)}
                  className="gold-btn rounded-xl px-6 py-2 text-xs font-bold shadow-lg"
                >
                  {isHindi ? "समझ लिया (Done)" : "Understood"}
                </button>
              </div>
            </div>
          </div>,
          document.body
        )}
    </div>
  );
}
