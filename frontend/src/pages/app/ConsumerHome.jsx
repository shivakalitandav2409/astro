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
  const { account, activeMember, lang, openUpgradeModal, showToast } = useApp();
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
    if (activeMember && activeMember.plan_id === 0 && upsellShownForId !== activeMember.id) {
      setUpsellShownForId(activeMember.id);
      const key = `upsell_seen_${activeMember.id}`;
      if (!sessionStorage.getItem(key)) {
        sessionStorage.setItem(key, "1");
        openUpgradeModal(
          `${activeMember.name} is currently on the Free Plan. Upgrade to unlock Past/Future Dashas, Remedies (Upay) & Horoscope Categories.`,
          activeMember.id
        );
      }
    }
  }, [activeMember, upsellShownForId, openUpgradeModal]);

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
    if (!account || !activeMember) {
      showToast("Sign in (or click Demo Login) to analyze a profile.", "info");
      return;
    }
    const isUnlocked = activeMember.plan_id !== 0 || account.reg_plan_id >= 2;
    if (!isUnlocked) {
      openUpgradeModal(`'${cat.title}' predictions require an active Membership Plan for ${activeMember.name}.`);
      return;
    }
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

  const isFree = !activeMember || (activeMember.plan_id === 0 && (account?.reg_plan_id || 0) < 2);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 space-y-8 animate-fade-up">
      {activeMember && isFree && (
        <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-amber-500/40 bg-gradient-to-r from-amber-500/15 via-slate-900 to-orange-500/15 p-4">
          <div>
            <div className="flex items-center gap-2 text-sm font-bold text-amber-300">
              <Crown className="h-4 w-4 animate-float" />
              <span>{activeMember.name} · Free Tier (PlanId = 0)</span>
            </div>
            <p className="mt-1 text-xs text-slate-300">
              Upgrade this profile for full Dashas &amp; Upay remedies, or switch profiles at the top bar to compare Free vs Premium.
            </p>
          </div>
          <button
            type="button"
            onClick={() => openUpgradeModal("Unlock Remedies (Upay), Past/Future Dashas & all Horoscope Categories.")}
            className="gold-btn rounded-xl px-4 py-2 text-xs"
          >
            Upgrade Plan (₹499+)
          </button>
        </div>
      )}

      {/* Hero + Quick Search */}
      <div className="cosmic-card relative overflow-hidden rounded-3xl p-6 md:p-8 grid gap-6 md:grid-cols-2 items-center">
        <div className="space-y-3">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-300">
            <Sparkles className="h-3.5 w-3.5" /> Swiss Ephemeris Lahiri Engine
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            {lang === "En" ? "Your Cosmic Blueprint & Remedies" : "आपकी वैदिक एवं लाल किताब कुंडली"}
          </h1>
          <p className="text-sm text-slate-300">
            Enter anyone’s Name, DOB, Time &amp; City to generate live charts, or manage saved family members cleanly.
          </p>
          <div className="pt-2 flex flex-wrap gap-2.5">
            <Link to="/app/kundli" className="gold-btn rounded-xl px-4 py-2.5 text-xs">
              Open Kundli &amp; Custom Chart
            </Link>
            <Link to="/app/profiles" className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:border-amber-400">
              <UserPlus className="h-3.5 w-3.5 text-amber-400" /> Add Person Profile
            </Link>
            <Link to="/app/matchmaking" className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:border-amber-400">
              36-Point Match
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
              placeholder="Search Remedies, Yantras, Lal Kitab Books, Mantras..."
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
              <div className="font-bold text-amber-300">Dashas &amp; Varshphal</div>
              <div className="text-slate-400 mt-0.5">Mahadasha, Antardasha &amp; 35-Yr Lal Kitab</div>
            </Link>
            <Link to="/app/panchang" className="cosmic-hover rounded-2xl border border-slate-800 bg-slate-900/70 p-3.5 transition">
              <div className="font-bold text-emerald-300">Choghadiya Panchang</div>
              <div className="text-slate-400 mt-0.5">Live Sunrise/Sunset Muhurat for any city</div>
            </Link>
          </div>
        </div>
      </div>

      {/* Horoscope Categories Grid */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Horoscope Consultations &amp; Life Categories</h2>
            <p className="text-xs text-slate-400">Marriage, Child, Matchmaking, Foreign Travel, Property, Career, Health &amp; Wealth.</p>
          </div>
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${isFree ? "bg-rose-500/15 text-rose-300" : "bg-emerald-500/15 text-emerald-300"}`}>
            {isFree ? "Free Profile: Categories Locked" : "Premium Unlocked"}
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
                {isFree ? (
                  <span className="flex items-center gap-1 rounded-full bg-rose-500/15 px-2 py-0.5 text-[10px] font-semibold text-rose-300">
                    <Lock className="h-3 w-3" /> Lock
                  </span>
                ) : (
                  <span className="flex items-center gap-1 rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] font-semibold text-emerald-300">
                    <Unlock className="h-3 w-3" /> Open
                  </span>
                )}
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
