import React, { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { apiFetch } from "../../api";
import CitySearchInput from "../../components/CitySearchInput";
import { useApp } from "../../context/AppContext";

export default function PanchangPage() {
  const { showToast } = useApp();
  const [targetDate, setTargetDate] = useState(new Date().toISOString().slice(0, 10));
  const [city, setCity] = useState({ place_name: "New Delhi, Delhi", latitude: 28.6139, longitude: 77.2090, tz_offset: 5.5 });
  const [data, setData] = useState(null);

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
          <h1 className="text-xl font-extrabold text-white">Choghadiya Muhurat &amp; Daily Panchang</h1>
          <p className="text-xs text-slate-400 mt-1">
            Exact Swiss Ephemeris sunrise/sunset slots for any city (±1 month calendar window).
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
              placeholder="Select Panchang city..."
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
            <div className="cosmic-card rounded-2xl p-4"><div className="text-slate-400">Sunrise / Sunset</div><div className="mt-1 font-bold text-amber-300 text-sm">{data.sunrise} / {data.sunset}</div></div>
            <div className="cosmic-card rounded-2xl p-4"><div className="text-slate-400">Weekday</div><div className="mt-1 font-bold text-white text-sm">{data.weekday}</div></div>
            <div className="cosmic-card rounded-2xl p-4"><div className="text-slate-400">Tithi</div><div className="mt-1 font-bold text-white text-sm">{data.tithi}</div></div>
            <div className="cosmic-card rounded-2xl p-4"><div className="text-slate-400">Moon Nakshatra</div><div className="mt-1 font-bold text-white text-sm">{data.nakshatra}</div></div>
            <div className="cosmic-card rounded-2xl p-4"><div className="text-slate-400">Rahu Kaal</div><div className="mt-1 font-bold text-rose-300 text-sm">{data.rahu_kaal}</div></div>
          </div>

          <div className="grid gap-6 md:grid-cols-2 text-xs">
            <div className="cosmic-card rounded-2xl p-5 space-y-2.5">
              <div className="flex items-center gap-2 font-bold text-amber-300 text-sm pb-1">
                <Sun className="h-4 w-4" /> Day Choghadiya (Sunrise → Sunset)
              </div>
              {data.day_choghadiya.map((s, i) => (
                <div key={i} className="flex items-center justify-between rounded-xl bg-slate-900/70 px-3.5 py-2.5 transition hover:bg-slate-800/80">
                  <span className="font-semibold text-white">{s.name}</span>
                  <span className="font-mono text-slate-300">{s.start} – {s.end}</span>
                  <span className={`rounded border px-2 py-0.5 text-[10px] font-bold ${badge(s.nature)}`}>{s.nature}</span>
                </div>
              ))}
            </div>

            <div className="cosmic-card rounded-2xl p-5 space-y-2.5">
              <div className="flex items-center gap-2 font-bold text-sky-300 text-sm pb-1">
                <Moon className="h-4 w-4" /> Night Choghadiya (Sunset → Next Sunrise)
              </div>
              {data.night_choghadiya.map((s, i) => (
                <div key={i} className="flex items-center justify-between rounded-xl bg-slate-900/70 px-3.5 py-2.5 transition hover:bg-slate-800/80">
                  <span className="font-semibold text-white">{s.name}</span>
                  <span className="font-mono text-slate-300">{s.start} – {s.end}</span>
                  <span className={`rounded border px-2 py-0.5 text-[10px] font-bold ${badge(s.nature)}`}>{s.nature}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
