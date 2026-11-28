import React, { useEffect, useState } from "react";
import { ArrowRight, Calendar, Clock, Lock, ShieldAlert, Sparkles, XCircle } from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";

export default function DashaExplorer() {
  const { account, activeMember, openUpgradeModal, showToast, lang } = useApp();
  const isHindi = lang === "हिं";
  const [bundle, setBundle] = useState(null);
  const [tab, setTab] = useState("mahadasha"); // mahadasha | antardasha | pratyantardasha | lk_dasha | age_ranges
  const [ageMode, setAgeMode] = useState("all"); // all | child | adult
  const [selectedDashaTile, setSelectedDashaTile] = useState(null);
  const [timelineFilter, setTimelineFilter] = useState("all"); // all | past | future

  useEffect(() => {
    const payload = activeMember
      ? { member_id: activeMember.id }
      : { dob: "1995-08-15", birth_time: "09:30", latitude: 28.6139, longitude: 77.2090 };
    apiFetch("/kundli/bundle", { method: "POST", body: JSON.stringify(payload) })
      .then(setBundle)
      .catch((e) => showToast(e.message, "error"));
  }, [activeMember?.id, activeMember?.plan_id, account?.reg_plan_id, showToast]);

  const rows =
    tab === "mahadasha"
      ? bundle?.dashas?.mahadashas || []
      : tab === "antardasha"
      ? bundle?.dashas?.antardashas || []
      : tab === "pratyantardasha"
      ? bundle?.dashas?.pratyantardashas || []
      : tab === "lk_dasha"
      ? bundle?.dashas?.lk_dashas || []
      : bundle?.age_ranges || [];

  const currMaha = bundle?.dashas?.mahadashas?.find((x) => x.is_current);
  const currAntar = bundle?.dashas?.antardashas?.find((x) => x.is_current);
  const currPraty = bundle?.dashas?.pratyantardashas?.find((x) => x.is_current);
  const currLk = bundle?.dashas?.lk_dashas?.find((x) => x.is_current);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 space-y-6">
      <div className="cosmic-card rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white">
            {isHindi ? "विंशोत्तरी एवं लाल किताब दशा चक्र" : "Vimshottari & Lal Kitab Dasha Timeline"}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            {isHindi
              ? "जन्मकालीन चंद्र स्थिति के आधार पर 120 वर्षीय विंशोत्तरी महादशा, अंतर्दशा, प्रत्यंतर्दशा एवं 35 साला लाल किताब चक्र।"
              : "Complete Mahadasha, Antardasha, Pratyantardasha & 35-Year Lal Kitab planetary cycles computed from natal Moon longitude."}
          </p>
        </div>
      </div>

      {/* Currently Running Summary */}
      {bundle && (
        <div className="grid gap-3 sm:grid-cols-4 text-xs">
          <div className="cosmic-card rounded-xl p-3">
            <div className="text-slate-400">{isHindi ? "वर्तमान महादशा" : "Running Mahadasha"}</div>
            <div className="font-bold text-emerald-300 mt-0.5">
              {currMaha
                ? `${isHindi ? currMaha.planet_hi || currMaha.planet : currMaha.planet} (${isHindi ? "तक" : "till"} ${currMaha.end_date})`
                : "—"}
            </div>
          </div>
          <div className="cosmic-card rounded-xl p-3">
            <div className="text-slate-400">{isHindi ? "वर्तमान अंतर्दशा" : "Running Antardasha"}</div>
            <div className="font-bold text-emerald-300 mt-0.5">
              {currAntar
                ? `${isHindi ? currAntar.maha_planet_hi || currAntar.maha_planet : currAntar.maha_planet}/${isHindi ? currAntar.planet_hi || currAntar.planet : currAntar.planet} (${isHindi ? "तक" : "till"} ${currAntar.end_date})`
                : "—"}
            </div>
          </div>
          <div className="cosmic-card rounded-xl p-3">
            <div className="text-slate-400">{isHindi ? "वर्तमान प्रत्यंतर्दशा" : "Running Pratyantardasha"}</div>
            <div className="font-bold text-emerald-300 mt-0.5">
              {currPraty
                ? `${isHindi ? currPraty.planet_hi || currPraty.planet : currPraty.planet} (${isHindi ? "तक" : "till"} ${currPraty.end_date})`
                : "—"}
            </div>
          </div>
          <div className="cosmic-card rounded-xl p-3">
            <div className="text-slate-400">{isHindi ? "लाल किताब 35 साला चक्र" : "Lal Kitab 35-Yr Chakra"}</div>
            <div className="font-bold text-amber-300 mt-0.5">
              {currLk
                ? `${isHindi ? currLk.planet_hi || currLk.planet : currLk.planet} (${currLk.years} ${isHindi ? "वर्ष" : "y"})`
                : "—"}
            </div>
          </div>
        </div>
      )}

      {/* Tabs matching APK ViewPager */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex flex-wrap gap-1.5 rounded-2xl border border-slate-800 bg-slate-950 p-1.5 text-xs">
          {[
            { id: "mahadasha", label: isHindi ? "महादशा (120 वर्ष)" : "Mahadasha (120 Yrs)" },
            { id: "antardasha", label: isHindi ? "अंतर्दशा" : "Antardasha" },
            { id: "pratyantardasha", label: isHindi ? "प्रत्यंतर्दशा" : "Pratyantardasha" },
            { id: "lk_dasha", label: isHindi ? "लाल किताब 35 साला" : "Lal Kitab 35-Yr Dasha" },
            { id: "age_ranges", label: isHindi ? "वर्षफल आयु चक्र" : "Varshphal Age Cycles" },
          ].map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTab(t.id)}
              className={`rounded-xl px-3.5 py-2 font-semibold transition ${
                tab === t.id ? "bg-amber-500 text-slate-950" : "text-slate-300 hover:bg-slate-900"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Childhood vs Adult Dasha Bifurcation Toggle */}
        {tab === "mahadasha" && (
          <div className="flex items-center gap-1 rounded-2xl border border-slate-800 bg-slate-950 p-1 text-xs">
            <button
              type="button"
              onClick={() => setAgeMode("all")}
              className={`rounded-xl px-2.5 py-1.5 font-semibold transition ${
                ageMode === "all" ? "bg-slate-800 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {isHindi ? "सभी दशाएं" : "All Ages"}
            </button>
            <button
              type="button"
              onClick={() => setAgeMode("child")}
              className={`rounded-xl px-2.5 py-1.5 font-semibold transition ${
                ageMode === "child" ? "bg-indigo-500/30 text-indigo-300 font-bold border border-indigo-500/40" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {isHindi ? "बाल्यावस्था (0-12 वर्ष)" : "Childhood (0-12 Yrs)"}
            </button>
            <button
              type="button"
              onClick={() => setAgeMode("adult")}
              className={`rounded-xl px-2.5 py-1.5 font-semibold transition ${
                ageMode === "adult" ? "bg-amber-500/30 text-amber-300 font-bold border border-amber-500/40" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {isHindi ? "वयस्क (12+ वर्ष)" : "Adult (12+ Yrs)"}
            </button>
          </div>
        )}
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {rows
          .filter((item) => {
            if (tab !== "mahadasha" || ageMode === "all") return true;
            if (ageMode === "child") return item.is_childhood_dasha;
            if (ageMode === "adult") return !item.is_childhood_dasha;
            return true;
          })
          .map((item, idx) => (
            <div
              key={idx}
              className={`rounded-2xl border p-4 text-xs space-y-2.5 transition ${
                item.is_current
                  ? "border-emerald-400/60 bg-emerald-950/20 shadow-lg"
                  : "border-slate-800 bg-slate-900/70"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="font-bold text-sm text-white">
                  {item.maha_planet
                    ? `${isHindi ? item.maha_planet_hi || item.maha_planet : item.maha_planet} / `
                    : ""}
                  {item.antar_planet
                    ? `${isHindi ? item.antar_planet_hi || item.antar_planet : item.antar_planet} / `
                    : ""}
                  {isHindi ? item.planet_hi || item.planet || item.label : item.planet || item.label}
                </div>
                <div className="flex items-center gap-1.5">
                  {item.start_age !== undefined && (
                    <span className="rounded-lg bg-indigo-500/20 px-2 py-0.5 text-[10px] font-bold text-indigo-300">
                      {isHindi ? `आयु: ${item.start_age} से ${item.end_age} वर्ष` : `Age: ${item.start_age}-${item.end_age}`}
                    </span>
                  )}
                  {item.is_current ? (
                    <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[10px] font-bold text-emerald-300">
                      {isHindi ? "वर्तमान सक्रिय" : "RUNNING NOW"}
                    </span>
                  ) : (
                    <span className="rounded-full bg-amber-500/15 px-2 py-0.5 text-[10px] text-amber-300">
                      {isHindi ? "सक्रिय" : "Active"}
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 text-slate-400 text-[11px]">
                <Calendar className="h-3.5 w-3.5 text-amber-400" />
                <span>
                  {item.start_date || item.start_year || item.start} → {item.end_date || item.end_year || item.end}
                  {item.duration_years
                    ? ` (${item.duration_years} ${isHindi ? "वर्ष" : "yrs"})`
                    : item.years
                    ? ` (${item.years} ${isHindi ? "वर्ष" : "yrs"})`
                    : ""}
                </span>
              </div>

              {/* Childhood Bifurcated Prediction */}
              {item.is_childhood_dasha && (ageMode === "all" || ageMode === "child") && item.child_prediction_hi && (
                <div className="rounded-xl bg-indigo-950/25 border border-indigo-500/30 p-2.5 space-y-1">
                  <div className="text-[10px] uppercase font-bold text-indigo-300 flex items-center gap-1">
                    <Sparkles className="h-3 w-3 text-indigo-400" />
                    {isHindi ? "बाल्यावस्था फलकथन (0-12 वर्ष - स्वास्थ्य, विद्या व नजर रक्षा)" : "Childhood Impact (Balarishta, Schooling & Health)"}
                  </div>
                  <p className="text-slate-200 text-[11px] leading-relaxed">
                    {isHindi ? item.child_prediction_hi : item.child_prediction_en}
                  </p>
                  {item.child_upay_hi && (
                    <div className="pt-1 text-[10px] text-amber-300 font-medium">
                      <strong>{isHindi ? "बाल रक्षा उपाय: " : "Child Remedy: "}</strong>
                      {isHindi ? item.child_upay_hi : item.child_upay_en}
                    </div>
                  )}
                </div>
              )}

              {/* Adult Bifurcated Prediction */}
              {(!item.is_childhood_dasha || ageMode === "adult") && item.adult_prediction_hi && (
                <div className="rounded-xl bg-amber-950/15 border border-amber-500/25 p-2.5 space-y-1">
                  <div className="text-[10px] uppercase font-bold text-amber-300 flex items-center gap-1">
                    <Sparkles className="h-3 w-3 text-amber-400" />
                    {isHindi ? "वयस्क फलकथन (आजीविका, दांपत्य व आर्थिक प्रभाव)" : "Adult Life Impact (Career, Marriage & Wealth)"}
                  </div>
                  <p className="text-slate-200 text-[11px] leading-relaxed">
                    {isHindi ? item.adult_prediction_hi : item.adult_prediction_en}
                  </p>
                </div>
              )}

              {/* Default summary fallback */}
              {!item.child_prediction_hi && !item.adult_prediction_hi && (
                <p className="text-slate-300 leading-relaxed">
                  {isHindi ? item.summary_hi || item.summary : item.summary || "Sub-transit period active."}
                </p>
              )}

              {/* Tap for Event Timeline Helper CTA */}
              <div
                onClick={() => setSelectedDashaTile(item)}
                className="mt-2 flex items-center justify-between rounded-xl bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 text-[11px] font-semibold text-amber-300 hover:bg-amber-500/20 transition cursor-pointer"
              >
                <span>{isHindi ? "टाइल पर टैप करें: जीवन घटनाएं व भविष्यवाणियां" : "Tap tile for life events & predictions"}</span>
                <ArrowRight className="h-3.5 w-3.5 text-amber-400" />
              </div>
            </div>
          ))}
      </div>

      {/* Dasha Tile-Tap Linked Event Timeline Modal */}
      {selectedDashaTile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-3 sm:p-4 backdrop-blur-md animate-fade-up overflow-y-auto">
          <div className="cosmic-card w-full max-w-3xl rounded-3xl p-5 sm:p-6 space-y-4 border border-amber-500/40 shadow-2xl max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-amber-500/15 text-amber-400 font-bold text-sm">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>
                      {selectedDashaTile.maha_planet
                        ? `${isHindi ? selectedDashaTile.maha_planet_hi || selectedDashaTile.maha_planet : selectedDashaTile.maha_planet} / `
                        : ""}
                      {selectedDashaTile.antar_planet
                        ? `${isHindi ? selectedDashaTile.antar_planet_hi || selectedDashaTile.antar_planet : selectedDashaTile.antar_planet} / `
                        : ""}
                      {isHindi
                        ? selectedDashaTile.planet_hi || selectedDashaTile.planet || selectedDashaTile.label
                        : selectedDashaTile.planet || selectedDashaTile.label}
                    </span>
                    {selectedDashaTile.is_current && (
                      <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[10px] font-bold text-emerald-300">
                        {isHindi ? "वर्तमान सक्रिय दशा" : "Current Active"}
                      </span>
                    )}
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    {selectedDashaTile.start_date || selectedDashaTile.start_year || selectedDashaTile.start} →{" "}
                    {selectedDashaTile.end_date || selectedDashaTile.end_year || selectedDashaTile.end}{" "}
                    {selectedDashaTile.duration_years
                      ? `(${selectedDashaTile.duration_years} ${isHindi ? "वर्ष" : "years"})`
                      : selectedDashaTile.years
                      ? `(${selectedDashaTile.years} ${isHindi ? "वर्ष" : "years"})`
                      : ""}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelectedDashaTile(null)}
                className="rounded-xl border border-slate-700 bg-slate-900 p-1.5 text-slate-400 hover:text-white transition"
              >
                <XCircle className="h-5 w-5" />
              </button>
            </div>

            {/* In-Modal Dasha Prediction & Remedy Overview */}
            <div className="rounded-2xl border border-amber-500/25 bg-amber-950/15 p-4 space-y-2">
              <div className="text-xs font-bold text-amber-300">
                {isHindi ? "दशा अवधि प्रभाव एवं लाल किताब मार्गदर्शन" : "Dasha Period Influence & Lal Kitab Guidance"}
              </div>
              <p className="text-xs text-slate-200 leading-relaxed">
                {isHindi
                  ? selectedDashaTile.adult_prediction_hi || selectedDashaTile.summary_hi || selectedDashaTile.summary
                  : selectedDashaTile.adult_prediction_en || selectedDashaTile.summary}
              </p>
              {selectedDashaTile.child_upay_hi && (
                <div className="pt-1 text-[11px] text-amber-200">
                  <strong>{isHindi ? "विशिष्ट लाल किताब उपाय: " : "Lal Kitab Upay: "}</strong>
                  <span>{isHindi ? selectedDashaTile.child_upay_hi : selectedDashaTile.child_upay_en}</span>
                </div>
              )}
            </div>

            {/* Filter Buttons for Timeline */}
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div className="text-xs font-bold text-slate-300">
                {isHindi ? "जीवन घटनाक्रम एवं भविष्यवाणियाँ (Timeline):" : "Life Events & Prediction Timeline:"}
              </div>
              <div className="flex items-center gap-1 rounded-xl border border-slate-800 bg-slate-950 p-1 text-xs">
                <button
                  type="button"
                  onClick={() => setTimelineFilter("all")}
                  className={`rounded-lg px-2.5 py-1 font-semibold transition ${
                    timelineFilter === "all" ? "bg-amber-500 text-slate-950" : "text-slate-400 hover:text-white"
                  }`}
                >
                  {isHindi ? "सभी (All)" : "All"}
                </button>
                <button
                  type="button"
                  onClick={() => setTimelineFilter("past")}
                  className={`rounded-lg px-2.5 py-1 font-semibold transition ${
                    timelineFilter === "past" ? "bg-amber-500 text-slate-950" : "text-slate-400 hover:text-white"
                  }`}
                >
                  {isHindi ? "📜 पिछली घटनाएं (Past)" : "Past Verified"}
                </button>
                <button
                  type="button"
                  onClick={() => setTimelineFilter("future")}
                  className={`rounded-lg px-2.5 py-1 font-semibold transition ${
                    timelineFilter === "future" ? "bg-amber-500 text-slate-950" : "text-slate-400 hover:text-white"
                  }`}
                >
                  {isHindi ? "🔮 आगामी भविष्य (Future)" : "Future Predictions"}
                </button>
              </div>
            </div>

            {/* Filtered Life Events List */}
            <div className="space-y-3">
              {(bundle?.life_events || [])
                .filter((ev) => {
                  const curYear = new Date().getFullYear();
                  if (timelineFilter === "past") return ev.type === "Past Verification" || ev.year <= curYear;
                  if (timelineFilter === "future") return ev.type !== "Past Verification" && ev.year > curYear;
                  return true;
                })
                .map((ev, eIdx) => {
                  const isPast = ev.type === "Past Verification";
                  const isCaution = (ev.caution_level || "").toLowerCase().includes("caution") || (ev.caution_level || "").toLowerCase().includes("alert");
                  return (
                    <div
                      key={eIdx}
                      className={`rounded-2xl border p-3.5 text-xs space-y-2 transition ${
                        isCaution
                          ? "border-rose-500/35 bg-rose-950/20"
                          : isPast
                          ? "border-slate-800 bg-slate-900/80"
                          : "border-emerald-500/30 bg-emerald-950/15"
                      }`}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white text-sm">
                            {ev.year} ({isHindi ? `आयु: ${ev.age} वर्ष` : `Age ${ev.age}`})
                          </span>
                          <span className="text-[11px] text-slate-400">
                            {isHindi ? ev.category_hi : ev.category}
                          </span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <span
                            className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                              isPast
                                ? "bg-slate-800 text-slate-300"
                                : "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40"
                            }`}
                          >
                            {isPast
                              ? isHindi ? "सत्यापित भूतकाल" : "Past Verified"
                              : isHindi ? "आगामी सम्भावना" : "Future Window"}
                          </span>
                          <span
                            className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                              isCaution
                                ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                                : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                            }`}
                          >
                            {ev.caution_level}
                          </span>
                        </div>
                      </div>

                      <div className="font-semibold text-amber-200">
                        {isHindi ? ev.headline_hi : ev.headline_en}
                      </div>

                      <p className="text-slate-300 leading-relaxed">
                        {isHindi ? ev.description_hi : ev.description_en}
                      </p>

                      <div className="rounded-xl bg-slate-950/60 p-2 text-slate-200 flex items-start gap-1.5 border border-slate-800/80 text-[11px]">
                        <Sparkles className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                        <div>
                          <strong className="text-amber-300">
                            {isHindi ? "मार्गदर्शन एवं लाल किताब सुरक्षा: " : "Guidance & Protection: "}
                          </strong>
                          <span>{isHindi ? ev.guidance_hi : ev.guidance_en}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setSelectedDashaTile(null)}
                className="gold-btn rounded-xl px-5 py-2 text-xs font-bold"
              >
                {isHindi ? "बंद करें" : "Close"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
