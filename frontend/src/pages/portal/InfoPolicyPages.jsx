import React from "react";
import { Mail, MapPin, Phone, ShieldCheck } from "lucide-react";

const PAGE_COPY = {
  about: {
    title: "About AstroUnified · Gurudev GD Vashist & Deep TechnoServices LLP",
    body: [
      "AstroUnified brings together the professional GDVPanel Acharya software portal and the 44-screen AstroScience mobile horoscope platform into one astronomically accurate web suite.",
      "Powered by authentic Swiss Ephemeris calculations using Chitrapaksha (Lahiri) Ayanamsa alongside traditional Lal Kitab Vashist Jyotish principles, our mission is to make precision Vedic horoscopes, Dashas, Ashtakoot matchmaking, and remedial guidance accessible to Acharyas, students, and families alike.",
      "Architected and developed by Shivang Saxena.",
    ],
  },
  contact: {
    title: "Contact & Support Center",
    body: [
      "Corporate Headquarters: Plot No. C-11/20, Industrial Area Phase-II, Mayapuri, New Delhi - 110064.",
      "Acharya & Software Helpline: +91-9266469991 / +91-9821397676 · Support Email: support@astrounified.local.",
    ],
  },
  privacy: {
    title: "Privacy Policy",
    body: [
      "Birth dates, times, coordinates, and saved consultations are stored strictly for horoscope computation, PDF generation, and remedy fulfillment.",
      "All sandbox demonstration accounts run locally without transmitting credentials or PII to third-party servers.",
    ],
  },
  terms: {
    title: "Terms & Conditions",
    body: [
      "GDVPanel Gold grants 1 simultaneous active workstation session; Platinum grants 2 simultaneous active sessions plus unlimited client Kundali PDF exports.",
      "Consumer AstroScience plans bind per selected family profile; modifying birth chart inputs on an active subscribed profile expires that PlanId upon confirmation.",
    ],
  },
  refunds: {
    title: "Return & Refund Policy",
    body: [
      "Physical remedies, Yantras, and books may be cancelled prior to dispatch from the Order History panel. Digital course enrollments and activated software subscriptions follow institutional 7-day support review.",
    ],
  },
  shipping: {
    title: "Shipping & Delivery",
    body: [
      "Physical energized Yantras and Lal Kitab Amrit books ship pan-India across 28+ postal circles within 3–7 business days with automated PIN-code validation.",
    ],
  },
};

export default function InfoPolicyPages({ pageKey = "about" }) {
  const info = PAGE_COPY[pageKey] || PAGE_COPY.about;
  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <div className="cosmic-card rounded-3xl p-8 space-y-4">
        <div className="flex items-center gap-2 text-amber-400">
          <ShieldCheck className="h-6 w-6" />
          <h1 className="text-2xl font-extrabold text-white">{info.title}</h1>
        </div>
        <div className="space-y-3 text-sm text-slate-300 leading-relaxed">
          {info.body.map((p, i) => (
            <p key={i}>{p}</p>
          ))}
        </div>
        {pageKey === "contact" && (
          <div className="mt-4 grid gap-3 sm:grid-cols-3 text-xs pt-4 border-t border-slate-800">
            <div className="flex items-center gap-2 text-amber-300"><MapPin className="h-4 w-4" /> Mayapuri, New Delhi</div>
            <div className="flex items-center gap-2 text-amber-300"><Phone className="h-4 w-4" /> +91-9266469991</div>
            <div className="flex items-center gap-2 text-amber-300"><Mail className="h-4 w-4" /> support@astrounified.local</div>
          </div>
        )}
      </div>
    </div>
  );
}
