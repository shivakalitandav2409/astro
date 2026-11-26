import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, CheckCircle2, Crown, MessageCircle, Phone, Sparkles } from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";

export default function PortalLanding() {
  const { showToast } = useApp();
  const [plans, setPlans] = useState([]);
  const [popup, setPopup] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [leadForm, setLeadForm] = useState({ name: "", contact: "", study_astro: "Yes", pro_astro: "Yes", city: "" });

  useEffect(() => {
    apiFetch("/plans?scope=portal_reg").then((r) => setPlans(r.plans || [])).catch(() => {});
    apiFetch("/popup").then(setPopup).catch(() => {});
  }, []);

  async function submitLead(e) {
    e.preventDefault();
    try {
      await apiFetch("/visitor", { method: "POST", body: JSON.stringify(leadForm) });
      setLeadForm({ name: "", contact: "", study_astro: "Yes", pro_astro: "Yes", city: "" });
      showToast("Inquiry saved to CRM leads!", "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 space-y-12 animate-fade-up">
      {/* Animated Cosmic Hero */}
      <section className="cosmic-card relative overflow-hidden rounded-3xl p-8 md:p-10 grid gap-8 md:grid-cols-12 items-center">
        {/* Rotating Sacred Mandala Background */}
        <div className="pointer-events-none absolute -right-24 -top-24 h-96 w-96 opacity-20">
          <svg viewBox="0 0 200 200" className="h-full w-full animate-spin-slow">
            <circle cx="100" cy="100" r="92" fill="none" stroke="#fbbf24" strokeWidth="0.8" strokeDasharray="4 4" />
            <circle cx="100" cy="100" r="70" fill="none" stroke="#f59e0b" strokeWidth="0.8" />
            <polygon points="100,12 176,144 24,144" fill="none" stroke="#fbbf24" strokeWidth="0.8" />
            <polygon points="100,188 176,56 24,56" fill="none" stroke="#a78bfa" strokeWidth="0.8" />
          </svg>
        </div>

        <div className="md:col-span-7 relative z-10 space-y-4">
          <div className="flex items-center gap-3">
            <img
              src="/astro-logo-banner.png"
              alt="ASTRO - Explore the Cosmos & Destiny"
              className="h-16 sm:h-20 w-auto rounded-2xl border border-amber-500/25 shadow-xl object-contain bg-[#091224]"
            />
          </div>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/35 bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-300 animate-glow">
            <Crown className="h-3.5 w-3.5" /> GDVPanel Portal &amp; AstroScience Suite
          </span>
          <h1 className="text-3xl md:text-5xl font-extrabold text-white tracking-tight leading-tight">
            Precision Kundli, <span className="text-amber-400">Lal Kitab</span> &amp; Acharya Workstation
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed max-w-xl">
            One simple unified platform: analyze anyone’s birth chart with Swiss Ephemeris accuracy, unlock remedies &amp; Dashas, study 14 Vashistha Jyotish lectures, or manage Acharya PDFs.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link to="/app" className="gold-btn flex items-center gap-1.5 rounded-xl px-5 py-2.5 text-xs">
              Open Kundli App <ArrowRight className="h-4 w-4" />
            </Link>
            <Link to="/registration" className="rounded-xl border border-slate-700 bg-slate-900/90 px-5 py-2.5 text-xs font-semibold text-white hover:border-amber-400">
              Gold &amp; Platinum Plans
            </Link>
            <Link to="/courses-details" className="rounded-xl border border-amber-500/40 bg-amber-500/10 px-5 py-2.5 text-xs font-semibold text-amber-300 hover:bg-amber-500/20">
              Jyotish Course (₹11,000)
            </Link>
          </div>
          {popup?.enabled && (
            <button onClick={() => setShowPopup(true)} className="text-xs text-amber-300/90 hover:text-amber-300 underline">
              View Announcement Popup
            </button>
          )}
        </div>

        {/* Clean Lead Capture Card */}
        <form onSubmit={submitLead} className="md:col-span-5 relative z-10 rounded-2xl border border-slate-800 bg-slate-950/90 p-5 space-y-3 text-xs backdrop-blur">
          <div className="font-bold text-amber-300 text-sm">Request Software Demo or Inquiry</div>
          <input required placeholder="Full Name" value={leadForm.name} onChange={(e) => setLeadForm({ ...leadForm, name: e.target.value })} className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-amber-400 focus:outline-none" />
          <input required placeholder="Phone or Email" value={leadForm.contact} onChange={(e) => setLeadForm({ ...leadForm, contact: e.target.value })} className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-amber-400 focus:outline-none" />
          <input required placeholder="City" value={leadForm.city} onChange={(e) => setLeadForm({ ...leadForm, city: e.target.value })} className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-amber-400 focus:outline-none" />
          <div className="grid grid-cols-2 gap-2">
            <select value={leadForm.study_astro} onChange={(e) => setLeadForm({ ...leadForm, study_astro: e.target.value })} className="rounded-xl border border-slate-700 bg-slate-900 px-2.5 py-2 text-white">
              <option value="Yes">Study Jyotish: Yes</option>
              <option value="No">Study Jyotish: No</option>
            </select>
            <select value={leadForm.pro_astro} onChange={(e) => setLeadForm({ ...leadForm, pro_astro: e.target.value })} className="rounded-xl border border-slate-700 bg-slate-900 px-2.5 py-2 text-white">
              <option value="Yes">Pro Astrologer: Yes</option>
              <option value="No">Pro Astrologer: No</option>
            </select>
          </div>
          <button type="submit" className="gold-btn w-full rounded-xl py-2.5">Submit Inquiry</button>
        </form>
      </section>

      {/* Gold vs Platinum Pricing Matrix */}
      <section className="space-y-4">
        <div className="text-center">
          <h2 className="text-2xl font-extrabold text-white">GDVPanel Registration Plans</h2>
          <p className="text-xs text-slate-400 mt-1">Server-enforced session limits (Gold 1 system vs Platinum 2 systems) &amp; Kundali PDF access.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {plans.map((pl) => (
            <div key={pl.id} className={`cosmic-card cosmic-hover rounded-3xl p-6 space-y-4 ${pl.is_popular ? "border-amber-400/60" : ""}`}>
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-white">{pl.name}</h3>
                {pl.is_popular ? <span className="rounded-full bg-amber-500 px-3 py-0.5 text-[10px] font-bold text-slate-950">MOST POPULAR</span> : null}
              </div>
              <div className="text-3xl font-extrabold text-amber-400">
                ₹{pl.total_price} <span className="text-xs font-normal text-slate-400">(Reg ₹{pl.base_fee} + Rec ₹{pl.recurring_fee} + GST ₹{pl.gst})</span>
              </div>
              <div className="text-xs font-semibold text-sky-300">
                Max Concurrent Logins: {pl.max_systems} System(s)
              </div>
              <ul className="space-y-2 text-xs text-slate-300">
                {pl.benefits.map((b, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
              <Link to={`/registration/${pl.id}`} className="gold-btn block w-full rounded-xl py-2.5 text-center text-xs">
                Choose {pl.name.split(" ")[0]}
              </Link>
            </div>
          ))}
        </div>
      </section>

      <div className="fixed bottom-4 right-4 z-30 flex flex-col gap-2">
        <a href="tel:+919266469991" className="flex items-center gap-1.5 rounded-full bg-slate-900 border border-amber-500/40 px-3.5 py-2 text-xs font-semibold text-amber-300 shadow-lg hover:bg-slate-800">
          <Phone className="h-3.5 w-3.5" /> Helpline
        </a>
        <Link to="/contact-us" className="flex items-center gap-1.5 rounded-full bg-emerald-600 px-3.5 py-2 text-xs font-semibold text-white shadow-lg hover:bg-emerald-500">
          <MessageCircle className="h-3.5 w-3.5" /> Support
        </Link>
      </div>

      {showPopup && popup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm">
          <div className="cosmic-card animate-fade-up max-w-md rounded-2xl p-6 space-y-3 text-center">
            <Sparkles className="mx-auto h-8 w-8 text-amber-400 animate-float" />
            <h3 className="text-lg font-bold text-white">{popup.title}</h3>
            <p className="text-xs text-slate-300">{popup.subtitle}</p>
            <div className="flex justify-center gap-2 pt-2">
              <button onClick={() => setShowPopup(false)} className="rounded-xl border border-slate-700 px-4 py-2 text-xs">Dismiss</button>
              <Link to={popup.cta_route} onClick={() => setShowPopup(false)} className="gold-btn rounded-xl px-4 py-2 text-xs">{popup.cta_text}</Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
