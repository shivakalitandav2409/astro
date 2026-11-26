import React from "react";
import { Link } from "react-router-dom";
import { Award, BookOpen, Cpu, FileCheck, Layers, ShieldCheck } from "lucide-react";

export default function ProductServicesPage() {
  const modules = [
    { icon: Cpu, title: "Swiss Ephemeris Lahiri Engine", desc: "High-precision sidereal planetary longitudes, retrograde status, Nakshatra/Pada, and sunrise/sunset Choghadiya." },
    { icon: Layers, title: "Lal Kitab & Vashist Fixed Charts", desc: "Automatic Pakka Ghar analysis, 35-year Saturn-to-Mercury cycle, Varshphal age rotations, and custom Upay prescriptions." },
    { icon: FileCheck, title: "Unlimited Platinum Kundali PDFs", desc: "Generate multi-page printable horoscopes for consultations (Platinum tier unlocks unlimited downloads)." },
    { icon: ShieldCheck, title: "Dual-System License Enforcement", desc: "Gold supports 1 active session at a time; Platinum unlocks 2 concurrent systems for assistant + Acharya workflows." },
    { icon: BookOpen, title: "Prarambhik Vashistha Jyotish", desc: "14 structured video lectures (90-day access) + Lal Kitab Amrit Part 1 hardbound companion textbook." },
    { icon: Award, title: "Unified Consumer + Acharya Sync", desc: "Remedies, Puja recommendations, and saved predictions sync seamlessly with the AstroScience Consumer App." },
  ];

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 space-y-8 text-xs">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white">Acharya Software Suite & Services</h1>
        <p className="text-slate-400">Comprehensive digital toolkit built by Deep TechnoServices LLP for Vashist Jyotish practitioners.</p>
      </div>
      <div className="grid gap-5 md:grid-cols-3">
        {modules.map((m) => (
          <div key={m.title} className="cosmic-card rounded-2xl p-5 space-y-2.5">
            <m.icon className="h-6 w-6 text-amber-400" />
            <h2 className="text-base font-bold text-white">{m.title}</h2>
            <p className="text-slate-300 leading-relaxed">{m.desc}</p>
          </div>
        ))}
      </div>
      <div className="flex justify-center gap-3">
        <Link to="/registration" className="gold-btn rounded-xl px-5 py-2.5">Compare Gold & Platinum</Link>
        <Link to="/app/kundli" className="rounded-xl border border-slate-700 px-5 py-2.5 text-white hover:border-amber-400">Open Live Chart Workbench</Link>
      </div>
    </div>
  );
}
