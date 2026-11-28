import React, { useEffect, useState } from "react";
import { AlertCircle, Calendar, CheckCircle2, Moon, Sparkles, Sun, XCircle } from "lucide-react";
import { apiFetch } from "../../api";
import CitySearchInput from "../../components/CitySearchInput";
import { useApp } from "../../context/AppContext";

export default function PanchangPage() {
  const { activeMember, showToast, lang } = useApp();
  const isHindi = lang === "हिं";
  const [targetDate, setTargetDate] = useState(new Date().toISOString().slice(0, 10));
  const [city, setCity] = useState({ place_name: "New Delhi, Delhi", latitude: 28.6139, longitude: 77.2090, tz_offset: 5.5 });
  const [data, setData] = useState(null);

  // Category Dates Finder State
  const [catKey, setCatKey] = useState("marriage");
  const [catDates, setCatDates] = useState(null);
  const [loadingCat, setLoadingCat] = useState(false);

  useEffect(() => {
    const qs = new URLSearchParams({
      target_date: targetDate,
      latitude: String(city.latitude),
      longitude: String(city.longitude),
      tz_offset: String(city.tz_offset),
      place_name: city.place_name,
    });
    apiFetch(`/panchang?${qs.toString()}`)
      .then(setData)
      .catch((e) => showToast(e.message, "error"));
  }, [targetDate, city.latitude, city.longitude, city.tz_offset, city.place_name, showToast]);

  useEffect(() => {
    setLoadingCat(true);
    const payload = activeMember
      ? { member_id: activeMember.id, category: catKey, days_ahead: 60 }
      : { dob: "1995-08-15", birth_time: "09:30", category: catKey, days_ahead: 60 };
    apiFetch("/kundli/category-dates", { method: "POST", body: JSON.stringify(payload) })
      .then(setCatDates)
      .catch(() => {})
      .finally(() => setLoadingCat(false));
  }, [activeMember?.id, catKey]);

  const badge = (nature) =>
    nature === "Shubh"
      ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30"
      : nature === "Neutral"
      ? "bg-amber-500/15 text-amber-300 border-amber-500/30"
      : "bg-rose-500/15 text-rose-300 border-rose-500/30";

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 space-y-6 animate-fade-up">
      <div className="cosmic-card flex flex-wrap items-center justify-between gap-4 rounded-3xl p-5">
        <div>
          <h1 className="text-xl font-extrabold text-white">
            {isHindi ? "चौघड़िया मुहूर्त एवं दैनिक पंचांग" : "Choghadiya Muhurat & Daily Panchang"}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            {isHindi
              ? "स्वीस एफिमेरिस द्वारा गणना: किसी भी शहर के लिए सूर्योदय/सूर्यास्त, चौघड़िया मुहूर्त व राहु काल।"
              : "Exact Swiss Ephemeris sunrise/sunset slots for any city (±1 month calendar window)."}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="w-60">
            <CitySearchInput
              value={city.place_name}
              latitude={city.latitude}
              longitude={city.longitude}
              tzOffset={city.tz_offset}
              onSelect={(c) => {
                if (c.picked) setCity({ place_name: c.place_name, latitude: c.latitude, longitude: c.longitude, tz_offset: c.tz_offset });
              }}
              placeholder={isHindi ? "पंचांग शहर चुनें..." : "Select Panchang city..."}
            />
          </div>
          <input
            type="date"
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
            className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-white"
          />
        </div>
      </div>

      {data && (
        <>
          <div className="grid gap-4 sm:grid-cols-5 text-xs">
            <div className="cosmic-card rounded-2xl p-4">
              <div className="text-slate-400">{isHindi ? "सूर्योदय / सूर्यास्त" : "Sunrise / Sunset"}</div>
              <div className="mt-1 font-bold text-amber-300 text-sm font-mono">{data.sunrise} / {data.sunset}</div>
            </div>
            <div className="cosmic-card rounded-2xl p-4">
              <div className="text-slate-400">{isHindi ? "वार (दिन)" : "Weekday"}</div>
              <div className="mt-1 font-bold text-white text-sm">{isHindi ? data.weekday_hi || data.weekday : data.weekday}</div>
            </div>
            <div className="cosmic-card rounded-2xl p-4">
              <div className="text-slate-400">{isHindi ? "तिथि" : "Tithi"}</div>
              <div className="mt-1 font-bold text-white text-sm">{isHindi ? data.tithi_hi || data.tithi : data.tithi}</div>
            </div>
            <div className="cosmic-card rounded-2xl p-4">
              <div className="text-slate-400">{isHindi ? "चंद्र नक्षत्र" : "Moon Nakshatra"}</div>
              <div className="mt-1 font-bold text-white text-sm">{data.nakshatra}</div>
            </div>
            <div className="cosmic-card rounded-2xl p-4">
              <div className="text-slate-400">{isHindi ? "राहु काल (अशुभ)" : "Rahu Kaal"}</div>
              <div className="mt-1 font-bold text-rose-300 text-sm font-mono">{data.rahu_kaal}</div>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2 text-xs">
            <div className="cosmic-card rounded-2xl p-5 space-y-2.5">
              <div className="flex items-center gap-2 font-bold text-amber-300 text-sm pb-1">
                <Sun className="h-4 w-4" /> {isHindi ? "दिन का चौघड़िया (सूर्योदय से सूर्यास्त)" : "Day Choghadiya (Sunrise → Sunset)"}
              </div>
              {data.day_choghadiya.map((s, i) => (
                <div key={i} className="flex items-center justify-between rounded-xl bg-slate-900/70 px-3.5 py-2.5 transition hover:bg-slate-800/80">
                  <span className="font-semibold text-white">{isHindi ? s.name_hi || s.name : s.name}</span>
                  <span className="font-mono text-slate-300">{s.start} – {s.end}</span>
                  <span className={`rounded border px-2 py-0.5 text-[10px] font-bold ${badge(s.nature)}`}>
                    {isHindi ? s.nature_hi || s.nature : s.nature}
                  </span>
                </div>
              ))}
            </div>

            <div className="cosmic-card rounded-2xl p-5 space-y-2.5">
              <div className="flex items-center gap-2 font-bold text-sky-300 text-sm pb-1">
                <Moon className="h-4 w-4" /> {isHindi ? "रात का चौघड़िया (सूर्यास्त से सूर्योदय)" : "Night Choghadiya (Sunset → Next Sunrise)"}
              </div>
              {data.night_choghadiya.map((s, i) => (
                <div key={i} className="flex items-center justify-between rounded-xl bg-slate-900/70 px-3.5 py-2.5 transition hover:bg-slate-800/80">
                  <span className="font-semibold text-white">{isHindi ? s.name_hi || s.name : s.name}</span>
                  <span className="font-mono text-slate-300">{s.start} – {s.end}</span>
                  <span className={`rounded border px-2 py-0.5 text-[10px] font-bold ${badge(s.nature)}`}>
                    {isHindi ? s.nature_hi || s.nature : s.nature}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Module 5: Category-wise Auspicious & Inauspicious Dates Finder (CategoryDateFindModel) */}
          <div className="cosmic-card rounded-3xl p-5 md:p-6 space-y-5 border border-amber-500/30">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
              <div>
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-amber-400" />
                  <h2 className="text-base font-bold text-white">
                    {isHindi ? "श्रेणी अनुसार शुभ व वर्जित तारीख खोजक" : "Category Auspicious & Inauspicious Dates Finder"}
                  </h2>
                </div>
                <p className="mt-0.5 text-xs text-slate-400">
                  {isHindi
                    ? "कुंडली चंद्र गोचर व शास्त्रीय तिथि नियमों के आधार पर आने वाले 60 दिनों की सबसे शुभ व त्याज्य तारीखें।"
                    : "Personalized lunar transit & tithi scan identifying best muhurats and forbidden days."}
                </p>
              </div>

              {/* Category Pills Selector */}
              <div className="flex flex-wrap gap-1.5 text-xs">
                {[
                  { key: "marriage", label: isHindi ? "विवाह व सगाई" : "Marriage" },
                  { key: "business", label: isHindi ? "व्यापार आरंभ" : "New Business" },
                  { key: "property", label: isHindi ? "मकान/रजिस्ट्री" : "Property / Entry" },
                  { key: "vehicle", label: isHindi ? "वाहन क्रय" : "Vehicle Purchase" },
                  { key: "surgery", label: isHindi ? "सर्जरी/ऑपरेशन" : "Medical / Surgery" },
                ].map((c) => (
                  <button
                    key={c.key}
                    type="button"
                    onClick={() => setCatKey(c.key)}
                    className={`rounded-xl px-3 py-1.5 font-semibold transition ${
                      catKey === c.key
                        ? "bg-amber-500 text-slate-950 font-bold shadow-md"
                        : "border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-700"
                    }`}
                  >
                    {c.label}
                  </button>
                ))}
              </div>
            </div>

            {loadingCat ? (
              <div className="py-8 text-center text-xs text-amber-300 animate-pulse">
                {isHindi ? "आगामी तिथियों व गोचर की गणना हो रही है..." : "Scanning lunar transits and auspicious dates..."}
              </div>
            ) : catDates ? (
              <div className="grid gap-6 md:grid-cols-2 text-xs">
                {/* Auspicious Green Dates */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between pb-1 border-b border-emerald-500/30">
                    <div className="font-bold text-emerald-400 flex items-center gap-1.5 text-sm">
                      <CheckCircle2 className="h-4 w-4" />
                      <span>{isHindi ? "सर्वश्रेष्ठ शुभ तारीखें (Green Dates)" : "Most Auspicious (Green Dates)"}</span>
                    </div>
                    <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[10px] font-bold text-emerald-300">
                      {catDates.total_shubh} {isHindi ? "शुभ दिन" : "Days"}
                    </span>
                  </div>

                  <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                    {catDates.shubh_dates.map((d, idx) => (
                      <div
                        key={idx}
                        className="rounded-xl border border-emerald-500/25 bg-emerald-950/15 p-3 space-y-1 hover:border-emerald-400/50 transition"
                      >
                        <div className="flex items-center justify-between font-bold text-white">
                          <span className="flex items-center gap-2">
                            <Calendar className="h-3.5 w-3.5 text-emerald-400" />
                            <span>{d.date} ({d.weekday})</span>
                          </span>
                          <span className="text-[10px] text-emerald-300 bg-emerald-500/20 px-2 py-0.5 rounded-md">
                            {isHindi ? "उत्तम मुहूर्त" : "Optimal"}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-300">
                          <strong>{isHindi ? "मुहूर्त काल: " : "Window: "}</strong>
                          {d.muhurat_time}
                        </div>
                        <p className="text-[11px] text-emerald-200/90 font-medium">
                          {isHindi ? d.reason_hi : d.reason_en}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Inauspicious Red Dates */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between pb-1 border-b border-rose-500/30">
                    <div className="font-bold text-rose-400 flex items-center gap-1.5 text-sm">
                      <XCircle className="h-4 w-4" />
                      <span>{isHindi ? "वर्जित व त्याज्य तारीखें (Red Dates)" : "Inauspicious / Forbidden (Red Dates)"}</span>
                    </div>
                    <span className="rounded-full bg-rose-500/20 px-2.5 py-0.5 text-[10px] font-bold text-rose-300">
                      {catDates.total_varjit} {isHindi ? "वर्जित दिन" : "Days"}
                    </span>
                  </div>

                  <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                    {catDates.varjit_dates.map((d, idx) => (
                      <div
                        key={idx}
                        className="rounded-xl border border-rose-500/25 bg-rose-950/15 p-3 space-y-1 hover:border-rose-400/50 transition"
                      >
                        <div className="flex items-center justify-between font-bold text-white">
                          <span className="flex items-center gap-2">
                            <Calendar className="h-3.5 w-3.5 text-rose-400" />
                            <span>{d.date} ({d.weekday})</span>
                          </span>
                          <span className="text-[10px] text-rose-300 bg-rose-500/20 px-2 py-0.5 rounded-md">
                            {isHindi ? "त्याज्य / वर्जित" : "Forbidden"}
                          </span>
                        </div>
                        <p className="text-[11px] text-rose-200/90">
                          <strong className="text-rose-300">{isHindi ? "कारण: " : "Reason: "}</strong>
                          {isHindi ? d.reason_hi : d.reason_en}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </>
      )}
    </div>
  );
}
