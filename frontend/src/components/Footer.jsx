import React from "react";
import { Link } from "react-router-dom";
import { Mail, MapPin, Phone, Volume2, X } from "lucide-react";
import { useApp } from "../context/AppContext";

export default function Footer() {
  const { playingAudio, setPlayingAudio } = useApp();

  return (
    <>
      {playingAudio && (
        <div className="fixed bottom-4 left-4 z-50 flex items-center gap-3 rounded-2xl border border-amber-500/40 bg-slate-900/95 px-4 py-3 shadow-2xl backdrop-blur">
          <Volume2 className="h-5 w-5 text-amber-400 animate-pulse" />
          <div>
            <div className="text-xs font-bold text-amber-300">{playingAudio.title}</div>
            <audio controls autoPlay src={playingAudio.url} className="mt-1 h-7 w-52" />
          </div>
          <button
            type="button"
            onClick={() => setPlayingAudio(null)}
            className="rounded-lg p-1 text-slate-400 hover:text-white"
            aria-label="Close Audio Player"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      <footer className="mt-16 border-t border-slate-800 bg-slate-950/90 py-10 text-xs text-slate-400">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 md:grid-cols-4">
          <div>
            <div className="flex items-center gap-2">
              <img src="/astro-emblem.png" alt="ASTRO Logo" className="h-7 w-7 rounded-full ring-1 ring-amber-400/40" />
              <div className="text-sm font-bold text-amber-400">ASTRO · Explore the Cosmos &amp; Destiny</div>
            </div>
            <p className="mt-2 leading-relaxed">
              Unified software combining GDVPanel Acharya Workspace + Courses with AstroScience Vedic & Lal Kitab Horoscope Suite.
            </p>
            <p className="mt-2 flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5 text-amber-400" /> Plot No. C-11/20, Mayapuri, New Delhi</p>
            <p className="mt-1 flex items-center gap-1.5"><Phone className="h-3.5 w-3.5 text-amber-400" /> +91-9266469991 / +91-9821397676</p>
            <p className="mt-1 flex items-center gap-1.5"><Mail className="h-3.5 w-3.5 text-amber-400" /> support@astrounified.local</p>
          </div>
          <div>
            <div className="font-semibold text-slate-200 mb-2">GDVPanel Portal</div>
            <ul className="space-y-1.5">
              <li><Link to="/" className="hover:text-amber-300">Portal Landing</Link></li>
              <li><Link to="/registration" className="hover:text-amber-300">Gold & Platinum Registration</Link></li>
              <li><Link to="/courses-details" className="hover:text-amber-300">Prarambhik Vashistha Jyotish</Link></li>
              <li><Link to="/acharya" className="hover:text-amber-300">Acharya Dashboard & PDFs</Link></li>
              <li><Link to="/crm-agent" className="hover:text-amber-300">CRM Agent Console</Link></li>
              <li><Link to="/guruji-live" className="hover:text-amber-300">Guruji Live Studio</Link></li>
            </ul>
          </div>
          <div>
            <div className="font-semibold text-slate-200 mb-2">AstroScience App</div>
            <ul className="space-y-1.5">
              <li><Link to="/app" className="hover:text-amber-300">Home & Horoscope Categories</Link></li>
              <li><Link to="/app/kundli" className="hover:text-amber-300">Kundli Charts & Vivaran</Link></li>
              <li><Link to="/app/dashas" className="hover:text-amber-300">Mahadasha / Lal Kitab Dasha</Link></li>
              <li><Link to="/app/matchmaking" className="hover:text-amber-300">36-Point Ashtakoot Matchmaking</Link></li>
              <li><Link to="/app/panchang" className="hover:text-amber-300">Choghadiya Panchang (±1 Mo)</Link></li>
              <li><Link to="/app/shop" className="hover:text-amber-300">Remedies, Kits & Free Mantras</Link></li>
            </ul>
          </div>
          <div>
            <div className="font-semibold text-slate-200 mb-2">Policies & Legal</div>
            <ul className="space-y-1.5">
              <li><Link to="/about-us" className="hover:text-amber-300">About Us</Link></li>
              <li><Link to="/contact-us" className="hover:text-amber-300">Contact Us</Link></li>
              <li><Link to="/privacy-policy" className="hover:text-amber-300">Privacy Policy</Link></li>
              <li><Link to="/terms_and_conditions" className="hover:text-amber-300">Terms & Conditions</Link></li>
              <li><Link to="/return_and_refunds" className="hover:text-amber-300">Return & Refunds</Link></li>
              <li><Link to="/shipping_and_delivery" className="hover:text-amber-300">Shipping & Delivery</Link></li>
            </ul>
          </div>
        </div>
        <div className="mx-auto mt-8 max-w-7xl border-t border-slate-800/80 px-4 pt-5 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] text-slate-500">
          <div>© {new Date().getFullYear()} ASTRO · All rights reserved.</div>
          <div>
            Developed by <span className="font-semibold text-amber-400">Shivang Saxena</span>
          </div>
        </div>
      </footer>
    </>
  );
}
