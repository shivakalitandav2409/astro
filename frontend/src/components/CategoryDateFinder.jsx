import React, { useEffect, useState } from "react";
import { AlertTriangle, Calendar, CheckCircle, Filter, Search, Sparkles } from "lucide-react";
import { apiFetch } from "../api";
import SpeechButton from "./SpeechButton";

export default function CategoryDateFinder({ memberId, guestData, isHindi = true }) {
  const [category, setCategory] = useState("marriage");
  const [daysAhead, setDaysAhead] = useState(60);
  const [filterType, setFilterType] = useState("all"); // "all" | "shubh" | "varjit"
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  const categories = [
    { id: "marriage", label_hi: "💍 विवाह व सगाई", label_en: "💍 Marriage & Betrothal" },
    { id: "business", label_hi: "🏢 नवीन व्यापार व दुकान", label_en: "🏢 New Business / Shop" },
    { id: "property", label_hi: "🏡 भूमि/मकान रजिस्ट्री व गृह प्रवेश", label_en: "🏡 Property Registry / Griha Pravesh" },
    { id: "vehicle", label_hi: "🚗 वाहन क्रय (कार/बाइक)", label_en: "🚗 Vehicle Purchase (Car/Bike)" },
    { id: "surgery", label_hi: "🩺 ऑपरेशन व चिकित्सा प्रक्रिया", label_en: "🩺 Medical Surgery / Procedures" },
  ];

  async function fetchDates() {
    setLoading(true);
    try {
      const payload = memberId
        ? { member_id: memberId, category, days_ahead: daysAhead }
        : {
            dob: guestData?.dob || "1995-08-15",
            birth_time: guestData?.birth_time || "09:30",
            latitude: guestData?.latitude || 28.6139,
            longitude: guestData?.longitude || 77.2090,
            tz_offset: guestData?.tz_offset || 5.5,
            category,
            days_ahead: daysAhead,
          };
      const res = await apiFetch("/kundli/category-dates", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setData(res);
    } catch (err) {
      console.error("Failed to fetch category dates:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchDates();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category, daysAhead, memberId]);

  const allDates = data
    ? [
        ...(data.shubh_dates || []).map((d) => ({ ...d, is_shubh: true })),
        ...(data.varjit_dates || []).map((d) => ({ ...d, is_shubh: false })),
      ].sort((a, b) => a.date.localeCompare(b.date))
    : [];

  const filteredDates = allDates.filter((item) => {
    if (filterType === "shubh") return item.is_shubh;
    if (filterType === "varjit") return !item.is_shubh;
    return true;
  });

  return (
    <div className="cosmic-card rounded-2xl p-4 sm:p-5 space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/15 text-amber-400">
            <Calendar className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-amber-300">
              {isHindi ? "श्रेणी अनुसार शुभ-अशुभ तारीख खोजक (Auspicious Date Finder)" : "Category Auspicious & Inauspicious Date Finder"}
            </h2>
            <p className="text-[11px] text-slate-400">
              {isHindi
                ? "चंद्र गोचर, तिथि शुद्धि एवं रिक्ता तिथि परिहार के आधार पर अनुकूल व वर्जित तिथियां"
                : "Personalized auspicious and caution dates based on lunar transit & tithi purity"}
            </p>
          </div>
        </div>

        {/* Days range selector */}
        <div className="flex items-center gap-1.5 text-xs">
          <span className="text-slate-400 text-[11px]">{isHindi ? "अवधि:" : "Span:"}</span>
          {[30, 60, 90].map((days) => (
            <button
              key={days}
              type="button"
              onClick={() => setDaysAhead(days)}
              className={`rounded-lg px-2.5 py-1 font-semibold transition ${
                daysAhead === days
                  ? "bg-amber-500 text-slate-950 font-bold"
                  : "border border-slate-800 bg-slate-900 text-slate-400 hover:text-white"
              }`}
            >
              {days} {isHindi ? "दिन" : "Days"}
            </button>
          ))}
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap gap-1.5">
        {categories.map((cat) => (
          <button
            key={cat.id}
            type="button"
            onClick={() => setCategory(cat.id)}
            className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition ${
              category === cat.id
                ? "bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold shadow-md"
                : "border border-slate-800 bg-slate-900/80 text-slate-300 hover:text-white"
            }`}
          >
            {isHindi ? cat.label_hi : cat.label_en}
          </button>
        ))}
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs border-y border-slate-800/80 py-2">
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => setFilterType("all")}
            className={`rounded-lg px-2.5 py-1 font-semibold transition ${
              filterType === "all" ? "bg-slate-800 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            {isHindi ? `सभी तिथियां (${allDates.length})` : `All Dates (${allDates.length})`}
          </button>
          <button
            type="button"
            onClick={() => setFilterType("shubh")}
            className={`rounded-lg px-2.5 py-1 font-semibold transition ${
              filterType === "shubh"
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {isHindi ? `🟢 शुभ तिथियां (${data?.shubh_dates?.length || 0})` : `🟢 Auspicious (${data?.shubh_dates?.length || 0})`}
          </button>
          <button
            type="button"
            onClick={() => setFilterType("varjit")}
            className={`rounded-lg px-2.5 py-1 font-semibold transition ${
              filterType === "varjit"
                ? "bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {isHindi ? `🔴 वर्जित/अशुभ दिन (${data?.varjit_dates?.length || 0})` : `🔴 Inauspicious (${data?.varjit_dates?.length || 0})`}
          </button>
        </div>

        {data && (
          <span className="text-[11px] text-slate-400">
            {data.start_date} → {data.end_date}
          </span>
        )}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="py-6 text-center text-xs text-amber-300 animate-pulse">
          {isHindi ? "सटीक खगोलीय पंचांग एवं गोचर की गणना हो रही है..." : "Computing lunar transits and auspicious timings..."}
        </div>
      )}

      {/* Date Cards Grid */}
      {!loading && filteredDates.length === 0 && (
        <div className="py-6 text-center text-xs text-slate-400">
          {isHindi ? "चयनित श्रेणी व अवधि में कोई तिथि नहीं मिली।" : "No dates found for the selected filter."}
        </div>
      )}

      {!loading && filteredDates.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 text-xs">
          {filteredDates.map((d, idx) => (
            <div
              key={idx}
              className={`rounded-2xl border p-3.5 space-y-2 transition ${
                d.is_shubh
                  ? "border-emerald-500/30 bg-emerald-950/15 hover:border-emerald-400"
                  : "border-rose-500/30 bg-rose-950/15 hover:border-rose-400"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">
                  {d.date} ({isHindi ? d.weekday_hi || d.weekday : d.weekday})
                </span>
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                    d.is_shubh
                      ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                      : "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                  }`}
                >
                  {d.is_shubh ? (isHindi ? "शुभ मुहूर्त" : "Auspicious") : isHindi ? "वर्जित / टालें" : "Inauspicious"}
                </span>
              </div>

              <div className="text-[11px] text-slate-300 flex items-center justify-between">
                <span>
                  {isHindi ? `तिथि: ${d.tithi_hi || d.tithi}` : `Tithi: ${d.tithi}`}
                </span>
                <span className="text-amber-300">
                  {isHindi ? `चंद्रमा भाव: ${d.house_from_moon}` : `Moon H: ${d.house_from_moon}`}
                </span>
              </div>

              <p className="text-slate-200 text-[11px] leading-relaxed">
                {isHindi ? d.reason_hi || d.reason : d.reason}
              </p>

              <div className="flex items-center justify-between pt-1 border-t border-slate-800/80 text-[10px] text-slate-400">
                <span>{isHindi ? d.transit_rashi_hi : d.transit_rashi_en}</span>
                <SpeechButton
                  text={`${d.date} ${isHindi ? d.weekday_hi : d.weekday}. ${d.is_shubh ? "शुभ मुहूर्त" : "वर्जित दिन"}. ${isHindi ? d.reason_hi : d.reason}`}
                  lang={isHindi ? "hi" : "en"}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
