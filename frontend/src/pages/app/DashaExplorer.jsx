import React, { useEffect, useState } from "react";
import { Calendar, Clock, Lock, Sparkles } from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";

export default function DashaExplorer() {
  const { account, activeMember, openUpgradeModal, showToast, lang } = useApp();
  const isHindi = lang === "हिं";
  const [bundle, setBundle] = useState(null);
  const [tab, setTab] = useState("mahadasha"); // mahadasha | antardasha | pratyantardasha | lk_dasha | age_ranges

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
      <div className="flex flex-wrap gap-2 rounded-2xl border border-slate-800 bg-slate-950 p-1.5 text-xs">
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

      <div className="grid gap-3 md:grid-cols-2">
        {rows.map((item, idx) => (
          <div
            key={idx}
            className={`rounded-2xl border p-4 text-xs transition ${
              item.is_current
                ? "border-emerald-400/60 bg-emerald-950/20"
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
            <div className="mt-1.5 flex items-center gap-2 text-slate-400">
              <Calendar className="h-3.5 w-3.5 text-amber-400" />
              <span>
                {item.start_date || item.start_year} → {item.end_date || item.end_year}
                {item.duration_years
                  ? ` (${item.duration_years} ${isHindi ? "वर्ष" : "yrs"})`
                  : item.years
                  ? ` (${item.years} ${isHindi ? "वर्ष" : "yrs"})`
                  : ""}
              </span>
            </div>
            <p className="mt-2 text-slate-300">
              {isHindi ? item.summary_hi || item.summary : item.summary || "Sub-transit period active."}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
