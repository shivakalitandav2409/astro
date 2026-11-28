import React, { useState } from "react";
import { HeartHandshake } from "lucide-react";
import { apiFetch } from "../../api";
import CitySearchInput from "../../components/CitySearchInput";
import { useApp } from "../../context/AppContext";

export default function MatchmakingPage() {
  const { showToast, lang } = useApp();
  const isHindi = lang === "हिं";
  const [form, setForm] = useState({
    boy_name: "Aarav Sharma",
    boy_dob: "1995-08-15",
    boy_time: "09:30",
    boy_place: "New Delhi, Delhi",
    boy_lat: 28.6139,
    boy_lon: 77.2090,
    boy_tz: 5.5,
    girl_name: "Ananya Verma",
    girl_dob: "1997-04-20",
    girl_time: "14:15",
    girl_place: "Mumbai, Maharashtra",
    girl_lat: 19.0760,
    girl_lon: 72.8777,
    girl_tz: 5.5,
  });
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  async function handleMatch(e) {
    e.preventDefault();
    setBusy(true);
    try {
      const res = await apiFetch("/matchmaking", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setResult(res);
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 space-y-6 animate-fade-up">
      <div className="cosmic-card rounded-3xl p-6 md:p-8">
        <div className="flex items-center gap-2.5 text-amber-300">
          <HeartHandshake className="h-6 w-6" />
          <h1 className="text-xl font-extrabold text-white">
            {isHindi ? "अष्टकूट कुंडली मिलान (36 गुण मिलान एवं मांगलिक विचार)" : "Ashtakoot Kundli Matchmaking (36 Gunas + Manglik)"}
          </h1>
        </div>
        <p className="mt-1 text-xs text-slate-400">
          {isHindi
            ? "स्वीस एफिमेरिस द्वारा गणना: वर एवं वधू के जन्म नगर चुनकर सटीक देशांतर एवं समय-क्षेत्र से गुण मिलान प्राप्त करें।"
            : "Search birth cities to lock exact coordinates & UTC timezone, computed live via Swiss Ephemeris."}
        </p>

        <form onSubmit={handleMatch} className="mt-5 grid gap-6 md:grid-cols-2 text-xs">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
            <div className="font-bold text-amber-300">
              {isHindi ? "वर (लड़के) का जन्म विवरण" : "Groom (Boy) Details"}
            </div>
            <input
              required
              value={form.boy_name}
              onChange={(e) => setForm({ ...form, boy_name: e.target.value })}
              placeholder={isHindi ? "वर का नाम" : "Groom Name"}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white"
            />
            <div className="grid grid-cols-2 gap-2">
              <input
                required
                type="date"
                value={form.boy_dob}
                onChange={(e) => setForm({ ...form, boy_dob: e.target.value })}
                className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white"
              />
              <input
                required
                type="time"
                value={form.boy_time}
                onChange={(e) => setForm({ ...form, boy_time: e.target.value })}
                className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white"
              />
            </div>
            <CitySearchInput
              value={form.boy_place}
              latitude={form.boy_lat}
              longitude={form.boy_lon}
              tzOffset={form.boy_tz}
              onSelect={(c) =>
                setForm((p) => ({
                  ...p,
                  boy_place: c.place_name,
                  boy_lat: c.latitude,
                  boy_lon: c.longitude,
                  boy_tz: c.tz_offset,
                }))
              }
              placeholder={isHindi ? "वर का जन्म स्थान..." : "Groom birth city..."}
            />
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
            <div className="font-bold text-rose-300">
              {isHindi ? "वधू (लड़की) का जन्म विवरण" : "Bride (Girl) Details"}
            </div>
            <input
              required
              value={form.girl_name}
              onChange={(e) => setForm({ ...form, girl_name: e.target.value })}
              placeholder={isHindi ? "वधू का नाम" : "Bride Name"}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white"
            />
            <div className="grid grid-cols-2 gap-2">
              <input
                required
                type="date"
                value={form.girl_dob}
                onChange={(e) => setForm({ ...form, girl_dob: e.target.value })}
                className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white"
              />
              <input
                required
                type="time"
                value={form.girl_time}
                onChange={(e) => setForm({ ...form, girl_time: e.target.value })}
                className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white"
              />
            </div>
            <CitySearchInput
              value={form.girl_place}
              latitude={form.girl_lat}
              longitude={form.girl_lon}
              tzOffset={form.girl_tz}
              onSelect={(c) =>
                setForm((p) => ({
                  ...p,
                  girl_place: c.place_name,
                  girl_lat: c.latitude,
                  girl_lon: c.longitude,
                  girl_tz: c.tz_offset,
                }))
              }
              placeholder={isHindi ? "वधू का जन्म स्थान..." : "Bride birth city..."}
            />
          </div>

          <div className="md:col-span-2 flex justify-end">
            <button type="submit" disabled={busy} className="gold-btn rounded-xl px-6 py-2.5 text-xs">
              {busy ? (isHindi ? "गणना हो रही है..." : "Computing...") : isHindi ? "36 गुण मिलान देखें" : "Calculate 36 Guna Milan"}
            </button>
          </div>
        </form>
      </div>

      {result && (
        <div className="cosmic-card animate-fade-up rounded-3xl p-6 space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div className="space-y-1.5">
              <div className="text-3xl font-extrabold text-amber-400">
                {result.total_points} / {result.max_points} {isHindi ? "गुण" : "Gunas"}
              </div>
              <div className="h-2.5 w-64 overflow-hidden rounded-full bg-slate-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-amber-500 to-emerald-400 transition-all duration-700"
                  style={{ width: `${Math.min(100, (result.total_points / 36) * 100)}%` }}
                />
              </div>
              <div className="text-sm font-bold text-white">
                {isHindi ? result.verdict_hi || result.verdict : result.verdict}
              </div>
            </div>
            <div className="text-xs text-right space-y-1">
              <div className="rounded-full bg-amber-500/15 px-3 py-1 font-semibold text-amber-300">
                {isHindi ? result.manglik_summary_hi || result.manglik_summary : result.manglik_summary}
              </div>
              <div className="text-slate-400">
                {result.boy.name}: {result.boy.nakshatra} ({isHindi ? result.boy.moon_rashi_hi || result.boy.moon_rashi : result.boy.moon_rashi}) ·{" "}
                {result.girl.name}: {result.girl.nakshatra} ({isHindi ? result.girl.moon_rashi_hi || result.girl.moon_rashi : result.girl.moon_rashi})
              </div>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 text-xs">
            {result.kootas.map((k) => (
              <div key={k.name} className="cosmic-hover rounded-xl border border-slate-800 bg-slate-900/70 p-3.5 space-y-1.5 transition">
                <div className="flex justify-between font-bold text-white">
                  <span>{isHindi ? k.name_hi || k.name : k.name}</span>
                  <span className="text-amber-300">{k.obtained} / {k.max}</span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                  <div
                    className="h-full rounded-full bg-amber-400 transition-all duration-500"
                    style={{ width: `${(k.obtained / k.max) * 100}%` }}
                  />
                </div>
                <p className="text-slate-400 leading-relaxed">{isHindi ? k.note_hi || k.note : k.note}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
