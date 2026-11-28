import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  Calendar,
  CheckCircle,
  Clock,
  Compass,
  Filter,
  Info,
  Layers,
  Moon,
  Search,
  Sparkles,
  Volume2,
  XCircle,
} from "lucide-react";
import { apiFetch } from "../api";
import SpeechButton from "./SpeechButton";

export default function CategoryDateFinder({ memberId, guestData, isHindi = true }) {
  const [category, setCategory] = useState("marriage");
  const [daysAhead, setDaysAhead] = useState(90); // default 3 months
  const [filterType, setFilterType] = useState("all"); // "all" | "best" | "moderate" | "avoid"
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  const categories = [
    { id: "marriage", icon: "💍", label_hi: "विवाह व सगाई", label_en: "Marriage & Betrothal" },
    { id: "business", icon: "🏢", label_hi: "नवीन व्यापार व दुकान", label_en: "New Business / Shop" },
    { id: "travel", icon: "✈️", label_hi: "विदेश यात्रा व दीर्घ यात्रा", label_en: "Foreign & Long Travel" },
    { id: "property", icon: "🏡", label_hi: "भूमि/मकान रजिस्ट्री व गृह प्रवेश", label_en: "Property & Griha Pravesh" },
    { id: "vehicle", icon: "🚗", label_hi: "वाहन क्रय (कार/बाइक)", label_en: "Vehicle Purchase" },
    { id: "surgery", icon: "🩺", label_hi: "ऑपरेशन व शल्य चिकित्सा", label_en: "Medical Surgery / Treatment" },
    { id: "job", icon: "💼", label_hi: "नौकरी जॉइनिंग व साक्षात्कार", label_en: "Job Joining & Interview" },
    { id: "investment", icon: "🪙", label_hi: "स्वर्ण क्रय व बड़ा निवेश", label_en: "Gold & Financial Investment" },
  ];

  const durationOptions = [
    { days: 30, label_hi: "1 महीना (30 दिन)", label_en: "1 Month (30 Days)" },
    { days: 60, label_hi: "2 महीने (60 दिन)", label_en: "2 Months (60 Days)" },
    { days: 90, label_hi: "3 महीने (90 दिन)", label_en: "3 Months (90 Days)" },
    { days: 180, label_hi: "6 महीने (180 दिन)", label_en: "6 Months (180 Days)" },
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

  // Merge and sort all dates
  const allDates = data
    ? [
        ...(data.shubh_dates || []),
        ...(data.moderate_dates || []),
        ...(data.varjit_dates || []),
      ].sort((a, b) => a.date.localeCompare(b.date))
    : [];

  const filteredDates = allDates.filter((item) => {
    if (filterType === "best") return item.quality === "best";
    if (filterType === "moderate") return item.quality === "moderate";
    if (filterType === "avoid") return item.quality === "avoid";
    return true;
  });

  // Group dates by month
  const groupedByMonth = filteredDates.reduce((acc, item) => {
    const key = isHindi ? item.month_label_hi : item.month_label_en;
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {});

  const currentCategoryObj = categories.find((c) => c.id === category) || categories[0];

  return (
    <div className="cosmic-card rounded-3xl p-5 sm:p-6 space-y-6 border border-amber-500/30">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-500/20 to-amber-700/20 border border-amber-500/30 text-amber-400 text-xl shadow-inner">
            <Calendar className="h-6 w-6 text-amber-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base sm:text-lg font-bold text-white">
                {isHindi ? "श्रेणी अनुसार शुभ-अशुभ तारीख खोजक" : "Category Auspicious & Inauspicious Date Finder"}
              </h2>
              <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-300">
                1 से 6 महीने
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              {isHindi
                ? "चंद्र गोचर, तिथि शुद्धि, नक्षत्र वेध एवं रिक्ता तिथि परिहार पर आधारित अचूक मुहूर्त प्रणाली"
                : "Exact lunar transits, tithi purity, nakshatra & rikta-avoidance algorithm across upcoming months"}
            </p>
          </div>
        </div>

        {/* Duration (Months) Selector */}
        <div className="flex items-center gap-2">
          <span className="text-slate-400 text-xs font-semibold">{isHindi ? "अवधि चुनें:" : "Span:"}</span>
          <div className="flex rounded-xl bg-slate-900/90 p-1 border border-slate-800">
            {durationOptions.map((opt) => (
              <button
                key={opt.days}
                type="button"
                onClick={() => setDaysAhead(opt.days)}
                className={`rounded-lg px-2.5 py-1 text-xs font-bold transition ${
                  daysAhead === opt.days
                    ? "bg-amber-500 text-slate-950 shadow"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {isHindi ? opt.label_hi : opt.label_en}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Category Selection Carousel / Grid */}
      <div className="space-y-2">
        <label className="text-xs font-bold text-amber-300 flex items-center gap-1.5 uppercase tracking-wide">
          <Sparkles className="h-3.5 w-3.5 text-amber-400" />
          {isHindi ? "कार्य की श्रेणी चुनें (Select Purpose):" : "Choose Event Category:"}
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {categories.map((c) => {
            const isActive = category === c.id;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => setCategory(c.id)}
                className={`flex items-center gap-2 rounded-2xl p-3 text-left transition border ${
                  isActive
                    ? "border-amber-500 bg-amber-500/15 text-white font-bold shadow-lg"
                    : "border-slate-800/80 bg-slate-900/60 text-slate-300 hover:border-slate-700 hover:bg-slate-800/40"
                }`}
              >
                <span className="text-xl">{c.icon}</span>
                <div className="truncate">
                  <div className="text-xs leading-tight">{isHindi ? c.label_hi : c.label_en}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Summary KPI Strip */}
      {data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-3">
            <div className="text-slate-400">{isHindi ? "कुल जांची गई तिथियां" : "Total Days Scanned"}</div>
            <div className="mt-1 text-base font-bold text-white font-mono">{data.total_scanned} दिन</div>
            <div className="text-[10px] text-slate-500">{data.start_date} → {data.end_date}</div>
          </div>
          <div className="rounded-2xl border border-emerald-500/30 bg-emerald-950/20 p-3">
            <div className="text-emerald-400 font-semibold">{isHindi ? "🟢 सर्वश्रेष्ठ शुभ दिन" : "🟢 Best Dates"}</div>
            <div className="mt-1 text-base font-bold text-emerald-300 font-mono">{data.total_shubh} दिन</div>
            <div className="text-[10px] text-emerald-400/80">{isHindi ? "विशिष्ट कार्य सिद्धि योग" : "Highly Recommended"}</div>
          </div>
          <div className="rounded-2xl border border-amber-500/30 bg-amber-950/20 p-3">
            <div className="text-amber-400 font-semibold">{isHindi ? "🟡 मध्यम / सामान्य" : "🟡 Moderate"}</div>
            <div className="mt-1 text-base font-bold text-amber-300 font-mono">{data.total_moderate} दिन</div>
            <div className="text-[10px] text-amber-400/80">{isHindi ? "चौघड़िया देखकर करें" : "Acceptable with caution"}</div>
          </div>
          <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-3">
            <div className="text-rose-400 font-semibold">{isHindi ? "🔴 वर्जित / त्याज्य" : "🔴 Forbidden"}</div>
            <div className="mt-1 text-base font-bold text-rose-300 font-mono">{data.total_varjit} दिन</div>
            <div className="text-[10px] text-rose-400/80">{isHindi ? "कार्य आरंभ से बचें" : "Avoid strictly"}</div>
          </div>
        </div>
      )}

      {/* Filter Tabs & Audio Overview */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-y border-slate-800/80 py-2.5">
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <span className="text-slate-400 font-semibold mr-1">{isHindi ? "फ़िल्टर:" : "Filter:"}</span>
          <button
            type="button"
            onClick={() => setFilterType("all")}
            className={`rounded-xl px-3 py-1 font-semibold transition ${
              filterType === "all" ? "bg-slate-800 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            {isHindi ? `सभी तिथियां (${allDates.length})` : `All (${allDates.length})`}
          </button>
          <button
            type="button"
            onClick={() => setFilterType("best")}
            className={`rounded-xl px-3 py-1 font-semibold transition ${
              filterType === "best"
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {isHindi ? `🟢 सर्वश्रेष्ठ शुभ (${data?.total_shubh || 0})` : `🟢 Best (${data?.total_shubh || 0})`}
          </button>
          <button
            type="button"
            onClick={() => setFilterType("moderate")}
            className={`rounded-xl px-3 py-1 font-semibold transition ${
              filterType === "moderate"
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {isHindi ? `🟡 मध्यम (${data?.total_moderate || 0})` : `🟡 Moderate (${data?.total_moderate || 0})`}
          </button>
          <button
            type="button"
            onClick={() => setFilterType("avoid")}
            className={`rounded-xl px-3 py-1 font-semibold transition ${
              filterType === "avoid"
                ? "bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {isHindi ? `🔴 वर्जित/अशुभ (${data?.total_varjit || 0})` : `🔴 Avoid (${data?.total_varjit || 0})`}
          </button>
        </div>

        {data && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-amber-300 hidden sm:inline">
              {isHindi ? "पूरी रिपोर्ट सुनें:" : "Listen to Overview:"}
            </span>
            <SpeechButton
              text={`${isHindi ? currentCategoryObj.label_hi : currentCategoryObj.label_en} के लिए आगामी ${daysAhead} दिनों में ${data.total_shubh} सर्वश्रेष्ठ शुभ दिन, ${data.total_moderate} मध्यम दिन, और ${data.total_varjit} वर्जित दिन पाए गए हैं।`}
              lang={isHindi ? "hi" : "en"}
            />
          </div>
        )}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="py-12 text-center text-xs text-amber-300 animate-pulse space-y-2">
          <div className="flex justify-center">
            <Calendar className="h-8 w-8 text-amber-400 animate-bounce" />
          </div>
          <p>{isHindi ? "स्वीस एफिमेरिस द्वारा आगामी महीनों के चंद्र गोचर व तिथियों की गणना हो रही है..." : "Calculating planetary positions, lunar transits, and muhurats..."}</p>
        </div>
      )}

      {/* No Dates */}
      {!loading && filteredDates.length === 0 && (
        <div className="py-10 text-center text-xs text-slate-400">
          {isHindi ? "चयनित फ़िल्टर के अनुसार कोई तिथि उपलब्ध नहीं है।" : "No dates match the selected filter."}
        </div>
      )}

      {/* Month-Grouped Cards View */}
      {!loading && Object.keys(groupedByMonth).map((monthKey) => (
        <div key={monthKey} className="space-y-3 pt-2">
          <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
            <h3 className="text-sm font-bold text-amber-300 flex items-center gap-2">
              <Calendar className="h-4 w-4 text-amber-400" />
              <span>{monthKey}</span>
            </h3>
            <span className="text-[11px] text-slate-400">
              {groupedByMonth[monthKey].length} {isHindi ? "तिथियां उपलब्ध" : "dates"}
            </span>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 text-xs">
            {groupedByMonth[monthKey].map((d, idx) => {
              const isBest = d.quality === "best";
              const isModerate = d.quality === "moderate";
              const isAvoid = d.quality === "avoid";

              const borderBg = isBest
                ? "border-emerald-500/35 bg-emerald-950/20 hover:border-emerald-400/60"
                : isModerate
                ? "border-amber-500/35 bg-amber-950/20 hover:border-amber-400/60"
                : "border-rose-500/35 bg-rose-950/20 hover:border-rose-400/60";

              const badgeColor = isBest
                ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                : isModerate
                ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                : "bg-rose-500/20 text-rose-300 border-rose-500/40";

              const badgeLabel = isBest
                ? isHindi ? "🟢 सर्वश्रेष्ठ शुभ" : "Optimal Muhurat"
                : isModerate
                ? isHindi ? "🟡 सामान्य / मध्यम" : "Moderate"
                : isHindi ? "🔴 वर्जित / त्याज्य" : "Avoid";

              return (
                <div
                  key={idx}
                  className={`rounded-2xl border p-4 space-y-2.5 transition shadow-sm ${borderBg}`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-sm">
                      {d.date} ({isHindi ? d.weekday_hi : d.weekday})
                    </span>
                    <span className={`rounded-full border px-2.5 py-0.5 text-[10px] font-bold ${badgeColor}`}>
                      {badgeLabel}
                    </span>
                  </div>

                  <div className="text-[11px] text-slate-300 flex items-center justify-between">
                    <span className="truncate max-w-[150px]">
                      {d.tithi}
                    </span>
                    <span className="text-amber-300 font-semibold">
                      {d.nakshatra} नक्षत्र
                    </span>
                  </div>

                  <div className="rounded-xl bg-slate-950/60 p-2 text-[11px] text-slate-300 space-y-1">
                    <div className="flex items-center gap-1.5 text-amber-200">
                      <Clock className="h-3 w-3 text-amber-400" />
                      <span className="font-semibold">{isHindi ? "अनुशंसित समय:" : "Recommended:"}</span>
                      <span>{d.muhurat_time}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-slate-400 text-[10px]">
                      <Moon className="h-3 w-3 text-sky-400" />
                      <span>{isHindi ? `चंद्र गोचर: ${d.transit_rashi_hi} (${d.house_from_moon}वां भाव)` : `Moon Transit: ${d.transit_rashi_en} (H${d.house_from_moon})`}</span>
                    </div>
                  </div>

                  <p className="text-slate-200 text-[11px] leading-relaxed">
                    {isHindi ? d.reason_hi : d.reason_en}
                  </p>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[10px]">
                    <span className="text-slate-400">
                      {isHindi ? currentCategoryObj.label_hi : currentCategoryObj.label_en}
                    </span>
                    <SpeechButton
                      text={`${d.date} ${isHindi ? d.weekday_hi : d.weekday}. ${badgeLabel}. ${d.muhurat_time}. ${isHindi ? d.reason_hi : d.reason_en}`}
                      lang={isHindi ? "hi" : "en"}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
