import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Baby,
  Compass,
  Crown,
  Heart,
  Lock,
  Search,
  Sparkles,
  Unlock,
  UserPlus,
} from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";

export default function ConsumerHome() {
  const { account, activeMember, lang, openUpgradeModal, demoLogin, showToast } = useApp();
  const [categories, setCategories] = useState([]);
  const [searchQ, setSearchQ] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [upsellShownForId, setUpsellShownForId] = useState(null);
  const [subDialog, setSubDialog] = useState(null);
  const [subStatus, setSubStatus] = useState("Unmarried");
  const navigate = useNavigate();

  useEffect(() => {
    apiFetch("/categories").then((r) => setCategories(r.categories || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (!searchQ.trim()) {
      setSearchResults([]);
      return;
    }
    const t = setTimeout(() => {
      apiFetch(`/products?q=${encodeURIComponent(searchQ)}`)
        .then((r) => setSearchResults(r.products || []))
        .catch(() => {});
    }, 220);
    return () => clearTimeout(t);
  }, [searchQ]);

  async function handleCategoryClick(cat) {
    let currAccount = account;
    let currMember = activeMember;
    if (!currAccount || !currMember) {
      try {
        const res = await demoLogin("consumer@astro.local");
        currAccount = res.account;
        currMember = res.members?.[0] || null;
      } catch {
        showToast("Sign in (or click Demo Login) to analyze a profile.", "info");
        return;
      }
    }
    if (!currMember) return;
    if (cat.id === 44) {
      navigate("/app/matchmaking");
      return;
    }
    if (cat.has_sub_dialog === "marriage") {
      setSubStatus("Unmarried");
      setSubDialog({ cat, reading: null, options: ["Unmarried", "Married", "Seeking Match"] });
      return;
    }
    if (cat.has_sub_dialog === "child") {
      setSubStatus("No");
      setSubDialog({ cat, reading: null, options: ["Yes", "No", "Expecting"] });
      return;
    }
    try {
      const res = await apiFetch(`/kundli/category/${cat.id}`, {
        method: "POST",
        body: JSON.stringify({ member_id: activeMember.id }),
      });
      setSubDialog({ cat, reading: res, options: null });
    } catch (err) {
      if (err.status === 402) openUpgradeModal(err.message);
      else showToast(err.message, "error");
    }
  }

  async function submitSubDialog() {
    if (!subDialog || !activeMember) return;
    try {
      const payload = { member_id: activeMember.id };
      if (subDialog.cat.has_sub_dialog === "marriage") payload.marriage_status = subStatus;
      if (subDialog.cat.has_sub_dialog === "child") payload.child_status = subStatus;
      const res = await apiFetch(`/kundli/category/${subDialog.cat.id}`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setSubDialog((prev) => ({ ...prev, reading: res }));
    } catch (err) {
      if (err.status === 402) {
        setSubDialog(null);
        openUpgradeModal(err.message);
      } else {
        showToast(err.message, "error");
      }
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 space-y-8 animate-fade-up">
      {/* Hero + Quick Search */}
      <div className="cosmic-card relative overflow-hidden rounded-3xl p-6 md:p-8 grid gap-6 md:grid-cols-2 items-center">
        <div className="space-y-3">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-300">
            <Sparkles className="h-3.5 w-3.5" /> Swiss Ephemeris Lahiri Engine
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            {lang === "En" ? "Your Cosmic Blueprint & Full Plan" : "आपकी संपूर्ण वैदिक एवं लाल किताब कुंडली"}
          </h1>
          <p className="text-sm text-slate-300">
            {lang === "En"
              ? "Accurate birth chart analysis, planetary dashas, and verified life remedies — completely unlocked."
              : "सटीक जन्म कुंडली, ग्रह दशाएं और लाल किताब उपाय — सीधे देखें और समझें।"}
          </p>
          <div className="pt-2 flex flex-wrap gap-2.5">
            <Link to="/app/kundli" className="gold-btn rounded-xl px-4 py-2.5 text-xs">
              {lang === "En" ? "Open Full Kundli & Report" : "अपनी पूरी कुंडली खोलें"}
            </Link>
            <Link to="/app/profiles" className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:border-amber-400">
              <UserPlus className="h-3.5 w-3.5 text-amber-400" /> {lang === "En" ? "Saved Profiles" : "सहेजे गए नाम"}
            </Link>
            <Link to="/app/matchmaking" className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:border-amber-400">
              {lang === "En" ? "36-Guna Matchmaking" : "36 गुण मिलान"}
            </Link>
          </div>
        </div>

        <div className="space-y-3">
          <div className="relative">
            <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={searchQ}
              onChange={(e) => setSearchQ(e.target.value)}
              placeholder={lang === "En" ? "Search Remedies, Yantras, Lal Kitab, Mantras..." : "उपाय, यंत्र, मंत्र और लाल किताब खोजें..."}
              className="w-full rounded-xl border border-slate-700 bg-slate-950/90 pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:border-amber-400 focus:outline-none"
            />
          </div>
          {searchResults.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-2 max-h-44 overflow-y-auto space-y-1">
              {searchResults.map((p) => (
                <Link key={p.id} to="/app/shop" className="flex items-center justify-between rounded-lg px-3 py-2 text-xs hover:bg-slate-800">
                  <span className="text-slate-100">{p.title}</span>
                  <span className="font-bold text-amber-400">{p.price === 0 ? "Free Audio" : `₹${p.price}`}</span>
                </Link>
              ))}
            </div>
          )}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <Link to="/app/dashas" className="cosmic-hover rounded-2xl border border-slate-800 bg-slate-900/70 p-3.5 transition">
              <div className="font-bold text-amber-300">{lang === "En" ? "Dashas & Varshphal" : "दशा और वर्षफल"}</div>
              <div className="text-slate-400 mt-0.5">{lang === "En" ? "Mahadasha, Antar & 35-Yr Cycles" : "महादशा, अंतर्दशा एवं 35 साला चक्र"}</div>
            </Link>
            <Link to="/app/panchang" className="cosmic-hover rounded-2xl border border-slate-800 bg-slate-900/70 p-3.5 transition">
              <div className="font-bold text-emerald-300">{lang === "En" ? "Choghadiya Panchang" : "चौघड़िया पंचांग"}</div>
              <div className="text-slate-400 mt-0.5">{lang === "En" ? "Live Sunrise/Sunset Muhurat" : "सटीक सूर्योदय और शुभ मुहूर्त"}</div>
            </Link>
          </div>
        </div>
      </div>

      {/* Horoscope Categories Grid */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">
              {lang === "En" ? "Horoscope Consultations & Life Guidance" : "जीवन के महत्वपूर्ण क्षेत्र एवं परामर्श"}
            </h2>
            <p className="text-xs text-slate-400">
              {lang === "En" ? "Marriage, Career, Health, Wealth, Family & Travel Insights." : "विवाह, करियर, स्वास्थ्य, धन, संतान एवं विदेश यात्रा।"}
            </p>
          </div>
          <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-300 flex items-center gap-1.5">
            <Sparkles className="h-3 w-3" /> {lang === "En" ? "Direct Access" : "पूर्ण विश्लेषण उपलब्ध"}
          </span>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {categories.map((cat) => (
            <button
              key={cat.id}
              type="button"
              onClick={() => handleCategoryClick(cat)}
              className="cosmic-card cosmic-hover group relative flex flex-col justify-between rounded-2xl p-4 text-left transition"
            >
              <div className="flex items-start justify-between">
                <div className="rounded-xl bg-amber-500/15 p-2 text-amber-400">
                  {cat.id === 3 || cat.id === 44 ? <Heart className="h-5 w-5" /> : cat.id === 5 ? <Baby className="h-5 w-5" /> : <Compass className="h-5 w-5" />}
                </div>
                <span className="flex items-center gap-1 rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] font-semibold text-emerald-300">
                  <Unlock className="h-3 w-3" /> {lang === "En" ? "Open" : "देखें"}
                </span>
              </div>
              <div className="mt-3">
                <div className="text-sm font-bold text-white group-hover:text-amber-300">
                  {lang === "En" ? cat.title : cat.title_hi}
                </div>
                <p className="mt-1 text-xs text-slate-400">{cat.description}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {subDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm">
          <div className="cosmic-card animate-fade-up w-full max-w-lg rounded-2xl p-6 space-y-4">
            <h3 className="text-lg font-bold text-amber-300">{subDialog.cat.title} Consultation</h3>
            {subDialog.options && !subDialog.reading && (
              <div className="space-y-3">
                <p className="text-xs text-slate-300">Select context for personalized planetary analysis:</p>
                <div className="flex flex-wrap gap-2">
                  {subDialog.options.map((opt) => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => setSubStatus(opt)}
                      className={`rounded-xl border px-3 py-1.5 text-xs ${
                        subStatus === opt ? "border-amber-400 bg-amber-500/20 text-amber-200" : "border-slate-700 text-slate-300"
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
                <button type="button" onClick={submitSubDialog} className="gold-btn rounded-xl px-4 py-2 text-xs">
                  Generate Horoscope Reading
                </button>
              </div>
            )}
            {subDialog.reading && (
              <div className="space-y-3 rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4 text-xs">
                <div className="font-bold text-emerald-300">
                  {subDialog.reading.member_name} · {subDialog.reading.ascendant}
                </div>
                {subDialog.reading.context_note && <div className="text-amber-300">{subDialog.reading.context_note}</div>}
                <p className="leading-relaxed text-slate-200">{subDialog.reading.detailed_reading}</p>
              </div>
            )}
            <div className="flex justify-end">
              <button type="button" onClick={() => setSubDialog(null)} className="rounded-xl border border-slate-700 px-4 py-1.5 text-xs text-slate-300">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
